import axios from 'axios';
import type { Company } from '../types';

const API_URL = 'http://127.0.0.1:8000';

export interface CompanyFilters {
    industry?: string;
    city?: string;
    state?: string;
    revenue_range?: string;
    founded_year?: string;
    limit?: number;
    days_ago?: number;
    startup_mode?: boolean;
}

export const fetchCompanies = async (filters: CompanyFilters = {}): Promise<Company[]> => {
    const params = new URLSearchParams();
    if (filters.industry) params.append('industry', filters.industry);
    if (filters.city) params.append('city', filters.city);
    if (filters.state) params.append('state', filters.state);
    if (filters.revenue_range) params.append('revenue_range', filters.revenue_range);
    if (filters.founded_year) params.append('founded_year', filters.founded_year);
    if (filters.limit) params.append('limit', filters.limit.toString());
    if (filters.days_ago) params.append('days_ago', filters.days_ago.toString());
    if (filters.startup_mode) params.append('startup_mode', 'true');

    const response = await axios.get(`${API_URL}/companies`, { params });
    return response.data;
};

export const triggerIngest = async (limit: number = 10): Promise<{ message: string }> => {
    const response = await axios.post(`${API_URL}/ingest?limit=${limit}`);
    return response.data;
};

export const triggerEnrichment = async (companyId: number): Promise<{ status: string; company_id: number }> => {
    const response = await axios.post(`${API_URL}/companies/${companyId}/enrich`);
    return response.data;
};

export const fetchEnrichmentStatus = async (companyId: number): Promise<{ company_id: number; enrichment_status: string }> => {
    const response = await axios.get(`${API_URL}/companies/${companyId}/enrichment-status`);
    return response.data;
};

export const triggerEnrichAll = async (): Promise<{ status: string; message: string }> => {
    const response = await axios.post(`${API_URL}/enrich-all`);
    return response.data;
};
