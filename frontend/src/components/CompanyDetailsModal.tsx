import React, { useEffect, useState, useCallback } from 'react';
import type { Company } from '../types';
import { X, Building, MapPin, DollarSign, Calendar, FileText, Globe, Users, TrendingUp, Briefcase } from 'lucide-react';
import './CompanyDetailsModal.css';
import { IntelligenceCard } from './IntelligenceCard';
import { EnrichmentBadge } from './EnrichmentBadge';

interface Props {
    company: Company;
    onClose: () => void;
}

export const CompanyDetailsModal: React.FC<Props> = ({ company, onClose }) => {
    const [isVisible, setIsVisible] = useState(false);

    const handleClose = useCallback(() => {
        setIsVisible(false);
        setTimeout(onClose, 300); // Wait for animation
    }, [onClose]);

    useEffect(() => {
        requestAnimationFrame(() => setIsVisible(true));
        const handleEsc = (e: KeyboardEvent) => {
            if (e.key === 'Escape') handleClose();
        };
        window.addEventListener('keydown', handleEsc);
        return () => window.removeEventListener('keydown', handleEsc);
    }, [handleClose]);

    return (
        <div className={`modal-overlay ${isVisible ? 'visible' : ''}`} onClick={handleClose}>
            <div
                className={`modal-content ${isVisible ? 'visible' : ''}`}
                onClick={e => e.stopPropagation()}
                role="dialog"
                aria-modal="true"
            >
                <div className="modal-header">
                    <div className="modal-title-section">
                        <div className="icon-wrapper">
                            <Building size={24} />
                        </div>
                        <div>
                            <h2>{company.name}</h2>
                            <div className="modal-badges">
                                <span className="cik-badge">CIK: {company.cik}</span>
                                <EnrichmentBadge status={company.enrichment_status} size="sm" />
                            </div>
                        </div>
                    </div>
                    <button onClick={handleClose} className="close-button" aria-label="Close modal">
                        <X size={20} />
                    </button>
                </div>

                <div className="modal-body">
                    <div className="details-grid">
                        <div className="detail-item">
                            <div className="detail-icon"><MapPin size={18} /></div>
                            <div className="detail-content">
                                <span className="label">Location</span>
                                <span className="value">
                                    {company.city !== 'Unknown' ? `${company.city}, ${company.state}` : 'Unknown Location'}
                                </span>
                            </div>
                        </div>

                        <div className="detail-item">
                            <div className="detail-icon"><Briefcase size={18} /></div>
                            <div className="detail-content">
                                <span className="label">Industry</span>
                                <span className="value">{company.industry}</span>
                            </div>
                        </div>

                        <div className="detail-item">
                            <div className="detail-icon"><DollarSign size={18} /></div>
                            <div className="detail-content">
                                <span className="label">Revenue Range</span>
                                <span className="value">{company.revenue_range}</span>
                            </div>
                        </div>

                        <div className="detail-item">
                            <div className="detail-icon"><TrendingUp size={18} /></div>
                            <div className="detail-content">
                                <span className="label">Amount Sold</span>
                                <span className="value accent-text">
                                    {company.amount_sold && company.amount_sold !== 'Unknown'
                                        ? `$${parseInt(company.amount_sold).toLocaleString()}`
                                        : 'N/A'}
                                </span>
                            </div>
                        </div>

                        <div className="detail-item">
                            <div className="detail-icon"><Calendar size={18} /></div>
                            <div className="detail-content">
                                <span className="label">Founded</span>
                                <span className="value">{company.founded_year}</span>
                            </div>
                        </div>

                        <div className="detail-item">
                            <div className="detail-icon"><FileText size={18} /></div>
                            <div className="detail-content">
                                <span className="label">Latest Filing</span>
                                <span className="value">{company.latest_filing_date}</span>
                            </div>
                        </div>
                    </div>

                    <div className="modal-actions">
                        {company.website_url && (
                            <a
                                href={company.website_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="action-button primary"
                            >
                                <Globe size={18} />
                                Visit Website
                            </a>
                        )}
                        {company.careers_url && (
                            <a
                                href={company.careers_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="action-button secondary"
                            >
                                <Users size={18} />
                                View Careers
                            </a>
                        )}
                    </div>

                    <IntelligenceCard company={company} />
                </div>
            </div>
        </div>
    );
};
