import { useRef, useEffect } from 'react';
import { MessageBubble } from './MessageBubble';
import styles from './MessageList.module.css';

export function MessageList({ messages, isLoading }) {
    const bottomRef = useRef(null);

    // Auto-scroll to bottom on new messages
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isLoading]);

    return (
        <div className={styles.list}>
            {messages.length === 0 && (
                <div className={styles.emptyState}>
                    <p className={styles.emptyTitle}>How can I help you today?</p>
                    <p className={styles.emptySubtitle}>Ask me about refunds, account issues, or product details.</p>
                </div>
            )}

            {messages.map((msg, index) => (
                msg.role === 'prompt' ? (
                    <div key={index} style={{ marginBottom: '1.5rem' }}>
                        {msg.content}
                    </div>
                ) : (
                    <MessageBubble key={index} message={msg} />
                )
            ))}

            {isLoading && (
                <div className={styles.typingIndicator}>
                    <span>AI is thinking...</span>
                </div>
            )}

            <div ref={bottomRef} />
        </div>
    );
}
