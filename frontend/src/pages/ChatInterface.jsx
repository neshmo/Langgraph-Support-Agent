import { ChatInput } from '../components/chat/ChatInput';
import { MessageList } from '../components/chat/MessageList';

export function ChatInterface({ messages, onSendMessage, isLoading }) {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
            <MessageList messages={messages} isLoading={isLoading} />
            <ChatInput onSend={onSendMessage} isLoading={isLoading} />
        </div>
    );
}
