import { useState, useEffect } from 'react';
import { checkBackendHealth } from '../services/api';

export default function Home() {
    const [status, setStatus] = useState('loading'); // loading, healthy, error

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

    return (
        <div className="min-h-screen pt-16 bg-slate-50">
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-8 animate-fade-in">
                    <h1 className="text-3xl font-bold text-slate-900 mb-4">
                        Welcome to Contextual Search
                    </h1>
                    <p className="text-lg text-slate-600 mb-8 max-w-2xl">
                        Experience the next generation of product search. Connect to our intelligent backend to explore semantically relevant results.
                    </p>

                    <div className="flex items-center space-x-3 p-4 bg-slate-50 rounded-lg border border-slate-200 w-fit">
                        <span className="text-sm font-medium text-slate-700">Backend Status:</span>
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
