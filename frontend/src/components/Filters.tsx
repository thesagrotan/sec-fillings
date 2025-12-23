import React from 'react';
import type { CompanyFilters } from '../services/api';
import { MapPin, Briefcase, DollarSign, Calendar, Filter as FilterIcon, RotateCcw } from 'lucide-react';
import './Filters.css';

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

    const handleLimitChange = (value: string) => {
        setFilters(prev => ({ ...prev, limit: parseInt(value) }));
    };

    const handleDaysChange = (value: string) => {
        const val = value ? parseInt(value) : undefined;
        setFilters(prev => ({ ...prev, days_ago: val }));
    };

    return (
        <div className="filters-container">
            <div className="filters-header">
                <div className="header-title">
                    <FilterIcon size={18} />
                    <h3>Filters</h3>
                </div>
                <div className="refresh-section">
                    <button
                        onClick={onRefresh}
                        disabled={isRefreshing}
                        className="primary refresh-button"
                    >
                        <RotateCcw size={16} className={isRefreshing ? "spin" : ""} />
                        {isRefreshing ? 'Scanning...' : 'Scan New Filings'}
                    </button>
                </div>
            </div>

            <div className="filters-grid">
                <div className="filter-group">
                    <label>Location</label>
                    <div className="input-wrapper">
                        <MapPin size={16} className="input-icon" />
                        <input
                            type="text"
                            placeholder="City"
                            value={filters.city || ''}
                            onChange={(e) => handleChange('city', e.target.value)}
                        />
                    </div>
                    <div className="input-wrapper">
                        <MapPin size={16} className="input-icon" />
                        <input
                            type="text"
                            placeholder="State"
                            value={filters.state || ''}
                            onChange={(e) => handleChange('state', e.target.value)}
                            className="state-input"
                        />
                    </div>
                </div>

                <div className="filter-group">
                    <label>Industry</label>
                    <div className="input-wrapper">
                        <Briefcase size={16} className="input-icon" />
                        <input
                            type="text"
                            placeholder="Industry (e.g. Tech)"
                            value={filters.industry || ''}
                            onChange={(e) => handleChange('industry', e.target.value)}
                        />
                    </div>
                </div>

                <div className="filter-group">
                    <label>Revenue</label>
                    <div className="input-wrapper">
                        <DollarSign size={16} className="input-icon" />
                        <select
                            value={filters.revenue_range || ''}
                            onChange={(e) => handleChange('revenue_range', e.target.value)}
                        >
                            <option value="">All Revenue Ranges</option>
                            <option value="$1 - $1,000,000">$1 - $1M</option>
                            <option value="$1,000,001 - $5,000,000">$1M - $5M</option>
                            <option value="$5,000,001 - $25,000,000">$5M - $25M</option>
                            <option value="$25,000,001 - $100,000,000">$25M - $100M</option>
                            <option value="Over $100,000,000">Over $100M</option>
                            <option value="Decline to Disclose">Decline to Disclose</option>
                        </select>
                    </div>
                </div>

                <div className="filter-group">
                    <label>Founded</label>
                    <div className="input-wrapper">
                        <Calendar size={16} className="input-icon" />
                        <input
                            type="text"
                            placeholder="Year"
                            value={filters.founded_year || ''}
                            onChange={(e) => handleChange('founded_year', e.target.value)}
                        />
                    </div>
                </div>
            </div>

            <div className="filters-advanced">
                <div className="advanced-group">
                    <span className="label">Scan Settings:</span>
                    <select
                        value={filters.limit || 100}
                        onChange={(e) => handleLimitChange(e.target.value)}
                        className="small-select"
                    >
                        <option value="10">Limit: 10</option>
                        <option value="50">Limit: 50</option>
                        <option value="100">Limit: 100</option>
                        <option value="500">Limit: 500</option>
                    </select>

                    <select
                        value={filters.days_ago || ''}
                        onChange={(e) => handleDaysChange(e.target.value)}
                        className="small-select"
                    >
                        <option value="">Any Time</option>
                        <option value="1">Last 24 Hours</option>
                        <option value="3">Last 3 Days</option>
                        <option value="7">Last Week</option>
                        <option value="14">Last 2 Weeks</option>
                        <option value="30">Last Month</option>
                    </select>
                </div>

                <label className="checkbox-label">
                    <input
                        type="checkbox"
                        checked={filters.startup_mode || false}
                        onChange={(e) => setFilters(prev => ({ ...prev, startup_mode: e.target.checked }))}
                    />
                    <span className="checkbox-text">Startup Mode Only</span>
                </label>
            </div>
        </div>
    );
};
