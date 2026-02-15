import { ArrowRight, Loader2 } from 'lucide-react';
import styles from './TicketForm.module.css';

export function TicketForm({ onSubmit, isLoading }) {
    const handleSubmit = (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const text = formData.get('ticketText');
        if (text?.trim()) {
            onSubmit(text);
        }
    };

    return (
        <form className={styles.form} onSubmit={handleSubmit}>
            <div className={styles.inputGroup}>
                <label htmlFor="ticketText" className={styles.label}>
                    Describe your issue
                </label>
                <textarea
                    id="ticketText"
                    name="ticketText"
                    className={styles.textarea}
                    placeholder="e.g., I was charged twice for my subscription this month..."
                    disabled={isLoading}
                    rows={4}
                    required
                />
            </div>

            <button
                type="submit"
                className={styles.submitButton}
                disabled={isLoading}
            >
                {isLoading ? (
                    <>
                        <Loader2 className={styles.spinner} size={20} />
                        Analyzing...
                    </>
                ) : (
                    <>
                        Submit Ticket
                        <ArrowRight size={20} />
                    </>
                )}
            </button>
        </form>
    );
}
