import React, { useState } from 'react';
import type { Company } from '../types';
import { CompanyDetailsModal } from './CompanyDetailsModal';

interface Props {
    companies: Company[];
}

export const CompaniesTable: React.FC<Props> = ({ companies }) => {
    const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);

    if (companies.length === 0) {
        return <div className="text-center p-4 text-gray-400">No newly founded companies found. Try ingesting more data.</div>;
    }

    return (
        <div className="overflow-x-auto">
            <table>
                <thead>
                    <tr>
                        <th>Company</th>
                        <th>Location</th>
                        <th>Industry</th>
                        <th>Revenue</th>
                        <th>Amount Raised</th>
                        <th>Founded</th>
                        <th>Latest Filing</th>
                        <th>Links</th>
                    </tr>
                </thead>
                <tbody>
                    {companies.map((company) => (
                        <tr
                            key={company.id}
                            onClick={() => setSelectedCompany(company)}
                            style={{ cursor: 'pointer' }}
                            title="Click to view details"
                        >
                            <td>
                                <div style={{ fontWeight: 600, color: 'white' }}>{company.name}</div>
                                <div style={{ fontSize: '0.8rem', color: '#888' }}>{company.cik}</div>
                            </td>
                            <td>{company.city !== 'Unknown' ? `${company.city}, ${company.state}` : 'Unknown'}</td>
                            <td>
                                <span style={{
                                    backgroundColor: '#374151',
                                    padding: '0.2rem 0.6rem',
                                    borderRadius: '1rem',
                                    fontSize: '0.85rem'
                                }}>
                                    {company.industry}
                                </span>
                            </td>
                            <td>{company.revenue_range}</td>
                            <td style={{ fontWeight: 'bold' }}>
                                {company.amount_sold && company.amount_sold !== 'Unknown'
                                    ? `$${parseInt(company.amount_sold).toLocaleString()}`
                                    : 'N/A'}
                            </td>
                            <td>{company.founded_year}</td>
                            <td>{company.latest_filing_date}</td>
                            <td>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                                    {company.website_url && (
                                        <a
                                            href={company.website_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            style={{ color: '#60a5fa', textDecoration: 'none', fontSize: '0.9em' }}
                                            onClick={(e) => e.stopPropagation()}
                                        >
                                            Website
                                        </a>
                                    )}
                                    {company.careers_url && (
                                        <a
                                            href={company.careers_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            style={{ color: '#42d392', textDecoration: 'none', fontWeight: 'bold', fontSize: '0.9em' }}
                                            onClick={(e) => e.stopPropagation()}
                                        >
                                            Careers
                                        </a>
                                    )}
                                    {!company.website_url && !company.careers_url && (
                                        <span style={{ color: '#666' }}>-</span>
                                    )}
                                </div>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {selectedCompany && (
                <CompanyDetailsModal
                    company={selectedCompany}
                    onClose={() => setSelectedCompany(null)}
                />
            )}
        </div>
    );
};

