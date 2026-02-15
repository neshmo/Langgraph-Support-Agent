import { useState, useEffect } from 'react';
import { getTickets, submitFeedback } from '../api/client';
import { TicketList } from '../components/TicketList';
import { ReviewForm } from '../components/ReviewForm';
import { Layout, RefreshCw, AlertCircle } from 'lucide-react';
import styles from './ReviewDashboard.module.css';

export function ReviewDashboard() {
    const [tickets, setTickets] = useState([]);
    const [selectedTicketId, setSelectedTicketId] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchTickets = async () => {
        setLoading(true);
        try {
            const data = await getTickets('waiting_human');
            setTickets(data);
            if (data.length > 0 && !selectedTicketId) {
                // Optionally select first ticket
                // setSelectedTicketId(data[0].ticket_id);
            }
        } catch (err) {
            setError('Failed to load tickets');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTickets();
    }, []);

    const handleResolve = async (payload) => {
        try {
            await submitFeedback(payload);

            // REQUIREMENT: Refetch tickets immediately after resolve
            // We clear local state first to avoid stale data flicker, then fetch fresh
            setTickets([]);
            setSelectedTicketId(null);

            await fetchTickets();
        } catch (err) {
            console.error(err);
            alert("Failed to submit resolution");
        }
    };

    const selectedTicket = tickets.find(t => t.ticket_id === selectedTicketId);

    return (
        <div className={styles.dashboard}>
            <div className={styles.sidebar}>
                <div className={styles.sidebarHeader}>
                    <h2>
                        <Layout size={20} />
                        Human Review
                    </h2>
                    <button onClick={fetchTickets} className={styles.refreshBtn} title="Refresh">
                        <RefreshCw size={16} />
                    </button>
                </div>

                {loading && <p className={styles.loading}>Loading tickets...</p>}
                {error && <p className={styles.error}><AlertCircle size={16} /> {error}</p>}

                {!loading && !error && tickets.length === 0 && (
                    <div className={styles.emptyState}>
                        <p>No tickets pending review.</p>
                        <p className={styles.subtext}>Great job!</p>
                    </div>
                )}

                <TicketList
                    tickets={tickets}
                    selectedId={selectedTicketId}
                    onSelect={setSelectedTicketId}
                />
            </div>

            <div className={styles.main}>
                {selectedTicket ? (
                    <ReviewForm ticket={selectedTicket} onResolve={handleResolve} />
                ) : (
                    <div className={styles.placeholder}>
                        <p>Select a ticket to review</p>
                    </div>
                )}
            </div>
        </div>
    );
}
