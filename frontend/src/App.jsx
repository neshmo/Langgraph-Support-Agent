import { useState } from 'react';
import { flushSync } from 'react-dom';
import { Bot, Link, Layout, MessageSquare, LogOut } from 'lucide-react';
import { submitTicket, submitFeedback } from './api/client';
import { ChatInterface } from './pages/ChatInterface';
import { ReviewDashboard } from './pages/ReviewDashboard';
import { ResolutionPrompt } from './components/chat/ResolutionPrompt';
import './App.css';

function App() {
  const [view, setView] = useState('chat'); // 'chat' or 'review'

  // Chat State (Lifted to preserve history)
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hi! Please describe the problem you\'re facing, and I\'ll create a support ticket.' }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTicketId, setActiveTicketId] = useState(null); // Track if we are in a ticket flow

  const [streamingTicketId, setStreamingTicketId] = useState(null);

  const handleSendMessage = async (text) => {
    // 1. Add User Message
    const userMsg = { role: 'user', content: text };

    // Clear prompt if exists
    setMessages(prev => {
      const filtered = prev.filter(m => m.role !== 'prompt');
      return [...filtered, userMsg];
    });

    // 2. Validation Checks (if not active ticket)
    if (!activeTicketId) {
      const lowerText = text.toLowerCase().trim();
      const isGreeting = ['hi', 'hello', 'hey', 'greetings'].includes(lowerText.replace(/[!.]/g, ''));
      const isTooShort = text.length < 5;

      if (isGreeting || isTooShort) {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: "Please describe the problem you're facing in detail so I can create a support ticket for you."
        }]);
        return;
      }
    }

    setIsLoading(true);

    // 3. Prepare AI Placeholder
    // specific ID to update this exact message
    const msgId = Date.now();
    const placeholderMsg = {
      id: msgId,
      role: 'assistant',
      content: '', // Start empty for streaming
      isStreaming: true
    };

    setMessages(prev => [...prev, placeholderMsg]);

    // 4. Start Stream
    try {
      // Import lazily or use existing import. Ensure 'streamTicket' is imported.
      const { streamTicket } = await import('./api/client'); // Dynamic import to avoid changing top-level imports yet? No, assume imported at top.

      // Pass activeTicketId for follow-ups so they attach to existing ticket
      await streamTicket(text, activeTicketId, {
        onTicketId: (id) => {
          setActiveTicketId(id);
          setStreamingTicketId(id);
        },
        onChunk: (chunk) => {
          // Use flushSync for immediate React render on each token
          // This bypasses React 18's automatic batching for ChatGPT-style streaming
          flushSync(() => {
            setMessages(prev => prev.map(m => {
              if (m.id === msgId) {
                return { ...m, content: m.content + chunk };
              }
              return m;
            }));
          });
        },
        onComplete: (result) => {
          setIsLoading(false);

          // Finalize message state
          setMessages(prev => prev.map(m => {
            if (m.id === msgId) {
              return {
                ...m,
                isStreaming: false,
                content: result.proposed_solution || result.final_response?.message || m.content,
                metadata: {
                  intent: result.intent,
                  confidence: result.confidence,
                  ticket_id: result.ticket_id || streamingTicketId,
                  needs_human: result.needs_human,
                  status: result.status
                }
              };
            }
            return m;
          }));

          // Handle Logic (Review/Escalation/Prompt)
          handlePostStreamLogic(result);
        },
        onError: (err) => {
          setIsLoading(false);
          setMessages(prev => prev.map(m => {
            if (m.id === msgId) {
              return { ...m, isStreaming: false, content: m.content + "\n\n[Connection Error: Response interrupted]" };
            }
            return m;
          }));
        }
      });

    } catch (err) {
      setIsLoading(false);
      setMessages(prev => [...prev, { role: 'system', content: `Error: ${err.message}` }]);
    }
  };

  const handlePostStreamLogic = (result) => {
    // Skip resolution prompt and escalation for off-topic/dismissed messages
    if (result.status === 'dismissed') {
      return;
    }

    // Use backend-provided flags for escalation decision
    // Only show escalation when backend explicitly indicates human review is needed
    const isEscalated = result.needs_human === true || result.status === 'waiting_human';

    if (isEscalated) {
      const ticketId = result.ticket_id || activeTicketId;
      const sysMsg = {
        role: 'system',
        content: `This ticket has been escalated for human review. Ticket ID: #${ticketId?.slice(0, 8) || 'pending'}. A human agent will review this, but I can still help meanwhile.`
      };
      setMessages(prev => [...prev, sysMsg]);
    }

    // Always show prompt to allow user to confirm or continue
    const promptMsg = {
      role: 'prompt',
      content: (
        <ResolutionPrompt
          onResolve={() => handleResolve(result.ticket_id || activeTicketId)}
          onContinue={handleContinue}
        />
      )
    };
    setMessages(prev => [...prev, promptMsg]);
  };

  const handleResolve = async (ticketId) => {
    // 1. Remove prompt
    setMessages(prev => prev.filter(m => m.role !== 'prompt'));

    // 2. Call feedback API (Optional, but good practice to mark resolved)
    try {
      await submitFeedback({
        ticket_id: ticketId,
        ticket_text: "Resolved by user confirmation",
        final_response: "User confirmed resolution",
        feedback: "positive"
        // Note: Backend might expect specific fields. existing 'submitFeedback' uses this shape.
      });
    } catch (e) {
      console.error("Failed to submit resolution feedback", e);
    }

    // 3. Show System Message
    const sysMsg = {
      role: 'system',
      content: "Ticket Resolved. If you have another issue, please describe it below."
    };
    setMessages(prev => [...prev, sysMsg]);

    // 4. Reset State
    setActiveTicketId(null);
  };

  const handleContinue = () => {
    // Just remove the prompt, user can keep typing
    setMessages(prev => prev.filter(m => m.role !== 'prompt'));
  };

  const Nav = () => (
    <nav className="nav-bar">
      <button
        className={`nav-btn ${view === 'chat' ? 'active' : ''}`}
        onClick={() => setView('chat')}
      >
        <MessageSquare size={18} /> Chat
      </button>
      <button
        className={`nav-btn ${view === 'review' ? 'active' : ''}`}
        onClick={() => setView('review')}
      >
        <Layout size={18} /> Review Queue
      </button>
    </nav>
  );

  return (
    <div className="app-container">
      <header className="header">
        <div className="header-content">
          <h1>AI Support Agent</h1>
          <Nav />
        </div>
      </header>

      <main className="main-content full-height">
        {view === 'chat' ? (
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
          />
        ) : (
          <ReviewDashboard />
        )}
      </main>
    </div>
  );
}

export default App;
