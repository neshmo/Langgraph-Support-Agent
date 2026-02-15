import { CheckCircle, XCircle } from 'lucide-react';
import styles from './ResolutionPrompt.module.css';

export function ResolutionPrompt({ onResolve, onContinue }) {
    return (
        <div className={styles.container}>
            <p className={styles.text}>Did this solve your problem?</p>
            <div className={styles.actions}>
                <button className={styles.resolveBtn} onClick={onResolve}>
                    <CheckCircle size={16} />
                    Yes, it's resolved
                </button>
                <button className={styles.continueBtn} onClick={onContinue}>
                    <XCircle size={16} />
                    No, I need more help
                </button>
            </div>
        </div>
    );
}
