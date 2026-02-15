import styles from './TicketList.module.css';
import { StatusBadge } from './StatusBadge';

export function TicketList({ tickets, selectedId, onSelect }) {
    return (
        <ul className={styles.list}>
            {tickets.map(ticket => (
                <li key={ticket.ticket_id}>
                    <button
                        className={`${styles.item} ${ticket.ticket_id === selectedId ? styles.selected : ''}`}
                        onClick={() => onSelect(ticket.ticket_id)}
                    >
                        <div className={styles.header}>
                            <StatusBadge status={ticket.result.status} confidence={ticket.result.confidence} />
                            <span className={styles.timeLocal}>{new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                        </div>
                        <div className={styles.preview}>
                            {ticket.result.intent && <span className={styles.intent}>{ticket.result.intent} • </span>}
                            {ticket.result.ticket_text?.substring(0, 50)}...
                        </div>
                    </button>
                </li>
            ))}
        </ul>
    );
}
