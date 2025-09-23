# TidyLLM Separation Guide

## Overview
This guide clarifies what functionality belongs in TidyLLM (core business logic package) versus Compliance-QA (application layer).

## Core Principle
**TidyLLM = Pure business logic, algorithms, and document processing**
**Compliance-QA = Application-specific workflows, infrastructure, and compliance rules**

## Feature Separation Table

| Feature/Component | Stay in TidyLLM | Move to Compliance-QA | Reason |
|-------------------|-----------------|----------------------|---------|
| **VectorQA Core** | ✅ | ❌ | Core document processing algorithm |
| **Document Chunking** | ✅ | ❌ | Generic text processing capability |
| **Embedding Generation** | ✅ | ❌ | Core ML/AI functionality |
| **RAG Algorithms** | ✅ | ❌ | Generic retrieval-augmented generation |
| **Text Extraction** | ✅ | ❌ | Universal document processing |
| **Vector Operations** | ✅ | ❌ | Mathematical operations on vectors |
| **Similarity Search** | ✅ | ❌ | Core search algorithms |
| **Document Analysis** | ✅ | ❌ | Generic analysis capabilities |
| **UnifiedRAGManager** | ✅ | ❌ | Core RAG orchestration |
| **Text Processing Utils** | ✅ | ❌ | Generic text manipulation |
| **DSPy Integration** | ✅ | ❌ | Core ML framework integration |
| **LLM Abstractions** | ✅ | ❌ | Generic LLM interfaces |
| | | | |
| **QA Control Flows** | ❌ | ✅ | Compliance-specific workflows |
| **MVR Processing** | ❌ | ✅ | Domain-specific report handling |
| **Compliance Checking** | ❌ | ✅ | Regulatory-specific validation |
| **MVS/VST Standards** | ❌ | ✅ | Specific compliance standards |
| **Finding Classification** | ❌ | ✅ | Compliance domain logic |
| **Audit Trail Generation** | ❌ | ✅ | Compliance requirement |
| **QA Checklists** | ❌ | ✅ | Domain-specific validation |
| **A/B Testing for QA** | ❌ | ✅ | Application-specific testing |
| **MLflow Integration** | ❌ | ✅ | Infrastructure concern |
| **Database Connections** | ❌ | ✅ | Infrastructure layer |
| **AWS Bedrock Config** | ❌ | ✅ | Infrastructure integration |
| **S3 Storage** | ❌ | ✅ | Infrastructure storage |
| **Session Management** | ❌ | ✅ | Application state |
| **Credential Management** | ❌ | ✅ | Infrastructure security |
| **Portal UI Code** | ❌ | ✅ | Presentation layer |
| **Streamlit Apps** | ❌ | ✅ | UI/Presentation |

## Detailed Component Breakdown

### TidyLLM Package Contents (Pure Business Logic)

#### Core Modules to Keep:
```
tidyllm/
├── core/
│   ├── vector_operations.py      # Mathematical vector ops
│   ├── text_processing.py        # Text manipulation utilities
│   └── document_parser.py        # Generic document parsing
│
├── rag/
│   ├── chunking_strategies.py    # Document chunking algorithms
│   ├── embedding_manager.py      # Embedding generation logic
│   ├── retrieval_engine.py       # RAG retrieval algorithms
│   └── context_builder.py        # Context window management
│
├── services/
│   ├── unified_rag_manager.py    # Core RAG orchestration
│   ├── document_processor.py     # Document processing pipeline
│   └── llm_interface.py          # Generic LLM abstractions
│
├── algorithms/
│   ├── similarity_search.py      # Vector similarity algorithms
│   ├── ranking_algorithms.py     # Result ranking logic
│   └── clustering.py             # Document clustering
│
└── utils/
    ├── text_utils.py              # Text helper functions
    ├── math_utils.py              # Mathematical utilities
    └── validation_utils.py        # Data validation helpers
```

### Compliance-QA Contents (Application & Infrastructure)

#### Application Layer:
```
compliance-qa/
├── application/
│   ├── workflows/
│   │   ├── qa_control_flows.py   # QA-specific workflows
│   │   ├── mvr_processing.py     # MVR document workflows
│   │   └── compliance_flows.py   # Compliance check workflows
│   │
│   └── use_cases/
│       ├── validate_model.py     # Model validation use case
│       ├── check_compliance.py   # Compliance checking
│       └── generate_report.py    # Report generation
│
├── domain/
│   ├── models/
│   │   ├── mvr.py                # MVR domain model
│   │   ├── finding.py            # Finding entity
│   │   └── compliance_result.py  # Compliance result model
│   │
│   ├── rules/
│   │   ├── mvs_rules.py          # MVS standard rules
│   │   ├── vst_rules.py          # VST standard rules
│   │   └── severity_rules.py     # Finding severity logic
│   │
│   └── services/
│       ├── qa_workflow_service.py     # QA workflow orchestration
│       ├── compliance_service.py      # Compliance checking
│       └── document_processor.py      # Wraps TidyLLM for compliance
```

#### Infrastructure Layer:
```
compliance-qa/
├── infrastructure/
│   ├── database/
│   │   ├── connection_pool.py    # DB connection management
│   │   └── repositories/         # Data access layer
│   │
│   ├── external/
│   │   ├── aws_bedrock.py        # AWS Bedrock integration
│   │   ├── s3_storage.py         # S3 file storage
│   │   └── mlflow_tracking.py    # MLflow experiment tracking
│   │
│   ├── config/
│   │   ├── environment_manager.py # Environment configuration
│   │   └── credential_validator.py # Credential management
│   │
│   └── session/
│       └── session_manager.py     # Application session state
```

#### Presentation Layer:
```
compliance-qa/
├── portals/
│   ├── setup/
│   │   └── lean_setup_portal.py  # Setup UI (uses services)
│   │
│   ├── qa/
│   │   └── lean_qa_portal.py     # QA workflows UI
│   │
│   └── common/
│       └── portal_base.py        # Shared portal utilities
```

## Migration Guidelines

### When Moving Code from TidyLLM to Compliance-QA:

1. **Identify Infrastructure Dependencies**
   - Database connections → Move to compliance-qa/infrastructure
   - AWS services → Move to compliance-qa/infrastructure
   - MLflow tracking → Move to compliance-qa/infrastructure

2. **Identify Domain-Specific Logic**
   - Compliance rules → Move to compliance-qa/domain/rules
   - QA workflows → Move to compliance-qa/application/workflows
   - MVR processing → Move to compliance-qa/domain/services

3. **Keep Generic Algorithms**
   - Document chunking algorithms → Keep in TidyLLM
   - Vector operations → Keep in TidyLLM
   - Text processing → Keep in TidyLLM

### When Using TidyLLM from Compliance-QA:

```python
# GOOD: Compliance-QA using TidyLLM's core functionality
from tidyllm.services.unified_rag_manager import UnifiedRAGManager
from tidyllm.core.vector_operations import calculate_similarity

class ComplianceDocumentProcessor:
    def __init__(self):
        # Use TidyLLM's RAG manager
        self.rag_manager = UnifiedRAGManager()

    def process_mvr(self, document):
        # Use TidyLLM for document processing
        chunks = self.rag_manager.process_document(document)

        # Apply compliance-specific rules
        compliance_results = self.check_mvs_compliance(chunks)
        return compliance_results
```

```python
# BAD: TidyLLM depending on compliance-specific logic
# This should NOT be in TidyLLM:
from compliance_qa.domain.rules import mvs_rules  # ❌ Wrong direction!

class DocumentProcessor:
    def process(self, doc):
        # Generic processing
        result = self.extract_text(doc)
        # Don't apply domain-specific rules in TidyLLM!
        mvs_check = mvs_rules.validate(result)  # ❌
```

## Key Principles

1. **TidyLLM is Domain-Agnostic**
   - Should work for ANY document processing need
   - No compliance-specific logic
   - No infrastructure dependencies

2. **Compliance-QA is Domain-Specific**
   - Implements compliance workflows
   - Contains regulatory rules
   - Manages infrastructure

3. **Dependency Direction**
   - Compliance-QA → TidyLLM ✅
   - TidyLLM → Compliance-QA ❌

4. **Testing Strategy**
   - TidyLLM: Unit tests for algorithms
   - Compliance-QA: Integration tests for workflows

## Summary

**TidyLLM** = Think of it as a powerful toolkit for document processing, like NumPy is for numerical computing.

**Compliance-QA** = The application that uses the toolkit to solve specific business problems, like a financial analysis application uses NumPy.

This separation ensures:
- TidyLLM remains reusable for other projects
- Compliance-QA can evolve independently
- Clear boundaries and responsibilities
- Easier testing and maintenance