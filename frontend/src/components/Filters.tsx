import React from 'react';
import type { CompanyFilters } from '../services/api';

interface Props {
    filters: CompanyFilters;
    setFilters: React.Dispatch<React.SetStateAction<CompanyFilters>>;
    onRefresh: () => void;
    isRefreshing: boolean;
}

export const Filters: React.FC<Props> = ({ filters, setFilters, onRefresh, isRefreshing }) => {
    const handleChange = (key: keyof CompanyFilters, value: string) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    };

    return (
        <div className="filters">
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                <input
                    type="text"
                    placeholder="City"
                    value={filters.city || ''}
                    onChange={(e) => handleChange('city', e.target.value)}
                    style={{ width: '150px' }}
                />
                <input
                    type="text"
                    placeholder="State"
                    value={filters.state || ''}
                    onChange={(e) => handleChange('state', e.target.value)}
                    style={{ width: '100px' }}
                />
                <input
                    type="text"
                    placeholder="Industry"
                    value={filters.industry || ''}
                    onChange={(e) => handleChange('industry', e.target.value)}
                    style={{ width: '150px' }}
                />
                <select
                    value={filters.revenue_range || ''}
                    onChange={(e) => handleChange('revenue_range', e.target.value)}
                    style={{ width: '200px' }}
                >
                    <option value="">All Revenue Ranges</option>
                    <option value="$1 - $1,000,000">$1 - $1,000,000</option>
                    <option value="$1,000,001 - $5,000,000">$1,000,001 - $5,000,000</option>
                    <option value="$5,000,001 - $25,000,000">$5,000,001 - $25,000,000</option>
                    <option value="$25,000,001 - $100,000,000">$25,000,001 - $100,000,000</option>
                    <option value="Over $100,000,000">Over $100,000,000</option>
                    <option value="Decline to Disclose">Decline to Disclose</option>
                </select>
                <input
                    type="text"
                    placeholder="Founded Year"
                    value={filters.founded_year || ''}
                    onChange={(e) => handleChange('founded_year', e.target.value)}
                    style={{ width: '120px' }}
                />

                {/* New Filters */}
                <select
                    value={filters.limit || 100}
                    onChange={(e) => {
                        const val = parseInt(e.target.value);
                        setFilters(prev => ({ ...prev, limit: val }));
                    }}
                    style={{ width: '120px' }}
                >
                    <option value="10">Limit: 10</option>
                    <option value="50">Limit: 50</option>
                    <option value="100">Limit: 100</option>
                    <option value="500">Limit: 500</option>
                </select>

                <select
                    value={filters.days_ago || ''}
                    onChange={(e) => {
                        const val = e.target.value ? parseInt(e.target.value) : undefined;
                        setFilters(prev => ({ ...prev, days_ago: val }));
                    }}
                    style={{ width: '150px' }}
                >
                    <option value="">Any Time</option>
                    <option value="1">Last 24 Hours</option>
                    <option value="3">Last 3 Days</option>
                    <option value="7">Last Week</option>
                    <option value="14">Last 2 Weeks</option>
                    <option value="30">Last Month</option>
                </select>

                <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <input
                        type="checkbox"
                        id="startup-mode"
                        checked={filters.startup_mode || false}
                        onChange={(e) => setFilters(prev => ({ ...prev, startup_mode: e.target.checked }))}
                    />
                    <label htmlFor="startup-mode">Show Startups Only</label>
                </div>
            </div>

            <div style={{ flexGrow: 1 }}></div>

            <button onClick={onRefresh} disabled={isRefreshing}>
                {isRefreshing ? 'Scanning SEC...' : 'Scan New Filings'}
            </button>
        </div>
    );
};
