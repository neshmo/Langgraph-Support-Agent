import { useState, useEffect } from 'react';
import { Send, CheckCircle, XCircle } from 'lucide-react';
import styles from './ReviewForm.module.css';

export function ReviewForm({ ticket, onResolve }) {
    const defaultResponse = ticket.result.proposed_solution || '';
    const [responseText, setResponseText] = useState(defaultResponse);
    const [feedback, setFeedback] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Reset form when ticket changes
    useEffect(() => {
        setResponseText(ticket.result.proposed_solution || '');
        setFeedback('');
    }, [ticket.ticket_id]);

    const handleAction = async (action) => {
        setIsSubmitting(true);
        // If "Approve", use current text. If "Reject", intent is failed.
        // But for simply closing, we just submit feedback/resolution.

        try {
            await onResolve({
                ticket_id: ticket.ticket_id,
                ticket_text: ticket.result.ticket_text || 'Text unavailable',
                final_response: responseText,
                feedback: feedback || (action === 'approve' ? 'Approved by human' : 'Modified by human')
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.scrollArea}>
                <div className={styles.section}>
                    <h3>Context</h3>
                    <div className={styles.contextBox}>
                        <p className={styles.originalText}>{ticket.result.ticket_text}</p>
                        <div className={styles.meta}>
                            <span>Intent: <strong>{ticket.result.intent}</strong></span>
                            <span>Confidence: <strong>{Math.round(ticket.result.confidence * 100)}%</strong></span>
                        </div>
                    </div>
                </div>

                <div className={styles.section}>
                    <h3>Solution (Editable)</h3>
                    <textarea
                        className={styles.editor}
                        value={responseText}
                        onChange={(e) => setResponseText(e.target.value)}
                        rows={10}
                    />
                </div>

                <div className={styles.section}>
                    <h3>Internal Feedback (Learning)</h3>
                    <textarea
                        className={styles.notes}
                        value={feedback}
                        onChange={(e) => setFeedback(e.target.value)}
                        placeholder="Why did the AI fail? Use this to improve future results."
                        rows={3}
                    />
                </div>
            </div>

            <div className={styles.actions}>
                <button
                    className={styles.btnApprove}
                    onClick={() => handleAction('approve')}
                    disabled={isSubmitting}
                >
                    <CheckCircle size={18} />
                    Approve & Resolve
                </button>
                {/* 
                <button 
                    className={styles.btnFail}
                    onClick={() => handleAction('fail')}
                    disabled={isSubmitting}
                >
                    <XCircle size={18} />
                    Mark as Failed
                </button> 
                */}
            </div>
        </div>
    );
}
