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
}
