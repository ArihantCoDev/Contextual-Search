import ProductCard from './ProductCard';

export default function ResultsGrid({ results }) {
    if (!results || results.length === 0) {
        return null;
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-fade-in">
            {results.map((product) => (
                <ProductCard key={product.id || Math.random()} product={product} />
            ))}
        </div>
    );
}
