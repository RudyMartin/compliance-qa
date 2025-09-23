# SME RAG Adapter Architecture & Rationale

## Why SME RAG Adapter?

The SME (Subject Matter Expert) RAG Adapter was created to address specific organizational and knowledge management requirements that other RAG adapters don't handle:

## Problem Statement

In enterprise environments, RAG systems often need to manage knowledge from different domains, expertise levels, and regulatory requirements. Generic RAG adapters treat all documents equally, leading to:

1. **Knowledge Mixing**: Medical documents mixed with financial regulations
2. **Expertise Confusion**: Beginner tutorials returned for expert queries
3. **No Domain Isolation**: Can't query specific knowledge areas
4. **Poor Organization**: Thousands of documents in a flat structure
5. **Compliance Issues**: Can't separate regulated vs non-regulated content

## SME RAG Solution

### Core Differentiators

```
Standard RAG:
Documents → Chunks → Embeddings → Search → Response

SME RAG:
Collections → Documents → Chunks → Embeddings → Filtered Search → Expert Response
     ↓
[Domain-specific, Authority-tiered, Metadata-rich]
```

## Architecture Design

### 1. Collection-Based Architecture

```python
# Traditional RAG - All documents in one pool
rag.add_document("GDPR requirements...")
rag.add_document("Machine learning tutorial...")
rag.add_document("AWS best practices...")
response = rag.query("data retention")  # Could get any of them

# SME RAG - Organized collections
sme.create_collection("gdpr_compliance")
sme.create_collection("ml_tutorials")
sme.create_collection("aws_practices")
sme.add_document("gdpr_compliance", "GDPR requirements...")
response = sme.query(domain="gdpr_compliance", query="data retention")  # Only GDPR
```

### 2. Authority Tier System

**Why Authority Tiers?**
- **Expertise Matching**: Beginners shouldn't get PhD-level responses
- **Credibility Ranking**: Official docs > community posts > opinions
- **Regulatory Compliance**: Some content must come from authoritative sources

```sql
-- SME tables support authority tiers
CREATE TABLE sme_collections (
    collection_id VARCHAR(36),
    authority_tier INTEGER,  -- 1=Basic, 2=Intermediate, 3=Expert, 4=Authoritative
    ...
);
```

### 3. Rich Metadata Support

**Standard RAG Metadata:**
```json
{
    "doc_id": "123",
    "timestamp": "2024-01-01"
}
```

**SME RAG Metadata:**
```json
{
    "doc_id": "123",
    "collection": "sox_compliance",
    "authority_tier": 4,
    "author": "Compliance Team",
    "regulation_version": "2024",
    "jurisdiction": "US",
    "last_reviewed": "2024-01-01",
    "tags": ["financial", "audit", "required"],
    "expertise_level": "professional",
    "source_type": "official_regulation"
}
```

## Use Case Comparison

### Scenario 1: Multi-Domain Knowledge Base

**Without SME RAG:**
- All documents mixed together
- Search returns irrelevant cross-domain results
- No way to scope searches
- Can't manage domains independently

**With SME RAG:**
```python
# Clear domain separation
collections = sme.list_collections()
# ['compliance', 'engineering', 'hr_policies', 'product_specs']

# Domain-scoped operations
sme.add_document("compliance", new_regulation)
sme.search_collection("engineering", "deployment patterns")
stats = sme.get_collection_stats("hr_policies")
```

### Scenario 2: Regulatory Compliance System

**Without SME RAG:**
- Compliance docs mixed with general docs
- Can't verify all regulations are indexed
- No audit trail for what's in the system
- Risk of returning non-authoritative content

**With SME RAG:**
```python
# Dedicated compliance collections
sme.create_collection("sox_2024", description="Sarbanes-Oxley 2024 Requirements")
sme.create_collection("gdpr_official", description="Official GDPR Documentation")

# Trackable compliance coverage
stats = sme.get_collection_stats("sox_2024")
print(f"SOX Coverage: {stats['document_count']} documents, {stats['chunk_count']} chunks")

# Authoritative-only queries
response = sme.query(
    domain="sox_2024",
    query="audit requirements",
    authority_tier=4  # Only official sources
)
```

### Scenario 3: Expertise-Level Documentation

**Without SME RAG:**
- Beginners get overwhelmed with expert content
- Experts get basic tutorials
- No progression path through content

**With SME RAG:**
```python
# Tiered knowledge delivery
beginner = sme.query(
    domain="python_tutorials",
    query="what are decorators",
    authority_tier=1
)
# Returns: "Decorators are a way to modify functions..."

expert = sme.query(
    domain="python_tutorials",
    query="decorator metaclass interactions",
    authority_tier=3
)
# Returns: "When decorators interact with metaclasses, the MRO..."
```

## Database Schema Advantages

### SME-Specific Tables

```sql
-- Collections with rich configuration
CREATE TABLE sme_collections (
    collection_id VARCHAR(36) PRIMARY KEY,
    collection_name VARCHAR(255) UNIQUE,
    description TEXT,
    authority_tier INTEGER,
    settings JSONB,  -- Flexible configuration
    tags TEXT[],     -- PostgreSQL arrays for categorization
    created_at TIMESTAMP
);

-- Document-to-collection relationships
CREATE TABLE sme_documents (
    doc_id VARCHAR(36) PRIMARY KEY,
    collection_id VARCHAR(36) REFERENCES sme_collections,
    content TEXT,
    metadata JSONB,  -- Rich, searchable metadata
    authority_score FLOAT,
    expertise_level VARCHAR(50)
);

-- Chunks maintain collection context
CREATE TABLE sme_document_chunks (
    chunk_id VARCHAR(36) PRIMARY KEY,
    doc_id VARCHAR(36) REFERENCES sme_documents,
    collection_id VARCHAR(36) REFERENCES sme_collections,
    content TEXT,
    metadata JSONB
);
```

## Performance Benefits

1. **Faster Searches**: Collection-scoped searches examine fewer chunks
2. **Better Relevance**: Domain-specific results reduce noise
3. **Efficient Indexing**: Can index collections independently
4. **Scalability**: Collections can be distributed/sharded

## Compliance & Governance Benefits

1. **Audit Trail**: Track what knowledge is in each collection
2. **Access Control**: Can restrict collections by user role
3. **Version Control**: Replace entire collections atomically
4. **Retention Policies**: Apply different retention per collection
5. **Regulatory Isolation**: Keep regulated content separate

## When to Use SME RAG vs Other Adapters

### Use PostgreSQL RAG When:
- Simple document storage needed
- No domain separation required
- Basic RAG functionality sufficient

### Use AI-Powered RAG When:
- Need LLM analysis of content
- Want intelligent summaries
- Quality over organization

### Use Intelligent RAG When:
- Focus on embedding quality
- Need smart chunking
- Single domain knowledge base

### Use SME RAG When:
- **Multiple distinct knowledge domains**
- **Regulatory/compliance requirements**
- **Different expertise levels needed**
- **Collection-level management required**
- **Rich metadata and categorization needed**
- **Audit and governance important**

## Integration with Hexagonal Architecture

The SME RAG Adapter follows hexagonal architecture principles:

```python
class SMERAGAdapter(BaseRAGAdapter):  # Implements port interface
    def __init__(self):
        # Uses infrastructure delegate, not direct DB
        self.infra = get_infra_delegate()

        # Internal domain logic
        self.sme_system = SMERAGSystem()
```

**Port Compliance:**
- Extends `BaseRAGAdapter` interface
- Implements required methods: `query()`, `health_check()`, `get_info()`
- Adds domain-specific methods for collections

**Adapter Pattern:**
- Translates between domain concepts (collections) and infrastructure
- Uses delegate pattern for all infrastructure access
- No direct database imports or connections

## Summary

The SME RAG Adapter provides **organizational intelligence** that other RAG adapters lack. It's not just about retrieving documents - it's about managing knowledge domains, expertise levels, and compliance requirements in a structured, auditable way.

**Key Value Proposition:**
> "Turn your RAG system from a document dump into an organized, multi-domain knowledge management platform with expertise levels, compliance tracking, and collection-based governance."

This makes SME RAG ideal for:
- Enterprise knowledge management
- Regulatory compliance systems
- Multi-tenant SaaS platforms
- Educational platforms with skill levels
- Professional documentation systems
- Domain-specific expert systems