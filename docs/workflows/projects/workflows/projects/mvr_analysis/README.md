# Mvr Analysis Workflow

## 📋 **Overview**

**Workflow ID**: `mvr_analysis`
**Type**: `MVR Analysis`
**Priority**: `normal`
**Status**: `active`

Model Validation Report analysis using QA gap analyzer and workflow router

## 🚀 **Quick Start**

### **CLI Usage**
```bash
# List available workflows
python workflow_cli.py list --name mvr_analysis

# Get workflow details
python workflow_cli.py info mvr_analysis

# Execute via Boss Portal
streamlit run unified_boss_portal.py
# Navigate to: 📝 Template Creator → Mvr Analysis
```

### **Python API Usage**
```python
from workflow_registry_system import WorkflowRegistrySystem
from intelligent_document_intake import IntelligentDocumentIntake

# Initialize systems
registry = WorkflowRegistrySystem()
intake = IntelligentDocumentIntake(registry)

# Route document to workflow
matches = intake.analyze_and_route_document("path/to/document.pdf")
for match in matches:
    if match.workflow_id == "mvr_analysis":
        print(f"Confidence: {match.confidence_score:.2f}")
        print(f"Recommended: {match.recommended}")
```

### **Bracket Commands** *(Optional - if enabled in settings)*
```bash
# CLI bracket command
tidyllm '[mvr_analysis]'

# API bracket command
curl -X POST http://localhost:8000/flow \\
  -H "Content-Type: application/json" \\
  -d '{"command": "[mvr_analysis]"}'

# S3 trigger file
aws s3 cp triggers/[mvr_analysis].trigger s3://workflow-bucket/triggers/
```

## ⚙️ **Configuration Options**

### **Template Variables**
| Field | Type | Description |
|-------|------|-------------|
| `actual_sections` | string | Template field |
| `analyzer_version` | string | Template field |
| `challenge_contribution` | string | Template field |
| `challenge_justification` | string | Template field |
| `challenge_score` | number | Challenge assessment score |
| `challenge_weight` | string | Template field |
| `clarity_contribution` | string | Template field |
| `clarity_justification` | string | Template field |
| `clarity_score` | number | Clarity assessment score |
| `clarity_weight` | string | Template field |
| `complexity_level` | string | Template field |
| `compliance_contribution` | string | Template field |
| `compliance_justification` | string | Template field |
| `compliance_score` | number | Compliance assessment score |
| `compliance_weight` | string | Template field |
| `coverage_contribution` | string | Template field |
| `coverage_justification` | string | Template field |
| `coverage_score` | number | Coverage assessment score |
| `coverage_weight` | string | Template field |
| `expected_sections` | string | Template field |
| `generated_date` | date | Report generation timestamp |
| `immediate_actions` | array | Priority action items |
| `incomplete_sections` | array | List of incomplete sections |
| `judge_version` | string | Template field |
| `key_findings` | string | Template field |
| `missing_sections` | array | List of missing sections |
| `model_id` | string | Model identifier |
| `model_specific_requirements` | string | Template field |
| `model_type` | string | Template field |
| `overall_score` | number | Total calculated score |
| `pending_items` | string | Template field |
| `processing_time` | string | Template field |
| `quality_improvement` | string | Template field |
| `regulatory_note` | string | Template field |
| `required_sections` | string | Template field |
| `requirements_analysis` | string | Template field |
| `review_activity` | string | Template field |
| `risk_tier` | string | Template field |
| `third_party` | string | Template field |
| `verdict` | string | Final assessment result |
| `vst_scoped_sections` | string | Template field |


### **Criteria Settings**
| Criterion | Weight | Description |
|-----------|--------|-------------|
| Compliance | 0.35 | Model validation shows missing required sections and incomplete sections |
| Coverage | 0.25 | Validation covers percentage of required sections based on model characteristics |
| Clarity | 0.20 | Review structure follows standard format with sufficient detail |
| Challenge | 0.20 | Evidence of independent challenge and validation |


### **Processing Options**
```yaml
processing_strategy: "single_template"
priority_level: "normal"
estimated_duration_hours: 1.0

# Model Configuration
default_model: "anthropic.claude-3-sonnet-20240229-v1:0"
alternative_models:
  - "anthropic.claude-3-haiku-20240307-v1:0"
  - "anthropic.claude-3-opus-20240229-v1:0"
```

## 📊 **Input Requirements**

### **Document Types**
- PDF: Model validation reports
- DOCX: Draft validation documents
- XLSX: Model data and checklists

### **Required Fields**
- Model identifier
- Validation sections
- Risk classification
- Validation dates

### **Optional Fields**
- Model owner
- Business justification
- Regulatory requirements

### **Document Criteria**
```json
{
  "keywords": [
    "model validation",
    "mvr",
    "compliance"
  ],
  "patterns": [
    "Model ID:",
    "Validation Date:",
    "Risk Rating:"
  ],
  "min_pages": 5
}
```

## 📄 **Output Structure**

### **Generated Files**
- **Report**: `mvr_analysis_report_{timestamp}.pdf`
- **Analysis**: `mvr_analysis_analysis_{timestamp}.json`
- **Metadata**: `mvr_analysis_metadata_{timestamp}.json`

### **Output Fields**
| Field | Description |
|-------|-------------|
| overall_score | Weighted assessment score |
| verdict | PASS/FAIL/REVIEW recommendation |
| missing_sections | Required sections not found |

### **Quality Metrics**
- Processing Time: < 30 seconds
- Accuracy: 95%+ section identification
- Coverage: 100% standard sections

## 🔧 **Advanced Usage**

### **Custom Configuration**
```python
from workflow_registry_system import WorkflowRegistrySystem

registry = WorkflowRegistrySystem()
workflow = registry.get_workflow("mvr_analysis")

# Customize processing
workflow.processing_strategy = "multi_perspective"
workflow.priority_level = "high"

# Add custom fields
workflow.add_custom_field("custom_field", "Custom Value")

# Execute with overrides
result = workflow.execute(
    input_file="document.pdf",
    custom_experiment="custom_analysis_2024",
    model_override="claude-3-opus"
)
```

### **Batch Processing**
```bash
# Process multiple documents
python intelligent_document_intake.py \\
  --batch-process ./input_folder \\
  --workflow mvr_analysis \\
  --output ./output_folder \\
  --parallel 3
```

### **Integration with Boss Portal**
```python
# Access via Boss Portal workflow system
from unified_boss_portal import UnifiedSystemOrchestrator

orchestrator = UnifiedSystemOrchestrator()
result = orchestrator.execute_workflow(
    workflow_id="mvr_analysis",
    input_data=input_data,
    options={
        "model": "claude-3-sonnet",
        "experiment": "production_run",
        "tags": ["automated", "v1.0"]
    }
)
```

## 🛠️ **Development**

### **Template Editing**
```bash
# Edit via Boss Portal
streamlit run unified_boss_portal.py
# Navigate to: 📝 Template Creator → Mvr Analysis → Edit Template

# Direct file editing
nano workflow_registry/workflows/mvr_analysis/templates/mvr_analysis_template.md
```

### **Criteria Editing**
```bash
# Edit via Boss Portal
streamlit run unified_boss_portal.py
# Navigate to: 📝 Template Creator → Mvr Analysis → Edit Criteria

# Direct JSON editing (with JSON scrubbing)
nano workflow_registry/workflows/mvr_analysis/criteria/mvr_analysis_criteria.json
```

### **Testing**
```python
# Test workflow execution
from workflow_registry_system import WorkflowRegistrySystem

registry = WorkflowRegistrySystem()
workflow = registry.get_workflow("mvr_analysis")

# Validate workflow
validation_result = workflow.validate()
print(f"Valid: {validation_result.is_valid}")
print(f"Issues: {validation_result.issues}")

# Test with sample data
test_result = workflow.test_execute(sample_document="test.pdf")
print(f"Success: {test_result.success}")
print(f"Output: {test_result.output_path}")
```

## 📖 **API Reference**

### **REST API Endpoints**

#### Execute Workflow
```http
POST /api/v1/workflows/mvr_analysis/execute
Content-Type: application/json

{
  "input_file": "document.pdf",
  "options": {
    "model": "claude-3-sonnet",
    "experiment": "api_test",
    "tags": ["api", "automated"]
  }
}
```

#### Get Workflow Status
```http
GET /api/v1/workflows/mvr_analysis/status/{execution_id}
```

#### Update Workflow Configuration
```http
PUT /api/v1/workflows/mvr_analysis/config
Content-Type: application/json

{
  "processing_strategy": "multi_perspective",
  "priority_level": "high",
  "model_override": "claude-3-opus"
}
```

### **Python API Classes**

#### WorkflowExecutor
```python
from workflow_registry_system import WorkflowExecutor

executor = WorkflowExecutor()
result = executor.execute_workflow(
    workflow_id="mvr_analysis",
    input_file="document.pdf",
    **options
)
```

#### IntelligentDocumentIntake
```python
from intelligent_document_intake import IntelligentDocumentIntake

intake = IntelligentDocumentIntake()
matches = intake.analyze_document("document.pdf")
best_match = intake.get_best_workflow_match(matches)
```

## 🔍 **Troubleshooting**

### **Common Issues**

#### Workflow Not Found
```bash
# Check workflow is registered
python workflow_cli.py list --all

# Verify folder structure
python workflow_cli.py structure
```

#### Template Rendering Errors
```python
# Check template fields
workflow = registry.get_workflow("mvr_analysis")
missing_fields = workflow.validate_template()
print(f"Missing fields: {missing_fields}")
```

#### Model Access Issues
```bash
# Test model connectivity
python qa_processor.py --chat-test

# Check model configuration
tidyllm config
```

### **Debug Mode**
```bash
# Enable verbose logging
python intelligent_document_intake.py \\
  --workflow mvr_analysis \\
  --debug \\
  --verbose

# Check system status
tidyllm status
```

## 📋 **Validation & Testing**

### **Document Validation**
```python
# Check if document qualifies for workflow
from intelligent_document_intake import IntelligentDocumentIntake

intake = IntelligentDocumentIntake()
profile = intake.analyze_document_profile("test.pdf")

# Check match criteria
matches = intake.match_document_to_workflows(profile)
workflow_match = next(
    (m for m in matches if m.workflow_id == "mvr_analysis"),
    None
)

if workflow_match:
    print(f"Confidence: {workflow_match.confidence_score}")
    print(f"Criteria met: {workflow_match.criteria_met}")
    print(f"Missing: {workflow_match.criteria_failed}")
else:
    print("Document does not qualify for this workflow")
```

### **Performance Testing**
```bash
# Benchmark workflow execution
python workflow_benchmark.py \\
  --workflow mvr_analysis \\
  --sample-docs 10 \\
  --iterations 3 \\
  --report benchmark_report.json
```

## 🏢 **Enterprise Integration**

### **Corporate Compliance**
- **Audit Trail**: All executions logged to MLflow
- **Data Security**: S3 server-side encryption enabled
- **Access Control**: Role-based permissions via Boss Portal
- **Credential Management**: UnifiedSessionManager integration

### **Monitoring & Metrics**
```python
# View execution metrics
from workflow_registry_system import WorkflowRegistrySystem

registry = WorkflowRegistrySystem()
stats = registry.get_workflow_stats()
workflow_stats = stats["workflows"]["mvr_analysis"]

print(f"Success rate: {workflow_stats['success_rate']:.1%}")
print(f"Avg duration: {workflow_stats['avg_duration']:.2f}s")
print(f"Total executions: {workflow_stats['total_executions']}")
```

### **Integration Points**
- **Boss Portal**: Streamlit web interface
- **CLI Tools**: Command line automation
- **REST API**: Programmatic access
- **S3 Triggers**: Event-driven processing
- **MLflow**: Experiment tracking
- **PostgreSQL**: Metadata storage

## 📚 **References**

### **Related Documentation**
- [Workflow Registry Documentation](../WORKFLOW_REGISTRY_DOCUMENTATION.md)
- [Boss Portal User Guide](../unified_boss_portal.py)
- [CLI Quick Reference](../docs/CLI_QUICK_REFERENCE.md)
- [API Patterns](../docs/API_PATTERNS.md)

### **Configuration Files**
- **Template**: `workflow_registry/workflows/mvr_analysis/templates/mvr_analysis_template.md`
- **Criteria**: `workflow_registry/workflows/mvr_analysis/criteria/mvr_analysis_criteria.json`
- **Resources**: `workflow_registry/workflows/mvr_analysis/resources/fields.json`
- **Outputs**: `workflow_registry/workflows/mvr_analysis/outputs/`

### **Support**
- **Issues**: Report problems via Boss Portal → 🔧 Settings
- **Documentation**: [Comprehensive docs](../docs/)
- **Status**: Check system health via `tidyllm status`

---

**Generated by Boss Portal Template Creator** ⚡
**Last Updated**: 2025-09-14
**Workflow Version**: 1.0