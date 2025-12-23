import { useEffect, useState, useCallback } from 'react';
import { fetchCompanies, triggerIngest } from './services/api';
import type { CompanyFilters } from './services/api';
import type { Company } from './types';
import { CompaniesTable } from './components/CompaniesTable';
import { Filters } from './components/Filters';
import { LayoutDashboard, RefreshCw, AlertCircle } from 'lucide-react';
import './App.css';

function App() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [ingesting, setIngesting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<CompanyFilters>({});

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchCompanies(filters);
      setCompanies(data);
    } catch (err) {
      console.error("Failed to fetch companies", err);
      setError("Failed to load companies. Please ensure the backend is running.");
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleIngest = async () => {
    setIngesting(true);
    setError(null);
    try {
      await triggerIngest(filters.limit || 10);
      await loadData();
    } catch (err) {
      console.error("Failed to ingest", err);
      setError("Failed to ingest new filings. Check backend logs for details.");
    } finally {
      setIngesting(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <LayoutDashboard className="app-logo" size={32} />
            <div>
              <h1>Startup Discovery</h1>
              <p className="subtitle">Real-time SEC Form D filing intelligence</p>
            </div>
          </div>
          <div className="header-actions">
            {/* Additional header actions could go here */}
          </div>
        </div>
      </header>

      <main className="app-content">
        <div className="content-wrapper">
          <div className="controls-section card">
            <Filters
              filters={filters}
              setFilters={setFilters}
              onRefresh={handleIngest}
              isRefreshing={ingesting}
            />
          </div>

          {error && (
            <div className="error-banner fade-in">
              <AlertCircle size={20} />
              <span>{error}</span>
            </div>
          )}

          <div className="results-section card">
            <div className="section-header">
              <h2>Recent Filings</h2>
              <span className="count-badge">{companies.length} results</span>
            </div>

            {loading ? (
              <div className="loading-state">
                <RefreshCw className="spin" size={24} />
                <span>Loading intelligence...</span>
              </div>
            ) : (
              <CompaniesTable companies={companies} />
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
