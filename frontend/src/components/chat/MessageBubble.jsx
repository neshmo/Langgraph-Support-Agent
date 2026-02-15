import { Bot, User, ShieldAlert } from 'lucide-react';
import { StatusBadge } from '../StatusBadge';
import styles from './MessageBubble.module.css';

export function MessageBubble({ message }) {
    const isUser = message.role === 'user';
    const isSystem = message.role === 'system';

    // Check if this is an escalation request (hide intent/confidence)
    const isEscalation = message.metadata?.intent === 'escalate_request';

    if (isSystem) {
        return (
            <div className={styles.systemMessage}>
                <ShieldAlert size={16} className={styles.systemIcon} />
                <span>{message.content}</span>
            </div>
        );
    }

    return (
        <div className={`${styles.row} ${isUser ? styles.userRow : styles.aiRow}`}>
            {!isUser && (
                <div className={styles.avatar}>
                    <img src="/ai-avatar.png" alt="AI Assistant" className={styles.avatarImage} />
                </div>
            )}

            <div className={styles.contentWrapper}>
                <div className={`${styles.bubble} ${isUser ? styles.userBubble : styles.aiBubble}`}>
                    {message.content}
                </div>
            </div>

            {isUser && (
                <div className={`${styles.avatar} ${styles.userAvatar}`}>
                    <User size={20} color="white" />
                </div>
            )}
        </div>
    );
}
