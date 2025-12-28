import { useState, useEffect } from 'react';

export default function Filters({ filters, onChange }) {
    const [errors, setErrors] = useState({
        price_min: '',
        price_max: '',
        range: ''
    });

    // Validate price inputs
    const validatePrices = (minPrice, maxPrice) => {
        const newErrors = { price_min: '', price_max: '', range: '' };

        // Check for negative prices
        if (minPrice && parseFloat(minPrice) < 0) {
            newErrors.price_min = 'Price cannot be less than 0';
        }
        if (maxPrice && parseFloat(maxPrice) < 0) {
            newErrors.price_max = 'Price cannot be less than 0';
        }

        // Check if min > max (only if both are valid and positive)
        if (minPrice && maxPrice &&
            parseFloat(minPrice) >= 0 && parseFloat(maxPrice) >= 0) {
            const min = parseFloat(minPrice);
            const max = parseFloat(maxPrice);

            if (min > max) {
                newErrors.range = 'Minimum price cannot exceed maximum price';
                // Don't auto-swap in UI - backend will handle swap during search
            }
        }

        setErrors(newErrors);
        return newErrors;
    };

    const handleChange = (key, value) => {
        const newFilters = { ...filters, [key]: value };
        onChange(newFilters);

        // Validate prices if price field changed
        if (key === 'price_min' || key === 'price_max') {
            validatePrices(
                key === 'price_min' ? value : filters.price_min,
                key === 'price_max' ? value : filters.price_max
            );
        }
    };

    // Clear errors when values become valid
    useEffect(() => {
        validatePrices(filters.price_min, filters.price_max);
    }, [filters.price_min, filters.price_max]);

    const hasError = (field) => errors[field] && errors[field].length > 0;

    return (
        <div className="w-full max-w-3xl mx-auto mt-6 p-6 bg-white rounded-xl border border-slate-200 shadow-sm animate-fade-in">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                {/* Category Filter */}
                <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">Category</label>
                    <select
                        value={filters.category || ''}
                        onChange={(e) => handleChange('category', e.target.value)}
                        className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-500 transition-all"
                    >
                        <option value="">All Categories</option>
                        <option value="Footwear">Footwear</option>
                        <option value="Electronics">Electronics</option>
                        <option value="Accessories">Accessories</option>
                        <option value="Clothing">Clothing</option>
                        <option value="Home">Home</option>
                    </select>
                </div>

                {/* Price Range */}
                <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">Price Range</label>
                    <div className="space-y-2">
                        <div className="flex space-x-2">
                            <input
                                type="number"
                                placeholder="Min"
                                value={filters.price_min || ''}
                                onChange={(e) => handleChange('price_min', e.target.value)}
                                className={`w-full px-3 py-2 bg-slate-50 border rounded-lg text-sm focus:outline-none focus:ring-2 transition-all ${hasError('price_min') || hasError('range')
                                    ? 'border-red-500 focus:ring-red-100 focus:border-red-500'
                                    : 'border-slate-200 focus:ring-blue-100 focus:border-blue-500'
                                    }`}
                            />
                            <input
                                type="number"
                                placeholder="Max"
                                value={filters.price_max || ''}
                                onChange={(e) => handleChange('price_max', e.target.value)}
                                className={`w-full px-3 py-2 bg-slate-50 border rounded-lg text-sm focus:outline-none focus:ring-2 transition-all ${hasError('price_max') || hasError('range')
                                    ? 'border-red-500 focus:ring-red-100 focus:border-red-500'
                                    : 'border-slate-200 focus:ring-blue-100 focus:border-blue-500'
                                    }`}
                            />
                        </div>

                        {/* Error Messages */}
                        {hasError('price_min') && (
                            <p className="text-xs text-red-600 flex items-center">
                                <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                </svg>
                                {errors.price_min}
                            </p>
                        )}
                        {hasError('price_max') && (
                            <p className="text-xs text-red-600 flex items-center">
                                <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                </svg>
                                {errors.price_max}
                            </p>
                        )}
                        {hasError('range') && (
                            <p className="text-xs text-amber-600 flex items-center">
                                <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                </svg>
                                {errors.range} (Search will use swapped values)
                            </p>
                        )}
                    </div>
                </div>

                {/* Rating Filter */}
                <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">Rating</label>
                    <select
                        value={filters.rating || ''}
                        onChange={(e) => handleChange('rating', e.target.value)}
                        className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-500 transition-all"
                    >
                        <option value="">Any Rating</option>
                        <option value="3">3 Stars &amp; Up</option>
                        <option value="4">4 Stars &amp; Up</option>
                        <option value="4.5">4.5 Stars &amp; Up</option>
                    </select>
                </div>

            </div>
        </div>
    );
}
