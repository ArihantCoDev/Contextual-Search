export default function Filters({ filters, onChange }) {
    const handleChange = (key, value) => {
        onChange({ ...filters, [key]: value });
    };

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
                    <div className="flex space-x-2">
                        <input
                            type="number"
                            placeholder="Min"
                            value={filters.price_min || ''}
                            onChange={(e) => handleChange('price_min', e.target.value)}
                            className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-500 transition-all"
                        />
                        <input
                            type="number"
                            placeholder="Max"
                            value={filters.price_max || ''}
                            onChange={(e) => handleChange('price_max', e.target.value)}
                            className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-500 transition-all"
                        />
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
                        <option value="3">3 Stars & Up</option>
                        <option value="4">4 Stars & Up</option>
                        <option value="4.5">4.5 Stars & Up</option>
                    </select>
                </div>

            </div>
        </div>
    );
}
