import { useEffect, useState } from 'react';
import { fetchCompanies, triggerIngest } from './services/api';
import type { CompanyFilters } from './services/api';
import type { Company } from './types';
import { CompaniesTable } from './components/CompaniesTable';
import { Filters } from './components/Filters';

function App() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [ingesting, setIngesting] = useState(false);
  const [filters, setFilters] = useState<CompanyFilters>({});

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchCompanies(filters);
      setCompanies(data);
    } catch (error) {
      console.error("Failed to fetch companies", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [filters]);

  const handleIngest = async () => {
    setIngesting(true);
    try {
      // Use the selected limit from filters, or default to 10 if not set or if "All" (which might be undefined/custom)
      // Actually filters.limit is number.
      // If limit is not set in filters (initial load), default to 10. `filters.limit || 10`.
      await triggerIngest(filters.limit || 10);
      await loadData();
    } catch (error) {
      console.error("Failed to ingest", error);
      alert("Failed to ingest new filings. Check backend logs.");
    } finally {
      setIngesting(false);
    }
  };

  return (
    <div>
      <h1>Startup Discovery</h1>
      <p style={{ color: '#aaa', marginBottom: '2rem' }}>
        Discover newly funded and founded companies via SEC Form D filings.
      </p>

      <Filters
        filters={filters}
        setFilters={setFilters}
        onRefresh={handleIngest}
        isRefreshing={ingesting}
      />

      {loading ? (
        <div>Loading companies...</div>
      ) : (
        <CompaniesTable companies={companies} />
      )}
    </div>
  );
}

export default App;
