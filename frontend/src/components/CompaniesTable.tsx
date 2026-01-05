import React, { useState, useMemo } from 'react';
import {
    createColumnHelper,
    flexRender,
    getCoreRowModel,
    useReactTable,
} from '@tanstack/react-table';
import type { Company } from '../types';
import { CompanyDetailsModal } from './CompanyDetailsModal';
import { EnrichmentBadge } from './EnrichmentBadge';
import { ExternalLink, Building2, MapPin, DollarSign, Calendar, FileText } from 'lucide-react';
import './CompaniesTable.css';

interface Props {
    companies: Company[];
}

export const CompaniesTable: React.FC<Props> = ({ companies }) => {
    const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);

    const columnHelper = createColumnHelper<Company>();

    const columns = useMemo(() => [
        columnHelper.accessor('name', {
            header: 'Company',
            cell: info => (
                <div className="company-cell">
                    <div className="company-name">{info.getValue()}</div>
                    <div className="company-cik">CIK: {info.row.original.cik}</div>
                </div>
            ),
        }),
        columnHelper.accessor(row => row.city !== 'Unknown' ? `${row.city}, ${row.state}` : 'Unknown', {
            id: 'location',
            header: 'Location',
            cell: info => (
                <div className="location-cell">
                    <MapPin size={14} className="cell-icon" />
                    <span>{info.getValue()}</span>
                </div>
            )
        }),
        columnHelper.accessor('industry', {
            header: 'Industry',
            cell: info => (
                <span className="industry-badge">
                    {info.getValue()}
                </span>
            ),
        }),
        columnHelper.accessor('revenue_range', {
            header: 'Revenue',
            cell: info => (
                <div className="revenue-cell">
                    <DollarSign size={14} className="cell-icon" />
                    <span>{info.getValue()}</span>
                </div>
            )
        }),
        columnHelper.accessor('amount_sold', {
            header: 'Amount Raised',
            cell: info => (
                <span className="amount-raised">
                    {info.getValue() && info.getValue() !== 'Unknown'
                        ? `$${parseInt(info.getValue()).toLocaleString()}`
                        : 'N/A'}
                </span>
            ),
        }),
        columnHelper.accessor('founded_year', {
            header: 'Founded',
            cell: info => (
                <div className="founded-cell">
                    <Building2 size={14} className="cell-icon" />
                    <span>{info.getValue()}</span>
                </div>
            )
        }),
        columnHelper.accessor('latest_filing_date', {
            header: 'Latest Filing',
            cell: info => (
                <div className="date-cell">
                    <Calendar size={14} className="cell-icon" />
                    <span>{info.getValue()}</span>
                </div>
            )
        }),
        columnHelper.accessor('enrichment_status', {
            header: 'AI Status',
            cell: info => (
                <EnrichmentBadge status={info.getValue()} size="sm" />
            )
        }),
        columnHelper.display({
            id: 'links',
            header: 'Links',
            cell: info => (
                <div className="links-cell">
                    {info.row.original.website_url && (
                        <a
                            href={info.row.original.website_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="link-button website-link"
                            onClick={(e) => e.stopPropagation()}
                            title="Visit Website"
                        >
                            <ExternalLink size={14} />
                        </a>
                    )}
                    {info.row.original.careers_url && (
                        <a
                            href={info.row.original.careers_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="link-button careers-link"
                            onClick={(e) => e.stopPropagation()}
                            title="Careers Page"
                        >
                            <FileText size={14} />
                        </a>
                    )}
                    {!info.row.original.website_url && !info.row.original.careers_url && (
                        <span className="no-links">-</span>
                    )}
                </div>
            ),
        }),
    ], [columnHelper]);

    const table = useReactTable({
        data: companies,
        columns,
        getCoreRowModel: getCoreRowModel(),
    });

    if (companies.length === 0) {
        return <div className="empty-state">No newly founded companies found. Try ingesting more data.</div>;
    }

    return (
        <div className="table-container">
            <table className="modern-table">
                <thead>
                    {table.getHeaderGroups().map(headerGroup => (
                        <tr key={headerGroup.id}>
                            {headerGroup.headers.map(header => (
                                <th key={header.id}>
                                    {header.isPlaceholder
                                        ? null
                                        : flexRender(
                                            header.column.columnDef.header,
                                            header.getContext()
                                        )}
                                </th>
                            ))}
                        </tr>
                    ))}
                </thead>
                <tbody>
                    {table.getRowModel().rows.map(row => (
                        <tr
                            key={row.id}
                            onClick={() => setSelectedCompany(row.original)}
                            className="table-row"
                            title="Click to view details"
                        >
                            {row.getVisibleCells().map(cell => (
                                <td key={cell.id}>
                                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                </td>
                            ))}
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

