# Compliance QA

An AI-powered Quality Assurance and Compliance system for regulatory document processing and workflow automation.

## Overview

Compliance QA is a comprehensive framework designed to automate quality assurance workflows, perform regulatory compliance checking, and optimize document processing using advanced AI models.

## Three Main Functions

### 1. QA Control Flows & Workflow Automation
**Location:** `packages/tidyllm/flow/qa_control_flows.py`

The QA Control Flow system provides bracket command shortcuts for common audit operations and compliance workflows:

#### Key Features:
- **MVR Processing**: Complete Model Validation Report processing with compliance checking
- **Compliance Validation**: Automated checking against MVS and VST regulatory standards
- **Finding Classification**: Automatic categorization of findings by severity and regulatory impact
- **Audit Workflow Orchestration**: End-to-end audit workflow management from document intake to final report

#### Example Usage:
```python
from packages.tidyllm.flow.qa_control_flows import QAControlFlowManager

# Initialize the QA flow manager
qa_manager = QAControlFlowManager()

# Process an MVR document
result = qa_manager.execute_qa_flow(
    "[Process MVR]",
    context={"document_id": "MVR_2025_001"}
)

# Check compliance against MVS standards
compliance_result = qa_manager.execute_qa_flow(
    "[Check MVS Compliance]",
    context={"document_path": "path/to/document.pdf"}
)

# Classify findings by severity
findings_result = qa_manager.execute_qa_flow(
    "[Classify Findings]",
    context={"findings": [...]}
)
```

#### Available Commands:
- `[Process MVR]` - Full MVR processing workflow
- `[Check MVS Compliance]` - Validate against MVS 5.4.3 requirements
- `[Check VST Compliance]` - Validate against VST Section 3, 4, 5
- `[Classify Findings]` - Categorize findings by severity
- `[Generate Finding Report]` - Create executive summary reports
- `[Start Audit Workflow]` - Initialize complete audit workflow
- `[Run QA Checklist]` - Execute standard QA checklist

### 2. Document Processing & Content Extraction
**Location:** `packages/tidyllm/infrastructure/adapters/simple_qa_adapter.py`

A lightweight document processor that handles multiple file formats without heavy dependencies:

#### Key Features:
- **Multi-format Support**: JSON, Excel (XLSX/XLS), and PDF files
- **Content Extraction**: Automatic extraction of document structure and content
- **Statistical Analysis**: Basic metrics and statistics for processed documents
- **Error Handling**: Graceful handling of unsupported formats and processing errors

#### Example Usage:
```python
from packages.tidyllm.infrastructure.adapters.simple_qa_adapter import SimpleQAProcessor

# Initialize the processor
processor = SimpleQAProcessor()

# Process a JSON file
json_result = processor.process_files("data/compliance_report.json")
print(f"Processing Status: {json_result.processing_status}")
print(f"Statistics: {json_result.basic_stats}")

# Process an Excel file
excel_result = processor.process_files("data/mvr_checklist.xlsx")
print(f"Sheets: {excel_result.basic_stats['sheet_names']}")
print(f"Columns: {excel_result.basic_stats['column_names']}")

# Process a PDF file
pdf_result = processor.process_files("documents/regulatory_report.pdf")
print(f"File Size: {pdf_result.basic_stats['file_size_mb']} MB")
```

#### Supported Formats:
- **JSON**: Full parsing with depth analysis and key extraction
- **Excel**: Sheet analysis, column extraction, basic data statistics
- **PDF**: File metadata and size analysis (full text extraction with optional dependencies)

### 3. AI-Powered A/B Testing & Optimization
**Location:** `packages/tidyllm/services/optimization/dual_ai_ab_testing.py`

Advanced framework for testing and optimizing AI model combinations for QA workflows:

#### Key Features:
- **Multi-Model Testing**: Compare different AI model combinations (Claude Haiku, Sonnet, Opus)
- **Dual-Stage Processing**: Initial analysis followed by enhanced optimization
- **Performance Metrics**: Track processing time, confidence scores, and token usage
- **Automated Reporting**: Generate comparison reports for different model configurations

#### Test Configurations:
- **Test A (Speed Focus)**: Haiku → Sonnet - Ultra-fast processing
- **Test B (Quality Focus)**: Sonnet → 3.5-Sonnet - High quality output
- **Test C (Premium Focus)**: Haiku → 3.5-Sonnet - Balance of speed and quality
- **Test D (DSPy Optimized)**: DSPy-powered pipeline with structured outputs

#### Example Usage:
```python
from packages.tidyllm.services.optimization.dual_ai_ab_testing import (
    DualAIABTesting,
    run_qaqc_ab_testing,
    run_selective_sequential_testing
)

# Run full A/B/C/D testing suite
test_results = run_qaqc_ab_testing(
    query="Analyze the QA/QC workflow for data quality assessment",
    template_order=["metadata_extraction", "analysis_steps", "results_aggregation"],
    sequential=True,  # Run tests sequentially to avoid racing
    delay_seconds=3
)

# Run selective tests (only A and C)
selective_results = run_selective_sequential_testing(
    selected_tests=["A", "C"],
    query="Optimize compliance checking workflow",
    delay_seconds=2
)

# Access results
for test_id, result in test_results['results'].items():
    print(f"Test {test_id}:")
    print(f"  Total Time: {result.total_processing_time_ms}ms")
    print(f"  Confidence Improvement: {result.confidence_improvement}")
    print(f"  Models: {test_results['test_configurations'][test_id].stage1_model} → "
          f"{test_results['test_configurations'][test_id].stage2_model}")
```

#### Metrics Tracked:
- Processing time (per stage and total)
- Confidence scores and improvement
- Token usage and cost efficiency
- Content quality and expansion ratio

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/compliance-qa.git
cd compliance-qa

# Install dependencies
pip install -r requirements.txt

# Install the tidyllm package
cd packages/tidyllm
pip install -e .
```

## Project Structure

```
compliance-qa/
├── packages/
│   └── tidyllm/
│       ├── flow/
│       │   └── qa_control_flows.py       # QA workflow automation
│       ├── infrastructure/
│       │   └── adapters/
│       │       └── simple_qa_adapter.py  # Document processing
│       └── services/
│           └── optimization/
│               └── dual_ai_ab_testing.py  # AI optimization
├── docs/                                  # Documentation
├── workflows/
│   └── projects/
│       └── alex_qaqc/                    # QA/QC workflow templates
└── README.md                              # This file
```

## Use Cases

1. **Regulatory Compliance Checking**: Automated validation of financial documents against regulatory standards
2. **Model Validation Reports**: Processing and analyzing MVR documents for compliance
3. **Audit Trail Generation**: Complete audit workflow from document intake to final reporting
4. **Quality Assurance Automation**: Running standardized QA checklists and generating reports
5. **AI Model Optimization**: Testing different AI configurations to find optimal performance/quality balance

## Configuration

The system uses YAML configuration files for workflow definitions and can be customized through:
- Workflow templates in `workflows/projects/`
- Compliance standards in `qa_control_flows.py`
- AI model configurations in `dual_ai_ab_testing.py`

## Dependencies

Core dependencies:
- pandas (Excel processing)
- mlflow (optional, for experiment tracking)
- dspy (optional, for advanced AI optimization)
- Standard Python libraries (json, pathlib, logging)

## License

[Specify your license here]

## Contributing

[Contribution guidelines]

## Support

For questions or issues, please contact the QA team or create an issue in the repository.