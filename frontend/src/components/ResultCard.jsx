// import ReactMarkdown from 'react-markdown'; // Removed to avoid dependency

import { StatusBadge } from './StatusBadge';
import styles from './ResultCard.module.css';

export function ResultCard({ result }) {
    const { status, intent, confidence, proposed_solution, error_message } = result;

    const isError = status === 'failed';
    const isEscalated = status === 'waiting_human';

    return (
        <div className={styles.card}>
            <header className={styles.header}>
                <div className={styles.meta}>
                    <span className={styles.intentLabel}>Detected Intent:</span>
                    <span className={styles.intentValue}>{intent || 'Unknown'}</span>
                </div>
                <StatusBadge status={status} confidence={confidence} />
            </header>

            <div className={styles.content}>
                {isError ? (
                    <div className={styles.errorBox}>
                        <p className={styles.errorTitle}>Processing Error</p>
                        <p>{error_message || 'An unexpected error occurred.'}</p>
                    </div>
                ) : (
                    <>
                        {isEscalated && (
                            <div className={styles.warningBox}>
                                <p><strong>Note:</strong> This ticket has been flagged for human review.</p>
                            </div>
                        )}

                        <div className={styles.solution}>
                            <h3>Proposed Solution</h3>
                            <div className={styles.markdown}>
                                {proposed_solution || 'No solution generated.'}
                            </div>
                        </div>
                    </>
                )}
            </div>

            <footer className={styles.footer}>
                Ticket ID: <span className={styles.ticketId}>{result.ticket_id}</span>
            </footer>
        </div>
    );
}
