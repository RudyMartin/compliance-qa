# TidyLLM Flow Portal Applications

## Overview

The Flow Portal ecosystem provides comprehensive workflow orchestration and execution capabilities for the TidyLLM platform. These applications facilitate Flow Macros - powerful command sequences that can invoke one or more workflows in structured, auditable processes.

## 🎯 Core Applications

### Chat Workflow Interface (Port 8503)
**File**: `portals/chat/chat_workflow_interface.py`

**Primary Purpose**: Interactive Flow Macro launcher with chat-based workflow execution

**Key Features**:
- **Flow Macros Command System**: Execute complex workflow sequences with single commands
- **Flow Macro Sidebar**: Structured workflow launcher with compliance tracking
- **MVR Analysis Integration**: 4-stage document processing workflow
- **Real-time Execution Monitoring**: Live status updates and progress tracking
- **Audit Trail Integration**: Compliance logging for SR-11-7, SOX-404 requirements

**Flow Macros Examples**:
```
[MVR_ANALYSIS] document.pdf
[COMPLIANCE_CHECK] financial_report.docx
[QUALITY_REVIEW] code_repository/
[MULTI_STAGE] doc1.pdf, doc2.pdf -> mvr_analysis -> peer_review -> compliance_check
```

**Architecture**:
- Chat Interface with Flow Macro sidebar
- Integration with Unified Flow Manager (UFM)
- Automatic RAG system deployment for workflow support
- Real-time status and metrics display

---

## 🔧 Flow Architecture Components

### Unified Flow Manager (UFM)
**File**: `packages/tidyllm/services/unified_flow_manager.py`

**Core Capabilities**:
- **13 Workflow Types**: MVR Analysis, Domain RAG, Financial Analysis, Contract Review, Compliance Check, Quality Check, Peer Review, Data Extraction, Hybrid Analysis, Code Review, Research Synthesis, Classification, Custom Workflows
- **CRUD Operations**: Create, Read, Update, Delete workflows
- **Status Management**: Created → Deployed → Running → Completed/Failed/Paused/Archived
- **RAG Integration**: Automatic deployment of supporting RAG systems
- **Health Monitoring**: System availability and performance tracking

### Flow Macro System
**Implementation**: MVRAnalysisFlow class in chat_workflow_interface.py

**Features**:
- Structured workflow configuration
- Compliance requirement tracking
- Audit trail generation
- Gateway approval management
- Auto-optimization settings

**Configuration Example**:
```python
FlowMacroConfig(
    macro_id="mvr_analysis_v1",
    macro_type="MVR Document Analysis",
    created_by="TidyLLM",
    approved_gateways=["dspy", "llm"],
    audit_requirements=["tidymart_storage", "processing_trail"],
    auto_optimizations=["noise_filtering", "sentiment_analysis"]
)
```

### Workflow Registry
**File**: `packages/tidyllm/workflows/registry.py`

**Purpose**: Central template and criteria management

**Components**:
- **Template Management**: Pre-configured workflow templates
- **Scoring Rubrics**: Automated quality assessment
- **Validation Rules**: Input/output validation
- **Criterion Files**: Workflow-specific requirements
- **Markdown Templates**: Documentation generation

---

## 🚀 Flow Macro Commands

### Basic Flow Macros
Flow Macros are command sequences that trigger one or more workflows:

| Macro Command | Description | Workflow Chain |
|---------------|-------------|----------------|
| `[MVR_ANALYSIS]` | 4-stage document analysis | mvr_tag → mvr_qa → mvr_peer → mvr_report |
| `[COMPLIANCE_CHECK]` | Regulatory validation | compliance_scan → audit_trail → report_gen |
| `[QUALITY_REVIEW]` | Quality assurance workflow | quality_scan → peer_review → approval |
| `[DOMAIN_RAG]` | RAG system creation | input → process → index → deploy |
| `[HYBRID_ANALYSIS]` | Multi-modal analysis | text_analysis + image_analysis + data_extraction |

### Advanced Flow Macros
Complex multi-workflow sequences:

```
[COMPREHENSIVE_REVIEW] document.pdf
├── MVR_ANALYSIS
├── COMPLIANCE_CHECK
├── QUALITY_REVIEW
└── PEER_REVIEW → FINAL_REPORT

[FINANCIAL_PIPELINE] quarterly_report.xlsx
├── DATA_EXTRACTION
├── FINANCIAL_ANALYSIS
├── COMPLIANCE_CHECK
└── AUDIT_TRAIL → APPROVAL_WORKFLOW

[CODE_DELIVERY] repository/
├── CODE_REVIEW
├── QUALITY_CHECK
├── COMPLIANCE_CHECK
└── DEPLOYMENT_WORKFLOW
```

### Flow Macro Syntax
```
[WORKFLOW_NAME] input_file(s) [options]
[WORKFLOW_CHAIN] input → stage1 → stage2 → output
[CONDITIONAL] input ? condition : true_workflow : false_workflow
[PARALLEL] input || workflow1 & workflow2 & workflow3
```

---

## 📊 Workflow Types and Use Cases

### 1. MVR Analysis Workflow
**Purpose**: Model Validation Report document processing
**Stages**: MVR Tag → MVR QA → MVR Peer Review → MVR Report Generation
**RAG Integration**: AI-powered, PostgreSQL, Intelligent retrieval
**Compliance**: SR-11-7, SOX-404 audit requirements

### 2. Domain RAG Creation
**Purpose**: Build specialized RAG systems for specific domains
**Stages**: Input Processing → Document Processing → Vector Indexing → System Deployment
**RAG Types**: AI-powered, PostgreSQL, Intelligent, SME, DSPy integration

### 3. Financial Analysis
**Purpose**: Financial document analysis and reporting
**Integration**: MLflow tracking, PostgreSQL storage, Bedrock LLM
**Outputs**: Analysis reports, compliance documentation, audit trails

### 4. Contract Review
**Purpose**: Legal document analysis and compliance checking
**Features**: Clause extraction, risk assessment, compliance validation
**Outputs**: Review reports, risk matrices, approval workflows

### 5. Quality Check
**Purpose**: Automated quality assurance for documents and code
**Features**: Standards compliance, best practice validation, metrics collection
**Integration**: Code analysis tools, document validators, reporting systems

---

## 🔌 Integration Points

### RAG System Integration
- **Automatic Deployment**: UFM automatically deploys required RAG systems
- **Multi-RAG Support**: AI-powered, PostgreSQL, Intelligent, SME, DSPy
- **Domain Specialization**: RAG systems tailored to workflow requirements

### MLflow Integration
- **Experiment Tracking**: Workflow execution metrics and results
- **Artifact Storage**: S3-based artifact management
- **Model Management**: LLM and embedding model tracking

### Database Integration
- **PostgreSQL Primary**: Workflow state and results storage
- **SQLite Backup**: Local workflow data backup
- **Connection Pooling**: Efficient database connection management

### LLM Integration
- **AWS Bedrock**: Claude 3.5 Sonnet, Haiku, Opus models
- **Embedding Models**: Amazon Titan, Cohere embedding models
- **Circuit Breakers**: Robust error handling and retry logic

---

## 🏃‍♂️ Getting Started

### 1. Access the Chat Workflow Interface
```
http://localhost:8503
```

### 2. Execute a Flow Macro
1. Open the Chat Workflow Interface
2. Use the Flow Macro sidebar to select a workflow
3. Execute using Flow Macro syntax: `[MVR_ANALYSIS] document.pdf`
4. Monitor execution in real-time
5. Review results and audit trail

### 3. Programmatic Access
```python
from packages.tidyllm.services.unified_flow_manager import UnifiedFlowManager, WorkflowSystemType

# Initialize UFM
ufm = UnifiedFlowManager()

# Create workflow
result = ufm.create_workflow(
    WorkflowSystemType.MVR_ANALYSIS,
    {"domain": "financial", "documents": ["quarterly_report.pdf"]}
)

# Deploy and execute
ufm.deploy_workflow(result["workflow_id"])
execution_result = ufm.execute_workflow(result["workflow_id"])
```

### 4. Health Monitoring
```python
# Check system health
health = ufm.health_check()
print(f"Overall Health: {health['overall_healthy']}")

# Get performance metrics
metrics = ufm.get_performance_metrics()
print(f"Total Workflows: {metrics['total_workflows']}")
```

---

## 📈 Monitoring and Metrics

### Real-time Monitoring
- **Workflow Status**: Created, Deployed, Running, Completed, Failed, Paused, Archived
- **Execution Progress**: Stage-by-stage progress tracking
- **Resource Usage**: CPU, memory, and storage utilization
- **Error Tracking**: Detailed error logs and recovery options

### Performance Metrics
- **Execution Time**: Per-workflow and per-stage timing
- **Success Rates**: Workflow completion statistics
- **Resource Efficiency**: Throughput and utilization metrics
- **Quality Scores**: Automated quality assessment results

### Audit and Compliance
- **Complete Audit Trail**: All workflow actions logged
- **Compliance Reporting**: SR-11-7, SOX-404 requirement tracking
- **Change Management**: Version control and approval workflows
- **Security Logging**: Access control and security event tracking

---

## 🔧 Advanced Configuration

### Custom Workflow Creation
```python
# Define custom workflow template
custom_template = {
    "workflow_id": "custom_analysis",
    "workflow_name": "Custom Analysis Workflow",
    "workflow_type": "custom_workflow",
    "description": "Tailored workflow for specific requirements",
    "stages": ["input", "custom_process", "validation", "output"],
    "rag_integration": ["ai_powered", "postgres"],
    "criteria": {
        "scoring_rubric": {"accuracy": 0.4, "efficiency": 0.3, "compliance": 0.3}
    }
}
```

### Flow Macro Extensions
Create custom Flow Macros by extending the FlowMacro base class:

```python
class CustomAnalysisFlow(FlowMacro):
    def __init__(self):
        config = FlowMacroConfig(
            macro_id="custom_analysis_v1",
            macro_type="Custom Analysis",
            created_by="TidyLLM",
            approved_gateways=["custom_gateway"],
            audit_requirements=["custom_audit"],
            auto_optimizations=["custom_optimization"]
        )
        super().__init__(config)
```

---

## 🛟 Troubleshooting

### Common Issues
1. **Workflow Creation Fails**: Check system availability and RAG dependencies
2. **Execution Timeout**: Review resource allocation and increase timeout settings
3. **RAG Integration Issues**: Verify database connections and model availability
4. **Compliance Failures**: Check audit requirements and approval workflows

### Debug Tools
- **Functional Tests**: `python functionals/workflow/tests/test_workflow_functional.py`
- **Health Checks**: UFM health monitoring system
- **Log Analysis**: Structured logging with correlation IDs
- **Performance Profiling**: Built-in metrics collection

---

## 📚 Additional Resources

### Documentation
- **UFM API Reference**: `packages/tidyllm/services/unified_flow_manager.py`
- **Flow Macro Guide**: `portals/chat/chat_workflow_interface.py`
- **Workflow Registry**: `packages/tidyllm/workflows/registry.py`

### Testing
- **Functional Tests**: `functionals/workflow/tests/`
- **Integration Tests**: Portal-specific test suites
- **Performance Tests**: Load and stress testing tools

### Support
- **Chat Interface**: Interactive help and guidance
- **Health Monitoring**: Real-time system status
- **Audit Logs**: Comprehensive execution tracking
- **Error Recovery**: Automated retry and fallback mechanisms

---

*For technical support or workflow customization, refer to the TidyLLM documentation or contact the development team.*