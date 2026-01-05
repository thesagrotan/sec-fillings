export interface Company {
    id: number;
    cik: string;
    name: string;
    city: string;
    state: string;
    industry: string;
    founded_year: string;
    latest_filing_date: string;
    revenue_range: string;
    amount_sold: string;
    jurisdiction: string;
    executive_name: string;
    executive_title: string;
    website_url?: string;
    careers_url?: string;

    // Intelligence Signals (stored as JSON strings)
    maturity_info?: string;
    funding_details?: string;
    founder_analysis?: string;
    public_presence_quality?: string;
    hiring_signal?: string;
    design_opportunity?: string;
    engagement_recommendation?: string;

    // AI Enrichment Status
    enrichment_status?: 'pending' | 'processing' | 'completed' | 'failed';
}
