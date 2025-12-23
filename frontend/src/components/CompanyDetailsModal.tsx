import React, { useEffect, useRef } from 'react';
import type { Company } from '../types';

interface Props {
    company: Company;
    onClose: () => void;
}

export const CompanyDetailsModal: React.FC<Props> = ({ company, onClose }) => {
    const modalRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (modalRef.current && !modalRef.current.contains(event.target as Node)) {
                onClose();
            }
        };

        const handleEscape = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                onClose();
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        document.addEventListener('keydown', handleEscape);

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
            document.removeEventListener('keydown', handleEscape);
        };
    }, [onClose]);

    return (
        <div className="modal-overlay">
            <div className="modal-content" ref={modalRef}>
                <div className="modal-header">
                    <div className="modal-title">
                        <h2>{company.name}</h2>
                        <span>CIK: {company.cik}</span>
                    </div>
                    <button className="close-button" onClick={onClose}>&times;</button>
                </div>
                <div className="modal-body">
                    <div className="detail-row">
                        <span className="detail-label">Location</span>
                        <span className="detail-value">
                            {company.city !== 'Unknown' ? `${company.city}, ${company.state}` : 'Unknown Location'}
                        </span>
                    </div>
                    <div className="detail-row">
                        <span className="detail-label">Industry</span>
                        <span className="detail-value">{company.industry}</span>
                    </div>
                    <div className="detail-row">
                        <span className="detail-label">Revenue Range</span>
                        <span className="detail-value" style={{ color: '#42d392' }}>{company.revenue_range}</span>
                    </div>
                    <div className="detail-row">
                        <span className="detail-label">Founded</span>
                        <span className="detail-value">{company.founded_year}</span>
                    </div>
                    <div className="detail-row">
                        <span className="detail-label">Jurisdiction</span>
                        <span className="detail-value">{company.jurisdiction}</span>
                    </div>
                    <div className="detail-row">
                        <span className="detail-label">Amount Sold</span>
                        <span className="detail-value" style={{ fontWeight: 'bold' }}>
                            {company.amount_sold && company.amount_sold !== 'Unknown'
                                ? `$${parseInt(company.amount_sold).toLocaleString()}`
                                : 'N/A'}
                        </span>
                    </div>
                    <div className="detail-row">
                        <span className="detail-label">Key Executive</span>
                        <span className="detail-value">
                            {company.executive_name !== 'Unknown'
                                ? `${company.executive_name} (${company.executive_title})`
                                : 'Unknown'}
                        </span>
                    </div>
                    <div className="detail-row">
                        <span className="detail-value">{company.latest_filing_date}</span>
                    </div>
                    {company.website_url && (
                        <div className="detail-row">
                            <span className="detail-label">Website</span>
                            <span className="detail-value">
                                <a
                                    href={company.website_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    style={{ color: '#646cff', textDecoration: 'none' }}
                                >
                                    Visit Website &rarr;
                                </a>
                            </span>
                        </div>
                    )}
                    {company.careers_url && (
                        <div className="detail-row">
                            <span className="detail-label">Careers</span>
                            <span className="detail-value">
                                <a
                                    href={company.careers_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    style={{ color: '#42d392', textDecoration: 'none' }}
                                >
                                    View Careers Page &rarr;
                                </a>
                            </span>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
