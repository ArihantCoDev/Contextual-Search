# AI-Powered Contextual Search Platform

## Table of Contents
1. [Problem Statement](#1-problem-statement)
2. [System Overview](#2-system-overview)
3. [System Design](#3-system-design)
4. [Data Flow](#4-data-flow)
5. [AI Usage](#5-ai-usage)
6. [Learning Logic](#6-learning-logic)
7. [Architecture Diagram](#7-architecture-diagram)
8. [Functional Requirements Implementation](#8-functional-requirements-implementation)
9. [Non-Functional Requirements](#9-non-functional-requirements)
10. [Project Structure](#10-project-structure)
11. [Setup & Execution](#11-setup--execution)
12. [Evaluation Criteria Alignment](#12-evaluation-criteria-alignment)
13. [Deliverables](#13-deliverables)
14. [Bonus Features](#14-bonus-features)

---

## 1. Problem Statement

Traditional keyword-based search systems struggle to understand user intent, context, and behavioral signals. Users often express needs in natural language with multiple constraints such as price, quality, category, and preferences, which keyword search fails to interpret correctly.

This project designs and implements a **contextual search platform** for a product catalog that:

- ✅ Understands natural language queries
- ✅ Retrieves products based on semantic relevance
- ✅ Continuously learns from user behavior
- ✅ Improves ranking quality over time

The solution is **production-oriented**, focusing on backend engineering, data pipelines, AI-assisted reasoning, and system architecture rather than UI polish.

---

## 2. System Overview

The system supports the following core capabilities:

1. **Product ingestion and indexing**
2. **Semantic (context-aware) search**
3. **Behavioral event tracking**
4. **Learning-based ranking improvements**
5. **Explainable AI-assisted search results**

The architecture is modular, layered, and designed to scale with increasing data and traffic.

---

## 3. System Design

### 3.1 Design Philosophy

The system is built on the following architectural principles:

#### **Layered Architecture**
```
┌─────────────────────────┐
│   API Layer (FastAPI)   │  ← Request handling, validation
├─────────────────────────┤
│   Service Layer         │  ← Business logic, orchestration
├─────────────────────────┤
│   NLP/AI Layer          │  ← Intent extraction, embeddings
├─────────────────────────┤
│   Data Layer            │  ← Storage, retrieval, indexing
└─────────────────────────┘
```

#### **Separation of Concerns**
- **API Layer**: Handles HTTP routing, request validation, response formatting
- **Service Layer**: Orchestrates business logic (search, ranking, learning)
- **NLP Layer**: Extracts intent and constraints from natural language
- **AI Layer**: Generates embeddings and explanations
- **Data Layer**: Manages persistence, vector indexing, and retrieval

#### **Key Design Decisions**

| Decision | Rationale |
|----------|-----------|
| **FastAPI for API** | Async support, automatic OpenAPI docs, type validation |
| **SQLite for metadata** | Lightweight, serverless, sufficient for MVP scale |
| **FAISS for vector search** | Fast, scalable, supports semantic similarity |
| **Sentence Transformers** | Pre-trained embeddings, no custom training needed |
| **Asyncio for events** | Non-blocking event ingestion, prevents API slowdown |
| **Heuristic learning** | Transparent, explainable, no black-box models |

### 3.2 Component Architecture

```
┌──────────────────────────────────────────────────────┐
│                     FastAPI Layer                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  /search    │  │  /ingest    │  │  /events    │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │
└─────────┼─────────────────┼─────────────────┼─────────┘
          │                 │                 │
┌─────────┼─────────────────┼─────────────────┼─────────┐
│         ▼                 ▼                 ▼         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Search    │  │  Ingestion  │  │   Events    │  │
│  │   Service   │  │   Service   │  │   Service   │  │
│  └──────┬──────┘  └──────┬──────┘  └─────────────┘  │
│         │                 │                           │
│         │                 │                           │
│  ┌──────▼──────┐  ┌───────▼──────┐                   │
│  │   Intent    │  │   Embedding  │                   │
│  │  Extractor  │  │   Service    │                   │
│  └──────┬──────┘  └───────┬──────┘                   │
└─────────┼──────────────────┼───────────────────────────┘
          │                  │
┌─────────┼──────────────────┼───────────────────────────┐
│         ▼                  ▼                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   SQLite    │  │    FAISS    │  │   Events    │   │
│  │  (Product   │  │   (Vector   │  │  (Behavior  │   │
│  │  Metadata)  │  │   Index)    │  │   Tracking) │   │
│  └─────────────┘  └─────────────┘  └─────────────┘   │
└───────────────────────────────────────────────────────┘
```

### 3.3 Scalability Considerations

| Component | Current Implementation | Future Scaling Strategy |
|-----------|------------------------|-------------------------|
| **Product Storage** | SQLite | Migrate to PostgreSQL with read replicas |
| **Vector Index** | FAISS (in-memory) | Redis + FAISS or Pinecone/Weaviate |
| **Event Pipeline** | Asyncio Queue | Kafka/RabbitMQ with consumer groups |
| **Search Service** | Single instance | Horizontal scaling behind load balancer |
| **Embedding Generation** | On-demand | Batch processing + caching layer |

### 3.4 Error Handling & Safety

The system implements comprehensive error handling:

- **Graceful degradation**: Empty results return structured responses
- **Input validation**: Pydantic models enforce type safety
- **Logging**: Structured logs for all failures
- **No crashes**: API never crashes on invalid input or empty data

---

## 4. Data Flow

### 4.1 Product Ingestion Flow

```
CSV/JSON File
     │
     ├─► Parse & Normalize
     │        │
     │        ├─► Extract metadata (title, price, category, etc.)
     │        │
     │        ├─► Generate embedding
     │        │        │
     │        │        └─► Sentence Transformer
     │        │                 │
     │        │                 └─► 384-dim vector
     │        │
     │        ├─► Store metadata
     │        │        │
     │        │        └─► SQLite (products table)
     │        │
     │        └─► Store vector
     │                 │
     │                 └─► FAISS index
     │
     └─► Success Response
```

**Ingestion Pipeline Steps:**

1. **Input Validation**: Check CSV/JSON format, required fields
2. **Normalization**: Convert to standard schema
3. **Text Preparation**: Combine title + description for embedding
4. **Embedding Generation**: Use `all-MiniLM-L6-v2` model
5. **Dual Storage**:
   - Metadata → SQLite for filtering
   - Embeddings → FAISS for similarity search
6. **Index Building**: Update FAISS index incrementally

### 4.2 Search Query Flow

```
User Query: "Running shoes under ₹5000 with rating above 4"
     │
     ├─► Intent Extractor (NLP)
     │        │
     │        ├─► Extract constraints:
     │        │    - price_max: 5000
     │        │    - rating_min: 4.0
     │        │    - category: "shoes"
     │        │
     │        └─► Clean query: "running shoes"
     │
     ├─► Merge with UI filters (if any)
     │        │
     │        └─► UI filters ALWAYS override NLP
     │
     ├─► Generate query embedding
     │        │
     │        └─► [0.123, -0.456, ...] (384-dim)
     │
     ├─► Vector Similarity Search (FAISS)
     │        │
     │        └─► Top 100 candidates by semantic relevance
     │
     ├─► Filter by constraints (SQLite)
     │        │
     │        ├─► Price range check
     │        ├─► Rating threshold
     │        ├─► Category match
     │        └─► Brand/attributes
     │
     ├─► Apply learning-based ranking
     │        │
     │        └─► Boost frequently clicked products
     │
     ├─► Generate AI explanations
     │        │
     │        └─► "Matched your query for running shoes, 
     │             under ₹5000, rating 4.5/5"
     │
     └─► Return top 10 results
```

**Search Flow Details:**

1. **NLP Intent Extraction**: Extract structured constraints from natural language
2. **Filter Merging**: Combine NLP + UI filters (UI has priority)
3. **Embedding Generation**: Convert query to 384-dim vector
4. **Semantic Retrieval**: FAISS returns top candidates by cosine similarity
5. **Constraint Filtering**: Apply price, rating, category filters
6. **Learning-Based Ranking**: Boost products with high engagement
7. **Explanation Generation**: AI generates human-readable justification
8. **Response Formation**: Return sorted, explained results

### 4.3 Event Tracking Flow

```
User Action (click/search/cart/purchase)
     │
     ├─► Event capture at frontend
     │
     ├─► POST /api/events
     │        │
     │        └─► Async Queue (non-blocking)
     │
     └─► Background Worker
              │
              ├─► Extract event metadata:
              │    - event_type
              │    - product_id
              │    - query
              │    - timestamp
              │
              ├─► Store in SQLite (events table)
              │
              └─► Update learning signals
                   │
                   └─► Increment product engagement score
```

**Event Types Tracked:**

- `search`: Query submission
- `click`: Product view
- `add_to_cart`: Cart addition
- `purchase`: Transaction completion

**Key Properties:**
- **Asynchronous**: No impact on search latency
- **Non-blocking**: Uses asyncio queue
- **Persistent**: Events stored for analytics and learning

### 4.4 Learning Feedback Loop

```
User Search → Results Displayed
     │              │
     │              ├─► User clicks Product A
     │              │         │
     │              │         └─► Event logged
     │              │
     │              └─► Next search with similar query
     │                        │
     │                        └─► Product A ranked higher
     │
     └─► Continuous improvement
```

---

## 5. AI Usage

### 5.1 Embedding Model

**Model**: `sentence-transformers/all-MiniLM-L6-v2`

**Specifications:**
- **Type**: Sentence embedding model
- **Dimensions**: 384
- **Training**: Pre-trained on 1B+ sentence pairs
- **Purpose**: Convert text to dense vectors for semantic similarity

**Usage in System:**

1. **Product Indexing**:
   ```python
   text = f"{product_title} {product_description}"
   embedding = model.encode(text)  # → 384-dim vector
   faiss_index.add(embedding)
   ```

2. **Query Embedding**:
   ```python
   query_embedding = model.encode(cleaned_query)
   results = faiss_index.search(query_embedding, k=100)
   ```

**Why This Model?**
- ✅ Lightweight (22M parameters)
- ✅ Fast inference (~5ms per query)
- ✅ Good semantic understanding
- ✅ No fine-tuning required

### 5.2 Intent Extraction (NLP)

**Approach**: Rule-based NLP with pattern matching

**Extracted Constraints:**

| Constraint | Example Query | Extracted |
|------------|--------------|-----------|
| **Price upper** | "under ₹5000" | `price_max: 5000` |
| **Price lower** | "above ₹2000" | `price_min: 2000` |
| **Price range** | "between ₹1000 and ₹3000" | `price_min: 1000, price_max: 3000` |
| **Approximate price** | "around ₹5000" | `price_max: 6000, fuzzy_price: true` |
| **Rating** | "rating above 4" | `rating_min: 4.0` |
| **Category** | "laptop" | `category: "Laptops"` |
| **Brand** | "Nike shoes" | `brand: "Nike"` |
| **Attributes** | "black leather bag" | `attributes: ["black", "leather"]` |

**NLP Pipeline:**

1. **Tokenization**: Split query into words
2. **Pattern Matching**: Detect price/rating patterns
3. **Entity Recognition**: Identify brands, categories
4. **Constraint Extraction**: Build structured filters
5. **Conflict Detection**: Flag contradictory constraints
6. **Query Cleaning**: Remove constraint keywords

**Example:**
```
Input: "Running shoes under ₹5000 with rating above 4"

Output:
{
  "cleaned_query": "running shoes",
  "constraints": {
    "price_max": 5000,
    "rating_min": 4.0,
    "category": "Footwear",
    "fuzzy_price": false,
    "conflict": false
  }
}
```

### 5.3 AI-Generated Explanations

**Purpose**: Provide transparent, human-readable rationale for search results

**Explanation Components:**

1. **Semantic Match**: "Matched your query for running shoes"
2. **Constraint Satisfaction**: "Under ₹5000, rating 4.5/5"
3. **Ranking Factors**: "Popular for this search"
4. **Relevance Score**: "95% similarity to your query"

**Generation Logic:**

```python
def generate_explanation(product, query, filters, similarity, engagement):
    parts = []
    
    # Semantic match
    parts.append(f"Matched your query for '{query}'")
    
    # Constraints satisfied
    if filters.price_max:
        parts.append(f"Under ₹{filters.price_max}")
    if filters.rating_min:
        parts.append(f"Rating {product.rating}/5")
    
    # Engagement signal
    if engagement > 0.7:
        parts.append("Frequently chosen for this search")
    
    # Similarity score
    parts.append(f"{int(similarity*100)}% relevance")
    
    return ", ".join(parts)
```

**Example Explanations:**

- "Matched your query for 'gaming laptop', under ₹50000, rating 4.5/5, 92% relevance"
- "Matched your query for 'wireless headphones', under ₹3000, frequently chosen for this search, 88% relevance"

**Key Properties:**
- ✅ **Transparent**: Shows which factors influenced ranking
- ✅ **Accurate**: Only mentions used signals
- ✅ **Consistent**: Generated from actual ranking logic
- ✅ **Explainable**: Users understand why they see results

### 5.4 AI Integration Summary

| AI Component | Technology | Purpose | Output |
|--------------|-----------|---------|--------|
| **Embeddings** | Sentence Transformers | Semantic similarity | 384-dim vectors |
| **Intent Extraction** | Rule-based NLP | Constraint extraction | Structured filters |
| **Explanations** | Template-based AI | Result justification | Human-readable text |

---

## 6. Learning Logic

### 6.1 Learning Philosophy

The system uses **heuristic-based learning** rather than complex machine learning models:

**Why Heuristics?**
- ✅ **Transparent**: Easy to understand and debug
- ✅ **Explainable**: Clear cause-effect relationships
- ✅ **Fast**: No model training required
- ✅ **Production-ready**: Works from day one
- ✅ **Controllable**: Can be tuned manually

### 6.2 Behavioral Signals

**Tracked Events:**

| Event Type | Weight | Signal Strength |
|------------|--------|-----------------|
| **Search** | 0.1 | Low (intent expression) |
| **Click** | 1.0 | Medium (interest) |
| **Add to Cart** | 3.0 | High (purchase intent) |
| **Purchase** | 10.0 | Very High (conversion) |

**Event Schema:**
```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    event_type TEXT,       -- 'search', 'click', 'cart', 'purchase'
    product_id TEXT,       -- Product involved (if applicable)
    query TEXT,            -- Search query (for search/click events)
    timestamp DATETIME,    -- Event time
    session_id TEXT        -- User session identifier
)
```

### 6.3 Click-Through Rate (CTR) Learning

**Engagement Score Calculation:**

```python
def calculate_engagement_score(product_id, query):
    # Count events for this product + query pair
    searches = count_events(query, event_type='search')
    clicks = count_events(query, product_id, event_type='click')
    carts = count_events(query, product_id, event_type='cart')
    purchases = count_events(query, product_id, event_type='purchase')
    
    # Weighted engagement score
    engagement = (
        clicks * 1.0 +
        carts * 3.0 +
        purchases * 10.0
    )
    
    # Normalize by search volume
    if searches > 0:
        ctr = engagement / searches
    else:
        ctr = 0.0
    
    return ctr
```

**Ranking Adjustment:**

```python
def apply_learning_boost(results, query):
    for result in results:
        # Get historical engagement
        engagement = calculate_engagement_score(result.product_id, query)
        
        # Boost similarity score based on engagement
        boost_factor = 1.0 + (engagement * 0.3)  # Up to 30% boost
        
        result.final_score = result.similarity_score * boost_factor
    
    # Re-sort by final score
    return sorted(results, key=lambda x: x.final_score, reverse=True)
```

### 6.4 Learning Examples

**Scenario 1: Popular Product Emerges**

```
Day 1:
  Query: "wireless headphones"
  Results: [A, B, C, D, E]
  User clicks: B (10 times), A (5 times)

Day 2:
  Query: "wireless headphones"
  Original ranking: [A, B, C, D, E]
  After learning: [B, A, C, D, E]  ← B boosted due to high CTR
```

**Scenario 2: Seasonal Trends**

```
Winter Season:
  Query: "jacket"
  Frequent clicks: Winter jackets (boosted)

Summer Season:
  Query: "jacket"
  Clicks decrease for winter items
  System gradually de-prioritizes them
```

### 6.5 Learning Decay & Freshness

**Time-Based Decay:**
```python
def apply_time_decay(engagement_score, event_timestamp):
    days_old = (now() - event_timestamp).days
    decay_factor = 0.95 ** (days_old / 30)  # 5% decay per month
    return engagement_score * decay_factor
```

**Benefits:**
- Recent behavior weighs more heavily
- Prevents stale patterns from dominating
- Adapts to changing user preferences

### 6.6 Cold Start Handling

**For New Products:**

1. **Initial Ranking**: Use semantic similarity only
2. **Exploration Boost**: Randomly promote some new items (10% chance)
3. **Fast Learning**: Higher weight to early engagement signals
4. **Fallback**: If no engagement, rely on category popularity

**For Rare Queries:**

1. **Query Generalization**: Use category-level engagement
2. **Semantic Fallback**: Rely on embedding similarity
3. **Similar Query Learning**: Apply signals from related queries

### 6.7 Learning Metrics

**Tracked Metrics:**

| Metric | Description | Target |
|--------|-------------|--------|
| **CTR** | Click / Search ratio | > 30% |
| **Add-to-Cart Rate** | Cart / Click ratio | > 15% |
| **Conversion Rate** | Purchase / Click ratio | > 5% |
| **Avg. Similarity** | Mean relevance score | > 0.75 |
| **Engagement Growth** | Week-over-week CTR improvement | +5% |

### 6.8 Learning Flow Diagram

```
┌────────────────────────────────────────┐
│         User searches "laptop"         │
└──────────────┬─────────────────────────┘
               │
               ├─► Semantic Search → [A, B, C, D, E]
               │
               ├─► Load engagement scores:
               │    A: 0.5, B: 0.8, C: 0.2, D: 0.1, E: 0.0
               │
               ├─► Apply learning boost:
               │    A: 0.85 → 0.98
               │    B: 0.90 → 1.14  ← Highest boost
               │    C: 0.80 → 0.86
               │    D: 0.75 → 0.78
               │    E: 0.70 → 0.70
               │
               ├─► Re-rank: [B, A, C, D, E]
               │
               └─► User clicks B → Event logged
                              │
                              └─► B's engagement score increases
                                        │
                                        └─► Future searches boost B more
```

### 6.9 Learning Summary

**Learning Approach:**
- **Heuristic-based**: Weighted engagement scoring
- **Signal Types**: Search, click, cart, purchase
- **Ranking Method**: Similarity score boosting
- **Time Awareness**: Decay for old signals
- **Cold Start**: Exploration + fallback strategies

**Key Advantages:**
- ✅ **Explainable**: Clear ranking factors
- ✅ **Fast**: No model training latency
- ✅ **Adaptive**: Responds to user behavior
- ✅ **Production-ready**: Works immediately
- ✅ **Controllable**: Tunable heuristics

---

## 7. Architecture Diagram

### High-Level Architecture

```
┌───────────────────────────────────────────────────────┐
│                 React Frontend                        │
│          (Search UI + Filters + Results)              │
└────────────────────┬──────────────────────────────────┘
                     │ HTTP/JSON
                     ▼
┌───────────────────────────────────────────────────────┐
│               FastAPI Backend                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  /search    │  │  /ingest    │  │  /events    │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │
└─────────┼─────────────────┼─────────────────┼─────────┘
          │                 │                 │
┌─────────┼─────────────────┼─────────────────┼─────────┐
│         ▼                 ▼                 ▼         │
│  ┌──────────────────────────────────────────────┐    │
│  │         Intent Extraction Layer              │    │
│  │    (NLP-based Query Understanding)           │    │
│  └──────────────────┬───────────────────────────┘    │
│                     ▼                                 │
│  ┌──────────────────────────────────────────────┐    │
│  │      Contextual Search Engine                │    │
│  │  - Semantic Retrieval (FAISS)                │    │
│  │  - Structured Filtering (SQLite)             │    │
│  │  - Learning-Based Ranking                    │    │
│  │  - AI Explanation Generation                 │    │
│  └──────────────────┬───────────────────────────┘    │
└─────────────────────┼──────────────────────────────────┘
                      │
┌─────────────────────┼──────────────────────────────────┐
│                     ▼                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   SQLite    │  │    FAISS    │  │   Events    │   │
│  │  (Product   │  │   (Vector   │  │  (Behavior  │   │
│  │  Metadata)  │  │   Index)    │  │   Logs)     │   │
│  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │    Async Behavior Event Pipeline             │    │
│  │  - Click / Search / Cart / Purchase          │    │
│  │  - Non-blocking Queue Processing             │    │
│  │  - Learning Signal Extraction                │    │
│  └──────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────┘
```

### Architectural Principles

1. **Clear separation of concerns**: Each layer has a single responsibility
2. **Deterministic intent extraction**: Transparent NLP-based parsing
3. **Asynchronous event handling**: Non-blocking behavior tracking
4. **Explainability over black-box**: Human-readable AI reasoning
5. **Scalable data layers**: Independent scaling of metadata and vectors

---

## 8. Functional Requirements Implementation

### 8.1 Product Ingestion Pipeline

The system includes a reusable ingestion pipeline that:

- ✅ Accepts CSV or JSON product datasets
- ✅ Normalizes fields:
  - Title, Description, Category
  - Attributes (brand, size, color, material, etc.)
  - Price, Rating
- ✅ Generates vector embeddings for searchable text
- ✅ Stores data in:
  - **SQLite**: Structured metadata
  - **FAISS**: Vector embeddings
- ✅ Reusable with new datasets (no hardcoding)

**API Endpoint:**
```
POST /api/ingest
Content-Type: application/json

{
  "products": [
    {
      "id": "prod_123",
      "title": "Running Shoes",
      "description": "Lightweight athletic shoes",
      "price": 4999,
      "rating": 4.5,
      "category": "Footwear",
      "brand": "Nike",
      "attributes": {"color": "black", "size": "10"}
    }
  ]
}
```

### 8.2 Contextual Search Engine

The search engine supports:

- ✅ **Natural language queries**:
  - "Running shoes under ₹5000 with rating above 4"
  - "Lightweight laptop for coding and gaming"
- ✅ **Query embedding and semantic similarity search**
- ✅ **Structured filtering**:
  - Price range
  - Category
  - Rating
  - Brand and attributes
- ✅ **Ranked and relevant product results**

**API Endpoint:**
```
POST /api/search
Content-Type: application/json

{
  "query": "wireless headphones under ₹3000",
  "filters": {
    "price_max": 3000,
    "rating_min": 4.0
  },
  "limit": 10
}
```

### 8.3 User Behavior Tracking & Analytics

The system tracks user interactions:

- ✅ Search queries
- ✅ Product clicks
- ✅ Add-to-cart events
- ✅ Purchases (simulated)
- ✅ Optional dwell time signals

**Key Properties:**
- Events captured asynchronously
- No synchronous logging in request flows
- Events stored for analytics and ranking

**API Endpoint:**
```
POST /api/events
Content-Type: application/json

{
  "event_type": "click",
  "product_id": "prod_123",
  "query": "wireless headphones",
  "session_id": "sess_abc"
}
```

### 8.4 Learning from User Behavior (Mandatory)

The platform demonstrates learning from real usage signals:

- ✅ **Click-based boosting**: Frequently clicked products ranked higher
- ✅ **Penalty for poor performance**: Low-engagement items de-prioritized
- ✅ **Conversion signals**: Purchase events have highest weight
- ✅ **Transparent logic**: Heuristic-based, explainable ranking

### 8.5 AI Integration (Mandatory)

The system implements AI-generated explanations for search results:

- ✅ **Human-readable explanations**:
  - Why the product matched the query
  - Which constraints were applied
  - How relevance was determined
- ✅ **Transparent reasoning**: No black-box decisions
- ✅ **Consistent**: Generated from actual ranking logic

**Example Response:**
```json
{
  "results": [
    {
      "id": "prod_123",
      "title": "Nike Running Shoes",
      "price": 4999,
      "rating": 4.5,
      "similarity_score": 0.92,
      "explanation": "Matched your query for 'running shoes', under ₹5000, rating 4.5/5, frequently chosen for this search, 92% relevance"
    }
  ]
}
```

---

## 9. Non-Functional Requirements

### 9.1 Architecture

- ✅ Modular and maintainable codebase
- ✅ Proper layering: API → Service → NLP/AI → Data
- ✅ Clear ownership of responsibilities per module

### 9.2 Scalability

- ✅ Designed to handle increasing product volume
- ✅ Vector search scales independently from metadata storage
- ✅ Event ingestion is asynchronous and non-blocking

### 9.3 Observability

- ✅ Structured logging across all services
- ✅ Basic metrics observable:
  - Query latency
  - Event ingestion counts
  - Search result quality

**Logging Examples:**
```
[INFO] Search request: query='laptop', filters={'price_max': 50000}, latency=45ms
[INFO] Event logged: type=click, product=prod_123, query='laptop'
[ERROR] Failed to generate embedding for product prod_456: timeout
```

---

## 10. Project Structure

```
contextual-search/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry
│   │
│   ├── api/                    # API layer (routes)
│   │   ├── __init__.py
│   │   ├── search.py           # /search endpoint
│   │   ├── ingestion.py        # /ingest endpoint
│   │   └── events.py           # /events endpoint
│   │
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── search_service.py   # Search orchestration
│   │   ├── ingestion_service.py
│   │   ├── event_service.py
│   │   └── ranking_service.py  # Learning-based ranking
│   │
│   ├── nlp/                    # NLP layer
│   │   ├── __init__.py
│   │   └── intent_extractor.py # Query understanding
│   │
│   ├── ai/                     # AI layer
│   │   ├── __init__.py
│   │   ├── embedding_service.py
│   │   └── explanation_generator.py
│   │
│   ├── data/                   # Data access layer
│   │   ├── __init__.py
│   │   ├── product_repository.py
│   │   ├── vector_repository.py
│   │   └── event_repository.py
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       └── logger.py
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchBar.jsx
│   │   │   ├── FilterPanel.jsx
│   │   │   └── ProductCard.jsx
│   │   ├── pages/
│   │   │   └── SearchPage.jsx
│   │   └── services/
│   │       └── api.js
│   └── package.json
│
├── data/                       # Data storage
│   ├── products.db             # SQLite database
│   ├── vectors.faiss           # FAISS index
│   └── events.db               # Event logs
│
├── sample_products_500.csv     # Sample dataset
├── ingest_data.py              # Ingestion script
├── requirements.txt
└── README.md
```

---

## 11. Setup & Execution

### Prerequisites
- Python 3.12+
- Node.js 18+
- pip, npm

### Backend Setup

```bash
# Navigate to project root
cd contextual-search

# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend server
uvicorn app.main:app --reload
```

**Backend URLs:**
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

**Frontend URL:**
- App: `http://localhost:5173`

### Data Ingestion

```bash
# Ingest sample products
python ingest_data.py
```

---

## 12. Evaluation Criteria Alignment

| Criteria | Weight | Implementation |
|----------|--------|----------------|
| **Search relevance & quality** | 25% | Semantic search + structured filtering + learning-based ranking |
| **Data pipeline design** | 20% | Reusable ingestion pipeline + dual storage (SQLite + FAISS) |
| **Learning from behavior** | 20% | Heuristic CTR-based ranking improvements |
| **Code quality & modularity** | 20% | Layered architecture + separation of concerns |
| **AI integration quality** | 15% | Explainable AI-generated result explanations |

---

## 13. Deliverables

- ✅ Source code repository
- ✅ Architecture diagram (this README)
- ✅ Detailed README (this document)
- ✅ Sample dataset (CSV)
- ⏳ Demo video (optional)

---

## 14. Bonus Features (Future Scope)

- 🔮 Personalized search per user
- 🔮 Query analytics dashboard
- 🔮 Offline batch re-ranking
- 🔮 Multi-language search support
- 🔮 A/B testing framework
- 🔮 Advanced ML models (BERT, transformers)

---

## Conclusion

This project demonstrates a **production-oriented contextual search system** that integrates:

1. **Semantic Understanding**: Vector embeddings for meaning-based retrieval
2. **Structured Filtering**: Precise constraint satisfaction
3. **Behavioral Learning**: Heuristic-based ranking improvements
4. **Explainable AI**: Transparent result justifications

The emphasis is on **system design, correctness, and clarity of reasoning** rather than surface-level UI completeness. The architecture is modular, scalable, and production-ready.

---

**For questions or contributions, please open an issue or submit a pull request.**