# TidyLLM Refactoring Tables

## 1. Document Processing Components

| Item | Before (Current Location) | After (Target Location) | Comments |
|------|--------------------------|------------------------|----------|
| VectorQA Core Algorithm | `tidyllm/services/unified_rag_manager.py` | **KEEP** in TidyLLM | Core business logic - the heart of document processing |
| Document Chunking | `tidyllm/rag/chunking.py` | **KEEP** in TidyLLM | Generic algorithm applicable to any document |
| Embedding Generation | `tidyllm/embeddings/generator.py` | **KEEP** in TidyLLM | Core ML functionality, not compliance-specific |
| QA Control Flows | `tidyllm/flow/qa_control_flows.py` | **MOVE** to `compliance-qa/application/workflows/` | Compliance-specific workflow logic |
| MVR Processing | `tidyllm/flow/qa_control_flows.py` | **MOVE** to `compliance-qa/domain/services/` | MVR is compliance domain concept |
| Text Extraction | `tidyllm/core/text_extractor.py` | **KEEP** in TidyLLM | Generic capability for any document type |

## 2. Infrastructure Components

| Item | Before (Current Location) | After (Target Location) | Comments |
|------|--------------------------|------------------------|----------|
| MLflow Integration | `tidyllm/services/enhanced_mlflow_service.py` | **MOVE** to `compliance-qa/infrastructure/mlflow/` | Infrastructure concern, not core logic |
| Database Connections | `tidyllm/db/connection_manager.py` | **MOVE** to `compliance-qa/infrastructure/database/` | Infrastructure layer responsibility |
| AWS Bedrock Config | `tidyllm/admin/aws_settings.yaml` | **MOVE** to `compliance-qa/infrastructure/aws/` | External service integration |
| S3 Storage | `tidyllm/storage/s3_adapter.py` | **MOVE** to `compliance-qa/infrastructure/storage/` | Infrastructure storage concern |
| Session Management | `tidyllm/session/manager.py` | **MOVE** to `compliance-qa/infrastructure/session/` | Application state management |
| Credential Management | `tidyllm/admin/config_manager.py` | **MOVE** to `compliance-qa/infrastructure/config/` | Security/infrastructure concern |

## 3. Portal/UI Components

| Item | Before (Current Location) | After (Target Location) | Comments |
|------|--------------------------|------------------------|----------|
| Setup Portal | `tidyllm/portals/config/setup_portal.py` | **MOVE** to `compliance-qa/portals/setup/` | UI is presentation layer |
| Flow Creator Portal | `tidyllm/portals/flow/flow_creator_v3.py` | **MOVE** to `compliance-qa/portals/flow/` | Application-specific UI |
| RAG Portal | `tidyllm/portals/rag/unified_rag_portal.py` | **MOVE** to `compliance-qa/portals/rag/` | UI should not be in core package |
| Streamlit Web Interface | `tidyllm/interfaces/web.py` | **MOVE** to `compliance-qa/portals/main/` | Presentation layer |
| Portal Tabs (t_*.py) | `tidyllm/portals/flow/t_*.py` | **MOVE** to `compliance-qa/portals/flow/tabs/` | UI components |

## 4. Compliance/Domain Logic

| Item | Before (Current Location) | After (Target Location) | Comments |
|------|--------------------------|------------------------|----------|
| MVS Compliance Rules | `tidyllm/flow/qa_control_flows.py` | **MOVE** to `compliance-qa/domain/rules/mvs_rules.py` | Domain-specific compliance standard |
| VST Compliance Rules | `tidyllm/flow/qa_control_flows.py` | **MOVE** to `compliance-qa/domain/rules/vst_rules.py` | Domain-specific compliance standard |
| Finding Classification | `tidyllm/flow/qa_control_flows.py` | **MOVE** to `compliance-qa/domain/services/finding_classifier.py` | Compliance domain logic |
| Audit Trail Generation | `tidyllm/flow/qa_control_flows.py` | **MOVE** to `compliance-qa/domain/services/audit_service.py` | Compliance requirement |
| QA Checklists | `tidyllm/flow/qa_control_flows.py` | **MOVE** to `compliance-qa/domain/checklists/` | Domain-specific validation |
| SR11-7 Rules | `tidyllm/flow/qa_control_flows.py` | **MOVE** to `compliance-qa/domain/rules/sr11_7_rules.py` | Regulatory requirement |

## 5. Core Algorithms (Stay in TidyLLM)

| Item | Current Purpose | Keep in TidyLLM? | Why Keep |
|------|----------------|-----------------|----------|
| Vector Similarity Search | Finding similar documents | ✅ YES | Mathematical algorithm, not domain-specific |
| Cosine Similarity | Calculate vector similarity | ✅ YES | Pure math, applicable everywhere |
| BM25 Ranking | Document ranking algorithm | ✅ YES | Generic search algorithm |
| Text Tokenization | Breaking text into tokens | ✅ YES | Fundamental NLP operation |
| Sliding Window Chunking | Document chunking strategy | ✅ YES | Generic text processing technique |
| Semantic Chunking | Smart document splitting | ✅ YES | AI/ML algorithm, not compliance-specific |

## 6. Service Layer Refactoring

| Item | Before (Mixed Location) | After (Clean Separation) | Comments |
|------|------------------------|-------------------------|----------|
| `UnifiedRAGManager` | Has both generic + compliance logic | TidyLLM: Generic RAG only | Remove compliance-specific methods |
| `DocumentProcessor` | Mixed processing + compliance | Split into two classes | TidyLLM: generic, Compliance-QA: domain |
| `QAControlFlowManager` | All in TidyLLM | **ENTIRELY MOVE** to compliance-qa | 100% compliance-specific |
| `SimpleQAProcessor` | In TidyLLM | Evaluate each method | Keep generic, move specific |
| `DualAIABTesting` | In TidyLLM optimization | **MOVE** if QA-specific | A/B testing for compliance scenarios |

## 7. Example Code Transformations

### Before (Mixed Concerns in TidyLLM):
```python
# tidyllm/services/document_processor.py
class DocumentProcessor:
    def process_document(self, doc):
        # Generic processing ✅
        chunks = self.chunk_document(doc)
        embeddings = self.generate_embeddings(chunks)

        # Compliance-specific ❌
        mvr_check = self.check_mvr_compliance(doc)
        vst_validation = self.validate_vst_requirements(doc)

        return ProcessResult(chunks, embeddings, mvr_check, vst_validation)
```

### After (Clean Separation):

**TidyLLM (Generic Only):**
```python
# tidyllm/services/document_processor.py
class DocumentProcessor:
    def process_document(self, doc):
        # Only generic processing
        chunks = self.chunk_document(doc)
        embeddings = self.generate_embeddings(chunks)
        return ProcessResult(chunks, embeddings)
```

**Compliance-QA (Uses TidyLLM + Adds Domain):**
```python
# compliance-qa/domain/services/compliance_document_processor.py
from tidyllm.services.document_processor import DocumentProcessor

class ComplianceDocumentProcessor:
    def __init__(self):
        self.processor = DocumentProcessor()  # Use TidyLLM

    def process_for_compliance(self, doc):
        # Use generic processing
        result = self.processor.process_document(doc)

        # Add compliance-specific logic
        mvr_check = self.check_mvr_compliance(result.chunks)
        vst_validation = self.validate_vst_requirements(result.chunks)

        return ComplianceResult(result, mvr_check, vst_validation)
```

## 8. Package Dependencies After Refactoring

| Package | Depends On | Should NOT Depend On | Clean? |
|---------|-----------|---------------------|--------|
| TidyLLM | numpy, pandas, transformers | compliance-qa, mlflow, boto3 | ✅ |
| Compliance-QA | tidyllm, mlflow, boto3, psycopg2 | (none - top level app) | ✅ |
| Infrastructure | boto3, psycopg2, mlflow | tidyllm (only compliance-qa) | ✅ |

## 9. File Movement Summary

### Files to DELETE from TidyLLM:
- All portal UI files (`portals/` directory)
- MLflow integration files
- Database connection files
- AWS configuration files
- Compliance-specific workflows

### Files to KEEP in TidyLLM:
- Core RAG algorithms
- Vector operations
- Text processing utilities
- Document chunking strategies
- Embedding generation

### Files to CREATE in Compliance-QA:
- Domain models for MVR, Findings, Compliance
- Service layer wrapping TidyLLM
- Infrastructure adapters
- Lean Streamlit portals
- Compliance rule engines

## 10. Testing Strategy After Separation

| Component | Test Type | Location | Focus |
|-----------|-----------|----------|-------|
| TidyLLM algorithms | Unit tests | `tidyllm/tests/unit/` | Algorithm correctness |
| TidyLLM integration | Integration tests | `tidyllm/tests/integration/` | Component interaction |
| Compliance rules | Unit tests | `compliance-qa/tests/unit/domain/` | Rule validation |
| Compliance workflows | Integration tests | `compliance-qa/tests/integration/` | End-to-end workflow |
| Infrastructure | Integration tests | `compliance-qa/tests/integration/infra/` | External service connectivity |
| Portals | UI tests | `compliance-qa/tests/ui/` | User interaction flows |

## Summary Benefits

| Aspect | Before (Mixed) | After (Separated) | Benefit |
|--------|---------------|-------------------|---------|
| **Reusability** | TidyLLM tied to compliance | TidyLLM usable for any document processing | Can use TidyLLM in other projects |
| **Testing** | Hard to test in isolation | Clear test boundaries | Faster, more focused tests |
| **Deployment** | Must deploy everything | Can deploy separately | Flexible deployment options |
| **Maintenance** | Changes affect everything | Isolated changes | Less risk, easier updates |
| **Team Work** | Everyone touches same code | Clear ownership boundaries | Teams can work independently |
| **Dependencies** | Heavy dependencies everywhere | Minimal core dependencies | Lighter, faster installation |