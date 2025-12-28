import { useState, useEffect } from 'react';
import { checkBackendHealth, searchProducts } from '../services/api';
import SearchBar from '../components/SearchBar';
import Filters from '../components/Filters';
import ResultsGrid from '../components/ResultsGrid';

export default function Home() {
    const [status, setStatus] = useState('loading'); // loading, healthy, error
    const [searchState, setSearchState] = useState({
        query: '',
        loading: false,
        error: null,
        hasSearched: false,
        results: []
    });

    // Filter State
    const [filters, setFilters] = useState({
        category: '',
        price_min: '',
        price_max: '',
        rating: ''
    });

    useEffect(() => {
        const checkHealth = async () => {
            try {
                await checkBackendHealth();
                setStatus('healthy');
            } catch (error) {
                setStatus('error');
            }
        };

        checkHealth();
    }, []);

    const handleSearch = async (queryInput) => {
        // Query might come from SearchBar (string) or use existing state
        const queryToUse = typeof queryInput === 'string' ? queryInput : searchState.query;

        if (!queryToUse.trim()) return;

        setSearchState(prev => ({
            ...prev,
            query: queryToUse,
            loading: true,
            error: null,
            hasSearched: true,
            results: []
        }));

        try {
            // Map frontend filter keys to API expected keys
            // Only send filters that have actual values (not empty strings)
            const apiFilters = {};

            if (filters.category && filters.category.trim()) {
                apiFilters.category = filters.category;
            }

            if (filters.price_min && filters.price_min.trim()) {
                apiFilters.price_min = parseFloat(filters.price_min);
            }

            if (filters.price_max && filters.price_max.trim()) {
                apiFilters.price_max = parseFloat(filters.price_max);
            }

            if (filters.rating && filters.rating.trim()) {
                apiFilters.min_rating = parseFloat(filters.rating);
            }

            const data = await searchProducts(queryToUse, apiFilters);
            const results = Array.isArray(data) ? data : (data.results || []);

            setSearchState(prev => ({
                ...prev,
                loading: false,
                results: results
            }));
        } catch (error) {
            setSearchState(prev => ({
                ...prev,
                loading: false,
                error: 'Failed to complete search. Please check backend connection.'
            }));
        }
    };

    return (
        <div className="min-h-screen pt-16 bg-slate-50">
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="text-center mb-12 animate-fade-in">
                    <h1 className="text-4xl font-bold text-slate-900 mb-4">
                        Contextual Product Search
                    </h1>
                    <p className="text-lg text-slate-600 max-w-2xl mx-auto">
                        Find exactly what you're looking for using natural language.
                    </p>
                </div>

                <div className="mb-12 animate-fade-in" style={{ animationDelay: '0.1s' }}>
                    <SearchBar onSearch={handleSearch} isLoading={searchState.loading} />

                    <Filters filters={filters} onChange={setFilters} />

                    {searchState.error && (
                        <div className="mt-4 text-center text-red-600 bg-red-50 py-2 px-4 rounded-lg inline-block w-full max-w-3xl mx-auto">
                            {searchState.error}
                        </div>
                    )}

                    {searchState.loading && (
                        <div className="mt-8 text-center text-slate-500">
                            Searching relevant products...
                        </div>
                    )}

                    {!searchState.loading && searchState.hasSearched && (
                        <div className="mt-12">
                            {searchState.results.length > 0 ? (
                                <ResultsGrid results={searchState.results} />
                            ) : (
                                <div className="text-center text-slate-500 py-12 bg-white rounded-xl border border-slate-100">
                                    <p className="text-lg">No products found matching your underlying specific criteria.</p>
                                    <p className="text-sm mt-2">Try adjusting your filters or search query.</p>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                <div className="flex justify-center animate-fade-in" style={{ animationDelay: '0.2s' }}>
                    <div className="flex items-center space-x-3 p-4 bg-white rounded-lg border border-slate-100 shadow-sm">
                        <span className="text-sm font-medium text-slate-700">System Status:</span>
                        {status === 'loading' && (
                            <span className="flex items-center text-yellow-600 text-sm font-medium">
                                <span className="w-2 h-2 bg-yellow-500 rounded-full mr-2 animate-pulse"></span>
                                Checking...
                            </span>
                        )}
                        {status === 'healthy' && (
                            <span className="flex items-center text-emerald-600 text-sm font-medium">
                                <span className="w-2 h-2 bg-emerald-500 rounded-full mr-2"></span>
                                Operational
                            </span>
                        )}
                        {status === 'error' && (
                            <span className="flex items-center text-red-600 text-sm font-medium">
                                <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
                                Unreachable
                            </span>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}
