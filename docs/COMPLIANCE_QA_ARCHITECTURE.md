# Compliance-QA Architecture

## Overview
Compliance-QA is an **application layer** that uses TidyLLM's core capabilities for compliance-specific workflows.

## Architecture Relationship

```
┌─────────────────────────────────────┐
│  Compliance-QA (Application Layer)  │
│  - QA Workflows                     │
│  - Compliance Rules                 │
│  - MVR Processing Logic             │
│  - Finding Classification           │
└──────────────┬──────────────────────┘
               │ uses
               ▼
┌─────────────────────────────────────┐
│   TidyLLM (Core Business Logic)     │
│  - VectorQA Document Processing     │
│  - Document Extraction & Chunking   │
│  - Embedding Generation              │
│  - Vector Operations                 │
│  - RAG Algorithms                    │
│  - Document Analysis                 │
└──────────────┬──────────────────────┘
               │ uses
               ▼
┌─────────────────────────────────────┐
│  QA-Compliance Infrastructure       │
│  - MLflow Tracking                  │
│  - Database Connections             │
│  - AWS Bedrock Integration          │
│  - S3 Storage                       │
│  - Session Management               │
│  - Environment Configuration        │
└─────────────────────────────────────┘
```

## What Belongs Where

### In Compliance-QA (This Repository)

**Application Layer (Domain-Specific):**
- QA control flows for compliance workflows
- MVR (Model Validation Report) processing rules
- Compliance checking against MVS/VST standards
- Finding classification and severity rules
- Audit trail generation logic
- QA checklist definitions
- A/B testing strategies for compliance use cases

**Infrastructure Layer:**
- MLflow tracking and experiments
- PostgreSQL database connections
- AWS Bedrock integration
- S3 storage adapters
- Session management
- Environment configuration
- Credential management

### In TidyLLM (Core Package)
**Pure Business Logic (Domain-Agnostic):**
- VectorQA document processing algorithms
- Document extraction and chunking logic
- Embedding generation algorithms
- Vector similarity operations
- RAG (Retrieval Augmented Generation) logic
- Document analysis algorithms
- Text processing utilities

## Directory Structure

```
compliance-qa/
├── application/           # Application Layer
│   ├── workflows/        # Compliance-specific workflows
│   │   ├── qa_control_flows.py
│   │   └── mvr_processing.py
│   └── use_cases/        # Business use cases
│       ├── check_compliance.py
│       └── classify_findings.py
│
├── domain/               # Domain Layer (Compliance-specific)
│   ├── models/          # Domain models
│   │   ├── mvr.py
│   │   ├── finding.py
│   │   └── compliance_check.py
│   └── rules/           # Business rules
│       ├── mvs_rules.py
│       └── vst_rules.py
│
├── infrastructure/       # Infrastructure Layer (Already exists!)
│   ├── environment_manager.py    # Environment configuration
│   ├── credential_validator.py   # Credential management
│   ├── session/                  # Session management
│   ├── services/                 # External services
│   │   ├── enhanced_mlflow_service.py
│   │   └── credential_carrier.py
│   └── adapters/                 # Adapters for external systems
│
├── adapters/            # Hexagonal Architecture Adapters
│   ├── primary/         # Inbound adapters (CLI, Web, etc.)
│   └── secondary/       # Outbound adapters (Database, AWS, etc.)
│
├── packages/            # Core Business Logic Packages
│   ├── tidyllm/        # Document processing, RAG, etc.
│   ├── tlm/            # Additional logic
│   └── tidyllm-sentence/ # Sentence processing
│
└── examples/            # Working examples
    ├── process_mvr_document.py
    ├── run_compliance_check.py
    └── test_ab_optimization.py
```

## Using TidyLLM in Compliance-QA

### Example 1: Document Processing
```python
# Import TidyLLM's document processing
from tidyllm.knowledge_systems.facades.document_processor import DocumentProcessor

# Use it for compliance documents
processor = DocumentProcessor(chunk_size=1000)
chunks = processor.process_document("mvr_report.pdf")
```

### Example 2: AI Model Integration
```python
# Import TidyLLM's AI capabilities
from tidyllm.services.bedrock_service import BedrockService

# Use for compliance analysis
ai_service = BedrockService()
analysis = ai_service.analyze(document_content, compliance_rules)
```

### Example 3: Vector Storage for Compliance
```python
# Import TidyLLM's vector capabilities
from tidyllm.knowledge_systems.facades.vector_storage import VectorStorage

# Store compliance documents
storage = VectorStorage()
storage.add_documents(compliance_docs, metadata={"type": "mvr"})
results = storage.search("finding related to data quality")
```

## Key Principles

1. **Separation of Concerns**
   - TidyLLM handles technical/infrastructure concerns
   - Compliance-QA handles business/domain concerns

2. **Don't Duplicate**
   - Use TidyLLM's document processing, don't recreate it
   - Use TidyLLM's AI integration, don't rebuild it
   - Use TidyLLM's vector storage, don't reimplement it

3. **Domain Focus**
   - Compliance-QA should focus on compliance rules and workflows
   - Let TidyLLM handle the technical heavy lifting

4. **Clean Dependencies**
   - Compliance-QA depends on TidyLLM
   - TidyLLM never depends on Compliance-QA

## Migration Path

1. Keep QA control flows in compliance-qa (domain-specific)
2. Remove duplicate document processing (use TidyLLM's)
3. Keep compliance rules and workflows (domain-specific)
4. Use TidyLLM for all technical infrastructure needs