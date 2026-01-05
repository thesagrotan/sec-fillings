import React from 'react';
import { Clock, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import './EnrichmentBadge.css';

interface EnrichmentBadgeProps {
    status?: 'pending' | 'processing' | 'completed' | 'failed';
    size?: 'sm' | 'md';
}

export const EnrichmentBadge: React.FC<EnrichmentBadgeProps> = ({
    status = 'pending',
    size = 'md'
}) => {
    const getStatusConfig = () => {
        switch (status) {
            case 'processing':
                return {
                    icon: <Loader2 size={size === 'sm' ? 12 : 14} className="spin" />,
                    label: 'Processing',
                    className: 'status-processing'
                };
            case 'completed':
                return {
                    icon: <CheckCircle2 size={size === 'sm' ? 12 : 14} />,
                    label: 'AI Enriched',
                    className: 'status-completed'
                };
            case 'failed':
                return {
                    icon: <AlertCircle size={size === 'sm' ? 12 : 14} />,
                    label: 'Failed',
                    className: 'status-failed'
                };
            case 'pending':
            default:
                return {
                    icon: <Clock size={size === 'sm' ? 12 : 14} />,
                    label: 'Pending',
                    className: 'status-pending'
                };
        }
    };

    const config = getStatusConfig();

    return (
        <span className={`enrichment-badge ${config.className} size-${size}`}>
            {config.icon}
            <span className="badge-label">{config.label}</span>
        </span>
    );
};
