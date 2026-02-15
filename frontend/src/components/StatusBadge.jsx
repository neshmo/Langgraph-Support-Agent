import { CheckCircle, AlertTriangle, XCircle, Clock } from 'lucide-react';
import styles from './StatusBadge.module.css';

// Placeholder for missing Loader import since we use CSS animation separately, 
// using generic AlertTriangle as fallback if status unknown
const Loader = AlertTriangle;

const CONFIG = {
    resolved: {
        icon: CheckCircle,
        label: 'Resolved',
        className: styles.success
    },
    waiting_human: {
        icon: Clock,
        label: 'Escalated',
        className: styles.warning
    },
    failed: {
        icon: XCircle,
        label: 'Failed',
        className: styles.error
    },
    processing: {
        icon: Loader,
        label: 'Processing',
        className: styles.neutral
    }
};

export function StatusBadge({ status, confidence }) {
    const config = CONFIG[status] || CONFIG.processing;
    const Icon = config.icon;

    return (
        <div className={`${styles.badge} ${config.className}`}>
            <Icon size={16} />
            <span>{config.label}</span>
            {typeof confidence === 'number' && (
                <span className={styles.confidence}>
                    {Math.round(confidence * 100)}% Match
                </span>
            )}
        </div>
    );
}
