export default function ProductCard({ product }) {
    // Defensive checks for missing data
    const {
        title: name = 'Unnamed Product', // Map title to name for internal use
        category = 'Uncategorized',
        brand = 'Generic',
        price = 0,
        rating = 0,
        image_url
    } = product || {};

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden hover:shadow-md hover:-translate-y-1 transition-all duration-300 group h-full flex flex-col">
            {/* Image Area */}
            <div className="aspect-w-4 aspect-h-3 bg-slate-100 relative overflow-hidden">
                {image_url ? (
                    <img
                        src={image_url}
                        alt={name}
                        className="w-full h-48 object-cover object-center group-hover:scale-105 transition-transform duration-500"
                    />
                ) : (
                    <div className="w-full h-48 flex items-center justify-center text-slate-300">
                        <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                    </div>
                )}
                <div className="absolute top-2 right-2 bg-white/90 backdrop-blur-sm px-2 py-1 rounded-md text-xs font-semibold text-slate-600 shadow-sm">
                    {category}
                </div>
            </div>

            {/* Content Area */}
            <div className="p-4 flex-1 flex flex-col">
                <div className="text-xs text-blue-600 font-semibold uppercase tracking-wide mb-1">
                    {brand}
                </div>
                <h3 className="text-base font-medium text-slate-900 mb-2 line-clamp-2 leading-snug flex-1">
                    {name}
                </h3>

                <div className="mt-4 flex items-center justify-between">
                    <div className="flex items-center space-x-1">
                        <span className="text-lg font-bold text-slate-900">
                            ${typeof price === 'number' ? price.toFixed(2) : price}
                        </span>
                    </div>
                    <div className="flex items-center text-amber-500 text-sm font-medium">
                        <svg className="w-4 h-4 mr-1 fill-current" viewBox="0 0 20 20">
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                        {rating}
                    </div>
                </div>
            </div>
        </div>
    );
}
