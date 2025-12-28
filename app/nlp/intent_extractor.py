"""
NLP-based intent extraction module.

Converts free-form natural language queries into structured intent objects
with semantic queries and extracted constraints (price, rating, category, etc.).

This module is DETERMINISTIC and does NOT apply filters or rank products.
It ONLY extracts intent from text.
"""
import re
from typing import Dict, Any, Optional, List, Tuple


# Category synonyms mapping
CATEGORY_SYNONYMS = {
    'sneakers': 'shoes',
    'footwear': 'shoes',
    'earphones': 'headphones',
    'mobile': 'electronics',
    'smartphone': 'electronics',
    'phone': 'electronics',
}

# Known categories (normalized)
KNOWN_CATEGORIES = {
    'shoes', 'headphones', 'laptop', 'electronics', 'accessories',
    'clothing', 'watches', 'bags', 'furniture', 'books'
}

# Known brands (case-insensitive matching)
KNOWN_BRANDS = {
    'nike', 'adidas', 'sony', 'apple', 'samsung', 'lg', 'dell',
    'hp', 'lenovo', 'asus', 'bose', 'jbl', 'boat', 'realme'
}

# Color keywords
COLORS = {
    'black', 'white', 'red', 'blue', 'green', 'yellow', 'orange',
    'purple', 'pink', 'brown', 'grey', 'gray', 'silver', 'gold'
}

# Size keywords
SIZE_PATTERNS = [
    r'\bsize\s+(\d+|[smlxSMLX]+)\b',
    r'\b(small|medium|large|x-?large|xx-?large)\b',
    r'\b([smlxSMLX]{1,3})\b(?=\s|$)',  # S, M, L, XL, XXL, etc.
]

# Fuzzy price keywords (no numeric assignment)
FUZZY_KEYWORDS = {
    'cheap', 'budget', 'affordable', 'economical', 'inexpensive',
    'premium', 'expensive', 'luxury', 'high-end'
}


def extract_intent(query: str) -> Dict[str, Any]:
    """
    Extract structured intent from a natural language query.
    
    Args:
        query: Raw user query string
        
    Returns:
        Dictionary with:
        - semantic_query: Query without numeric constraints
        - constraints: Dict of extracted constraints
    """
    query_lower = query.lower()
    
    # Initialize constraints
    constraints = {
        'price_min': None,
        'price_max': None,
        'rating_min': None,
        'category': None,
        'brand': None,
        'color': None,
        'size': None,
        'approximate_price': False,
        'fuzzy_price': False,
        'conflict': False
    }
    
    # Track what text to remove from semantic query
    removal_spans: List[Tuple[int, int]] = []
    
    # Extract price constraints
    price_info = _extract_price(query_lower)
    if price_info:
        constraints['price_min'] = price_info.get('price_min')
        constraints['price_max'] = price_info.get('price_max')
        constraints['approximate_price'] = price_info.get('approximate_price', False)
        removal_spans.extend(price_info.get('removal_spans', []))
    
    # Extract rating constraints
    rating_info = _extract_rating(query_lower)
    if rating_info:
        constraints['rating_min'] = rating_info.get('rating_min')
        removal_spans.extend(rating_info.get('removal_spans', []))
    
    # Extract category
    category_info = _extract_category(query_lower)
    if category_info:
        constraints['category'] = category_info.get('category')
        # Don't remove category from query as it's part of semantic intent
    
    # Extract brand
    brand_info = _extract_brand(query_lower)
    if brand_info:
        constraints['brand'] = brand_info.get('brand')
        # Don't remove brand from query as it's part of semantic intent
    
    # Extract color
    color_info = _extract_color(query_lower)
    if color_info:
        constraints['color'] = color_info.get('color')
        # Don't remove color from query as it's part of semantic intent
    
    # Extract size
    size_info = _extract_size(query_lower)
    if size_info:
        constraints['size'] = size_info.get('size')
        removal_spans.extend(size_info.get('removal_spans', []))
    
    # Detect fuzzy price intent
    if _has_fuzzy_price_keywords(query_lower):
        constraints['fuzzy_price'] = True
    
    # Detect conflicts
    if constraints['price_min'] and constraints['price_max']:
        if constraints['price_min'] > constraints['price_max']:
            constraints['conflict'] = True
    
    # Generate semantic query (remove numeric constraints)
    semantic_query = _clean_semantic_query(query, removal_spans)
    
    return {
        'semantic_query': semantic_query,
        'constraints': constraints
    }


def _extract_price(query: str) -> Optional[Dict[str, Any]]:
    """Extract price constraints from query."""
    result = {
        'price_min': None,
        'price_max': None,
        'approximate_price': False,
        'removal_spans': []
    }
    
    # Approximate price patterns (±15%)
    approx_patterns = [
        r'around\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
        r'approx(?:imately)?\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
        r'about\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
        r'near\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
    ]
    
    for pattern in approx_patterns:
        match = re.search(pattern, query)
        if match:
            price = float(match.group(1).replace(',', ''))
            margin = price * 0.15
            result['price_min'] = round(price - margin, 2)
            result['price_max'] = round(price + margin, 2)
            result['approximate_price'] = True
            result['removal_spans'].append((match.start(), match.end()))
            return result
    
    # Price range patterns
    range_patterns = [
        r'between\s+(\d+(?:,\d{3})*(?:\.\d+)?)\s+(?:and|to)\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
        r'from\s+(\d+(?:,\d{3})*(?:\.\d+)?)\s+to\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
        r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*[-–]\s*(\d+(?:,\d{3})*(?:\.\d+)?)',
        r'in\s+the\s+range\s+of\s+(\d+(?:,\d{3})*(?:\.\d+)?)\s+to\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
        r'budget\s+(?:of\s+)?(\d+(?:,\d{3})*(?:\.\d+)?)\s+to\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
    ]
    
    for pattern in range_patterns:
        match = re.search(pattern, query)
        if match:
            result['price_min'] = float(match.group(1).replace(',', ''))
            result['price_max'] = float(match.group(2).replace(',', ''))
            result['removal_spans'].append((match.start(), match.end()))
            return result
    
    # Price upper bound patterns
    upper_patterns = [
        r'under\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
        r'below\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
        r'less\s+than\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
        r'cheaper\s+than\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
        r'within\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
        r'max(?:imum)?\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
        r'up\s*to\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
        r'not\s+more\s+than\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
    ]
    
    for pattern in upper_patterns:
        match = re.search(pattern, query)
        if match:
            result['price_max'] = float(match.group(1).replace(',', ''))
            result['removal_spans'].append((match.start(), match.end()))
            # Don't return yet, check for lower bound too
            break
    
    # Price lower bound patterns
    lower_patterns = [
        r'over\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
        r'above\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
        r'more\s+than\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
        r'starting\s+from\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
        r'minimum\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
        r'at\s+least\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
    ]
    
    for pattern in lower_patterns:
        match = re.search(pattern, query)
        if match:
            result['price_min'] = float(match.group(1).replace(',', ''))
            result['removal_spans'].append((match.start(), match.end()))
            break
    
    # Return if any price constraint found
    if result['price_min'] or result['price_max']:
        return result
    
    return None


def _extract_rating(query: str) -> Optional[Dict[str, Any]]:
    """Extract rating constraints from query."""
    result = {
        'rating_min': None,
        'removal_spans': []
    }
    
    # Special keywords
    if re.search(r'\b(highly|best)\s+rated\b', query):
        result['rating_min'] = 4.5
        match = re.search(r'\b(highly|best)\s+rated\b', query)
        if match:
            result['removal_spans'].append((match.start(), match.end()))
        return result
    
    # Rating patterns
    rating_patterns = [
        r'rated\s+above\s+(\d+(?:\.\d+)?)',
        r'rating\s+(?:more\s+than|above|over)\s+(\d+(?:\.\d+)?)',
        r'at\s+least\s+(\d+(?:\.\d+)?)\s+stars?',
        r'(\d+(?:\.\d+)?)\+\s+rating',
        r'rating\s+(?:of\s+)?(\d+(?:\.\d+)?)\+',
    ]
    
    for pattern in rating_patterns:
        match = re.search(pattern, query)
        if match:
            result['rating_min'] = float(match.group(1))
            result['removal_spans'].append((match.start(), match.end()))
            return result
    
    return None


def _extract_category(query: str) -> Optional[Dict[str, Any]]:
    """Extract category from query."""
    # Check for synonyms first
    for synonym, category in CATEGORY_SYNONYMS.items():
        if re.search(rf'\b{synonym}\b', query):
            return {'category': category}
    
    # Check for direct category matches
    for category in KNOWN_CATEGORIES:
        if re.search(rf'\b{category}\b', query):
            return {'category': category}
    
    return None


def _extract_brand(query: str) -> Optional[Dict[str, Any]]:
    """Extract brand from query."""
    for brand in KNOWN_BRANDS:
        if re.search(rf'\b{brand}\b', query, re.IGNORECASE):
            return {'brand': brand.capitalize()}
    
    return None


def _extract_color(query: str) -> Optional[Dict[str, Any]]:
    """Extract color from query."""
    for color in COLORS:
        if re.search(rf'\b{color}\b', query):
            return {'color': color}
    
    return None


def _extract_size(query: str) -> Optional[Dict[str, Any]]:
    """Extract size from query."""
    result = {
        'size': None,
        'removal_spans': []
    }
    
    for pattern in SIZE_PATTERNS:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            # Get the size value (first capturing group)
            size = match.group(1).upper()
            result['size'] = size
            result['removal_spans'].append((match.start(), match.end()))
            return result
    
    return None


def _has_fuzzy_price_keywords(query: str) -> bool:
    """Check if query contains fuzzy price keywords."""
    for keyword in FUZZY_KEYWORDS:
        if re.search(rf'\b{keyword}\b', query):
            return True
    return False


def _clean_semantic_query(query: str, removal_spans: List[Tuple[int, int]]) -> str:
    """
    Remove numeric constraints from query while preserving semantic meaning.
    
    Args:
        query: Original query
        removal_spans: List of (start, end) tuples to remove
        
    Returns:
        Cleaned semantic query
    """
    if not removal_spans:
        return query.strip()
    
    # Sort spans in reverse order to remove from end to start
    removal_spans.sort(reverse=True)
    
    result = query
    for start, end in removal_spans:
        result = result[:start] + result[end:]
    
    # Clean up extra whitespace
    result = re.sub(r'\s+', ' ', result)
    result = result.strip()
    
    # If query is empty after removal, use a generic term
    if not result:
        result = "products"
    
    return result
