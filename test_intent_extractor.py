"""
Comprehensive test suite for NLP intent extractor.

Tests all specified language patterns:
- Price bounds (upper, lower, ranges, approximate)
- Ratings
- Categories (with synonyms)
- Brands
- Attributes (colors, sizes)
- Fuzzy keywords
- Conflict detection
- Combined queries
"""
import sys
import io

# Fix Windows UTF-8 encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, 'D:/contextual-search')

from app.nlp.intent_extractor import extract_intent


def test_price_upper_bound():
    """Test upper price bound patterns."""
    print("\n=== Testing Price Upper Bounds ===")
    
    test_cases = [
        ("laptop under 50000", 50000),
        ("shoes below 3000", 3000),
        ("headphones less than 2000", 2000),
        ("watch cheaper than 5000", 5000),
        ("phone within 30000", 30000),
        ("bag max 2500", 2500),
        ("tablet upto 15000", 15000),
        ("not more than 10000", 10000),
    ]
    
    for query, expected_max in test_cases:
        result = extract_intent(query)
        actual_max = result['constraints']['price_max']
        status = "✓" if actual_max == expected_max else "✗"
        print(f"{status} '{query}' -> price_max={actual_max} (expected {expected_max})")


def test_price_lower_bound():
    """Test lower price bound patterns."""
    print("\n=== Testing Price Lower Bounds ===")
    
    test_cases = [
        ("laptop over 40000", 40000),
        ("shoes above 2000", 2000),
        ("watch more than 5000", 5000),
        ("starting from 3000", 3000),
        ("minimum 2500", 2500),
        ("at least 10000", 10000),
    ]
    
    for query, expected_min in test_cases:
        result = extract_intent(query)
        actual_min = result['constraints']['price_min']
        status = "✓" if actual_min == expected_min else "✗"
        print(f"{status} '{query}' -> price_min={actual_min} (expected {expected_min})")


def test_price_ranges():
    """Test price range patterns."""
    print("\n=== Testing Price Ranges ===")
    
    test_cases = [
        ("between 2000 and 5000", 2000, 5000),
        ("from 3000 to 7000", 3000, 7000),
        ("2000-5000", 2000, 5000),
        ("in the range of 3000 to 6000", 3000, 6000),
        ("budget 4000 to 8000", 4000, 8000),
    ]
    
    for query, expected_min, expected_max in test_cases:
        result = extract_intent(query)
        actual_min = result['constraints']['price_min']
        actual_max = result['constraints']['price_max']
        status = "✓" if (actual_min == expected_min and actual_max == expected_max) else "✗"
        print(f"{status} '{query}' -> {actual_min}-{actual_max} (expected {expected_min}-{expected_max})")


def test_approximate_prices():
    """Test approximate price patterns (±15%)."""
    print("\n=== Testing Approximate Prices ===")
    
    test_cases = [
        ("around 3000", 3000, 0.15),
        ("approx 5000", 5000, 0.15),
        ("about 4000", 4000, 0.15),
        ("near 6000", 6000, 0.15),
    ]
    
    for query, base_price, margin_pct in test_cases:
        result = extract_intent(query)
        expected_min = round(base_price * (1 - margin_pct), 2)
        expected_max = round(base_price * (1 + margin_pct), 2)
        actual_min = result['constraints']['price_min']
        actual_max = result['constraints']['price_max']
        is_approx = result['constraints']['approximate_price']
        status = "✓" if (is_approx and actual_min == expected_min and actual_max == expected_max) else "✗"
        print(f"{status} '{query}' -> {actual_min}-{actual_max} (expected {expected_min}-{expected_max}, approx={is_approx})")


def test_ratings():
    """Test rating patterns."""
    print("\n=== Testing Ratings ===")
    
    test_cases = [
        ("rated above 4", 4.0),
        ("rating more than 4.5", 4.5),
        ("at least 4 stars", 4.0),
        ("4+ rating", 4.0),
        ("highly rated", 4.5),
        ("best rated", 4.5),
    ]
    
    for query, expected_rating in test_cases:
        result = extract_intent(query)
        actual_rating = result['constraints']['rating_min']
        status = "✓" if actual_rating == expected_rating else "✗"
        print(f"{status} '{query}' -> rating_min={actual_rating} (expected {expected_rating})")


def test_categories():
    """Test category extraction with synonyms."""
    print("\n=== Testing Categories ===")
    
    test_cases = [
        ("shoes", "shoes"),
        ("sneakers", "shoes"),  # Synonym
        ("footwear", "shoes"),  # Synonym
        ("headphones", "headphones"),
        ("earphones", "headphones"),  # Synonym
        ("laptop", "laptop"),
        ("mobile phone", "electronics"),  # Synonym
        ("smartphone", "electronics"),  # Synonym
    ]
    
    for query, expected_category in test_cases:
        result = extract_intent(query)
        actual_category = result['constraints']['category']
        status = "✓" if actual_category == expected_category else "✗"
        print(f"{status} '{query}' -> category={actual_category} (expected {expected_category})")


def test_brands():
    """Test brand extraction."""
    print("\n=== Testing Brands ===")
    
    test_cases = [
        ("Nike shoes", "Nike"),
        ("adidas sneakers", "Adidas"),
        ("Sony headphones", "Sony"),
        ("Apple laptop", "Apple"),
        ("Samsung phone", "Samsung"),
    ]
    
    for query, expected_brand in test_cases:
        result = extract_intent(query)
        actual_brand = result['constraints']['brand']
        status = "✓" if actual_brand == expected_brand else "✗"
        print(f"{status} '{query}' -> brand={actual_brand} (expected {expected_brand})")


def test_colors():
    """Test color extraction."""
    print("\n=== Testing Colors ===")
    
    test_cases = [
        ("black shoes", "black"),
        ("white sneakers", "white"),
        ("red headphones", "red"),
        ("blue laptop bag", "blue"),
    ]
    
    for query, expected_color in test_cases:
        result = extract_intent(query)
        actual_color = result['constraints']['color']
        status = "✓" if actual_color == expected_color else "✗"
        print(f"{status} '{query}' -> color={actual_color} (expected {expected_color})")


def test_sizes():
    """Test size extraction."""
    print("\n=== Testing Sizes ===")
    
    test_cases = [
        ("size 9 shoes", "9"),
        ("medium t-shirt", "MEDIUM"),
        ("large bag", "LARGE"),
        ("XL shirt", "XL"),
    ]
    
    for query, expected_size in test_cases:
        result = extract_intent(query)
        actual_size = result['constraints']['size']
        status = "✓" if actual_size == expected_size else "✗"
        print(f"{status} '{query}' -> size={actual_size} (expected {expected_size})")


def test_fuzzy_keywords():
    """Test fuzzy price keyword detection."""
    print("\n=== Testing Fuzzy Keywords ===")
    
    test_cases = [
        "cheap shoes",
        "budget laptop",
        "affordable phone",
        "premium headphones",
        "luxury watch",
    ]
    
    for query in test_cases:
        result = extract_intent(query)
        is_fuzzy = result['constraints']['fuzzy_price']
        has_numeric = result['constraints']['price_min'] or result['constraints']['price_max']
        status = "✓" if (is_fuzzy and not has_numeric) else "✗"
        print(f"{status} '{query}' -> fuzzy_price={is_fuzzy}, no numeric constraint={not has_numeric}")


def test_conflicts():
    """Test conflicting constraint detection."""
    print("\n=== Testing Conflict Detection ===")
    
    test_cases = [
        ("under 2000 over 5000", True),  # Conflict
        ("over 5000 under 2000", True),  # Conflict
        ("between 2000 and 5000", False),  # No conflict
        ("under 5000", False),  # No conflict
    ]
    
    for query, expected_conflict in test_cases:
        result = extract_intent(query)
        actual_conflict = result['constraints']['conflict']
        status = "✓" if actual_conflict == expected_conflict else "✗"
        print(f"{status} '{query}' -> conflict={actual_conflict} (expected {expected_conflict})")


def test_combined_queries():
    """Test complex queries with multiple constraints."""
    print("\n=== Testing Combined Queries ===")
    
    query = "Nike shoes under 3000 rated above 4"
    result = extract_intent(query)
    
    checks = [
        ("brand", result['constraints']['brand'], "Nike"),
        ("category", result['constraints']['category'], "shoes"),
        ("price_max", result['constraints']['price_max'], 3000),
        ("rating_min", result['constraints']['rating_min'], 4.0),
    ]
    
    print(f"Query: '{query}'")
    for name, actual, expected in checks:
        status = "✓" if actual == expected else "✗"
        print(f"  {status} {name}={actual} (expected {expected})")
    
    print(f"  Semantic query: '{result['semantic_query']}'")


def test_semantic_query_cleaning():
    """Test semantic query cleaning."""
    print("\n=== Testing Semantic Query Cleaning ===")
    
    test_cases = [
        ("laptop under 50000", "laptop"),
        ("Nike shoes", "Nike shoes"),  # Brand/category preserved
        ("between 2000 and 5000", "products"),  # Only constraints, use generic
        ("shoes rated above 4", "shoes"),  # Category preserved, rating removed
    ]
    
    for query, expected_semantic in test_cases:
        result = extract_intent(query)
        actual_semantic = result['semantic_query']
        # Allow some flexibility in whitespace
        status = "✓" if actual_semantic.strip() == expected_semantic.strip() else "✗"
        print(f"{status} '{query}' -> '{actual_semantic}' (expected '{expected_semantic}')")


def run_all_tests():
    """Run all test suites."""
    print("\n" + "="*60)
    print("NLP INTENT EXTRACTOR - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    test_price_upper_bound()
    test_price_lower_bound()
    test_price_ranges()
    test_approximate_prices()
    test_ratings()
    test_categories()
    test_brands()
    test_colors()
    test_sizes()
    test_fuzzy_keywords()
    test_conflicts()
    test_combined_queries()
    test_semantic_query_cleaning()
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETED")
    print("="*60)


if __name__ == "__main__":
    run_all_tests()
