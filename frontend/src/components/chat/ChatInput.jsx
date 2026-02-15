import { useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import styles from './ChatInput.module.css';

export function ChatInput({ onSend, isLoading }) {
    const inputRef = useRef(null);

    // Auto-focus on mount
    useEffect(() => {
        inputRef.current?.focus();
    }, []);

    // Keep focus after sending (optional, but good for power users)
    useEffect(() => {
        if (!isLoading) {
            inputRef.current?.focus();
        }
    }, [isLoading]);

    const handleSubmit = (e) => {
        e.preventDefault();
        const text = inputRef.current.value.trim();

        if (text && !isLoading) {
            onSend(text);
            inputRef.current.value = '';
            // Immediate focus back to input for rapid fire, 
            // though standard is wait for response. 
            // But we want "continuous chat loop".
            inputRef.current.focus();
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    return (
        <form className={styles.container} onSubmit={handleSubmit}>
            <div className={styles.inputWrapper}>
                <textarea
                    ref={inputRef}
                    name="message"
                    className={styles.input}
                    placeholder="Describe the issue you need help with..."
                    autoComplete="off"
                    rows={1}
                    onKeyDown={handleKeyDown}
                    disabled={false} // Allow typing while waiting
                />
                <button type="submit" className={styles.sendBtn} disabled={isLoading}>
                    <Send size={20} />
                </button>
            </div>
            <div className={styles.footer}>
                Powered by AI • Human review available if needed
            </div>
        </form>
    );
}
