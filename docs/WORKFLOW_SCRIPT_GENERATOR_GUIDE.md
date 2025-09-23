# Workflow Script Generator Guide
> **Complete documentation for the TidyLLM Workflow Script Generation System**

## 🎯 Overview

The Workflow Script Generator allows you to create downloadable Python scripts that automate complex AI-powered workflows. Each script combines chat modes, model configurations, and the proven 5-stage OODA loop pattern to create executable automation tools.

**Key Features:**
- ✅ Interactive visual workflow builder
- ✅ Downloadable executable Python scripts
- ✅ 5-stage pattern (OBSERVE → ORIENT → DECIDE → ACT → MONITOR)
- ✅ Granular chat mode control per step
- ✅ Custom command templates
- ✅ Pipeline chaining capabilities
- ✅ Real TidyLLM integration

---

## 📍 Location & Access

### Where to Find It
1. **Main Portal**: Open Chat Portal (http://localhost:8502)
2. **Navigate to**: `Modes Overview` tab
3. **Scroll to**: `🚀 Workflow Script Builder` section

### Alternative Access
- **Workflows Tab**: Custom Commands and Pipeline Builder
- **Direct Import**: `from portals.chat.workflow_script_generator import WorkflowScriptGenerator`

---

## 🏗️ Architecture

### System Components

```
Chat Portal (UI Layer)
    ↓
Workflow Script Generator (Logic Layer)
    ↓
Generated Python Script (Executable Layer)
    ↓
UnifiedChatManager (AI Processing Layer)
    ↓
Infrastructure Services (Bedrock, RAG, etc.)
```

### File Structure
```
compliance-qa/
├── portals/chat/
│   ├── chat_app.py              # Main portal with builder UI
│   └── workflow_script_generator.py  # Generation logic
├── docs/
│   ├── WORKFLOW_SCRIPT_GENERATOR_GUIDE.md  # This file
│   └── CHAT_MODES_OVERVIEW.md              # Mode documentation
└── generated_scripts/
    └── [downloaded_workflows].py            # User-generated scripts
```

---

## 🎛️ The 5-Stage Pattern

### Stage Definitions

| Stage | Purpose | Typical Actions | Chat Mode Recommendations |
|-------|---------|-----------------|---------------------------|
| **OBSERVE** | Data gathering | Load documents, extract data, search | `direct` + haiku (fast) |
| **ORIENT** | Understanding | Analyze content, compare, contextualize | `rag` + sonnet (balanced) |
| **DECIDE** | Decision making | Evaluate options, generate insights | `hybrid` + sonnet (smart) |
| **ACT** | Taking action | Create reports, send results, execute | `direct` + opus (quality) |
| **MONITOR** | Validation | Check results, log metrics, validate | `direct` + haiku (efficient) |

### Example Stage Flow
```
OBSERVE: Load financial report → document_text
    ↓
ORIENT: Analyze financial data → financial_analysis
    ↓
DECIDE: Identify risk factors → risk_assessment
    ↓
ACT: Generate executive summary → executive_report
    ↓
MONITOR: Validate report accuracy → validation_log
```

---

## 📖 Step-by-Step Usage Guide

### 1. **Access the Builder**

1. Open Chat Portal: http://localhost:8502
2. Click **"Modes Overview"** tab
3. Scroll down to **"🚀 Workflow Script Builder"**

### 2. **Configure Workflow Settings**

```yaml
Workflow Name: "Financial Report Analysis"
Description: "Automated analysis of quarterly financial reports"
Author: "Your Name"
```

### 3. **Build Workflow Steps**

#### Adding a Step:
1. Click **"➕ Add New Step"**
2. Fill in step details:

**Example Step Configuration:**
```yaml
Step Name: "load_financial_data"
Stage: "OBSERVE"
Description: "Load and extract financial data from quarterly report"
Model: "claude-3-haiku"         # Fast for data extraction
Temperature: 0.3                # Low for accuracy
Mode: "direct"                  # Simple extraction
Requires: []                    # No dependencies (first step)
Produces: ["financial_data"]    # Output for next step
Max Tokens: 1000               # Sufficient for data extraction
```

#### Step Dependencies:
- **Requires**: What this step needs from previous steps
- **Produces**: What this step outputs for later steps

**Example Dependency Chain:**
```yaml
Step 1: Produces → ["raw_data"]
Step 2: Requires → ["raw_data"], Produces → ["analysis"]
Step 3: Requires → ["analysis"], Produces → ["report"]
```

### 4. **Configure Chat Mode Combinations**

Each step can use different AI configurations:

**For Data Extraction (OBSERVE):**
```yaml
Model: claude-3-haiku     # Fast and cost-effective
Temperature: 0.2          # Consistent extraction
Mode: direct              # Simple processing
```

**For Analysis (ORIENT):**
```yaml
Model: claude-3-sonnet    # Balanced performance
Temperature: 0.5          # Some creativity for insights
Mode: rag                 # Use knowledge base
```

**For Final Output (ACT):**
```yaml
Model: claude-3-opus      # Highest quality
Temperature: 0.4          # Professional output
Mode: direct              # Controlled generation
```

### 5. **Generate and Download**

1. Review your workflow steps
2. Click **"⬇️ Generate & Download Script"**
3. Click **"📥 Download workflow_script.py"**
4. Save the file to your desired location

---

## 🔧 Working with Generated Scripts

### Script Structure

Generated scripts follow this pattern:

```python
#!/usr/bin/env python3
"""
================================================================================
FILENAME: financial_report_analysis_workflow.py
DATE: 2025-09-23
AUTHOR: Your Name
PURPOSE: Automated analysis of quarterly financial reports
================================================================================
"""

# Imports and setup
import sys, json, time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# TidyLLM integration
from packages.tidyllm.services.unified_chat_manager import UnifiedChatManager

# Base step class with 8 standard attributes
class BaseWorkflowStep:
    # Core workflow step implementation

# Generated step classes
class LoadFinancialDataStep(BaseWorkflowStep):
    # Your specific step implementation

class AnalyzeDataStep(BaseWorkflowStep):
    # Next step implementation

# Pipeline executor
class FinancialReportAnalysisPipeline:
    # Orchestrates all steps

# Main execution
def main():
    # Command-line interface

if __name__ == "__main__":
    # CLI argument parsing and execution
```

### Running Generated Scripts

#### Basic Execution:
```bash
python financial_report_analysis_workflow.py
```

#### With Input Data:
```bash
python financial_report_analysis_workflow.py --input "Q3_2024_Report.pdf"
```

#### With Output File:
```bash
python financial_report_analysis_workflow.py \
    --input "data.txt" \
    --output "results.json"
```

#### Dry Run (Preview):
```bash
python financial_report_analysis_workflow.py --dry-run --verbose
```

### Script Features

**Automatic Features:**
- ✅ Progress tracking and logging
- ✅ Error handling and recovery
- ✅ Dependency validation
- ✅ JSON result export
- ✅ CLI argument support
- ✅ Mock mode fallback

**Example Output:**
```
============================================================
Executing Financial Report Analysis Pipeline
============================================================

▶ Step 1: load_financial_data
  Type: OBSERVE
  Model: claude-3-haiku (temp=0.3)
  ✓ Completed in 1.23s

▶ Step 2: analyze_data
  Type: ORIENT
  Model: claude-3-sonnet (temp=0.5)
  ✓ Completed in 3.45s

▶ Step 3: generate_summary
  Type: ACT
  Model: claude-3-opus (temp=0.4)
  ✓ Completed in 5.67s

============================================================
Pipeline COMPLETED
============================================================
```

---

## 🛠️ Custom Commands

### Creating Custom Commands

1. Navigate to **Workflows** tab → **Custom Commands**
2. Build reusable command templates:

**Example Custom Command:**
```yaml
Name: "Legal Document Review"
Description: "Analyze legal documents for compliance issues"
Model: "claude-3-opus"
Temperature: 0.2
Mode: "rag"
Template: |
  Review the following legal document for compliance with {standards}:

  Document: {input}

  Provide analysis of:
  1. Compliance issues
  2. Risk factors
  3. Recommendations
```

### Using Custom Commands

**In Workflows:**
- Commands can be added to pipeline builders
- Reusable across multiple workflows
- Maintain consistent configurations

**Template Variables:**
- `{input}` = User-provided input
- `{context}` = Workflow context
- `{standards}` = Custom parameters

---

## 🔗 Pipeline Builder

### Creating Multi-Step Pipelines

1. Go to **Workflows** tab → **Pipeline Builder**
2. Chain different component types:

**Component Types:**
- **Workflows**: Existing workflow definitions
- **Custom Commands**: Your saved command templates
- **Chat Modes**: Direct mode selections

**Example Pipeline:**
```
1. Workflow: mvr_analysis
2. Custom Command: Legal Document Review
3. Chat Mode: hybrid
4. Custom Command: Generate Executive Summary
```

### Pipeline Execution

Pipelines execute sequentially:
```
Step 1 Output → Step 2 Input → Step 3 Input → Final Result
```

Each step can access outputs from previous steps.

---

## 📊 Example Use Cases

### 1. **Document Processing Pipeline**

**Scenario**: Process legal contracts for compliance review

**Workflow Steps:**
```yaml
1. OBSERVE - Extract text from PDF contract
   - Model: claude-3-haiku
   - Mode: direct
   - Output: contract_text

2. ORIENT - Analyze contract structure
   - Model: claude-3-sonnet
   - Mode: rag (legal knowledge base)
   - Input: contract_text
   - Output: structure_analysis

3. DECIDE - Identify compliance issues
   - Model: claude-3-opus
   - Mode: hybrid
   - Input: structure_analysis
   - Output: compliance_issues

4. ACT - Generate compliance report
   - Model: claude-3-opus
   - Mode: direct
   - Input: compliance_issues
   - Output: compliance_report

5. MONITOR - Validate report completeness
   - Model: claude-3-haiku
   - Mode: direct
   - Input: compliance_report
   - Output: validation_log
```

### 2. **Financial Analysis Workflow**

**Scenario**: Analyze quarterly earnings reports

**Workflow Steps:**
```yaml
1. OBSERVE - Load financial data
   - Extract numbers from earnings report
   - Model: claude-3-haiku (fast extraction)

2. ORIENT - Historical comparison
   - Compare with previous quarters
   - Model: claude-3-sonnet + RAG (historical data)

3. DECIDE - Risk assessment
   - Identify trends and risks
   - Model: claude-3-opus (complex analysis)

4. ACT - Executive summary
   - Generate investor-ready summary
   - Model: claude-3-opus (high quality)

5. MONITOR - Accuracy validation
   - Verify calculations and claims
   - Model: claude-3-haiku (efficient checking)
```

### 3. **Customer Support Automation**

**Scenario**: Process and route customer inquiries

**Workflow Steps:**
```yaml
1. OBSERVE - Classify inquiry type
   - Categorize customer message
   - Model: claude-3-haiku (fast classification)

2. ORIENT - Retrieve relevant information
   - Search knowledge base and history
   - Model: claude-3-sonnet + RAG

3. DECIDE - Determine response strategy
   - Choose escalation vs. auto-response
   - Model: claude-3-sonnet (decision logic)

4. ACT - Generate response
   - Create customer-friendly response
   - Model: claude-3-sonnet (conversational)

5. MONITOR - Quality check
   - Validate response appropriateness
   - Model: claude-3-haiku (quick validation)
```

---

## ⚙️ Advanced Configuration

### Model Selection Strategy

**For High Volume, Low Complexity:**
```yaml
Model: claude-3-haiku
Temperature: 0.3-0.5
Mode: direct
Reasoning: Fast, cost-effective, consistent
```

**For Balanced Tasks:**
```yaml
Model: claude-3-sonnet
Temperature: 0.5-0.7
Mode: rag or hybrid
Reasoning: Good balance of speed, quality, context
```

**For Complex Analysis:**
```yaml
Model: claude-3-opus
Temperature: 0.3-0.6
Mode: hybrid or rag
Reasoning: Highest quality, best reasoning
```

### Temperature Guidelines

| Temperature | Use Case | Example |
|-------------|----------|---------|
| 0.0 - 0.3 | Deterministic tasks | Data extraction, validation |
| 0.3 - 0.6 | Analytical tasks | Financial analysis, compliance |
| 0.6 - 0.8 | Creative tasks | Content generation, brainstorming |
| 0.8 - 1.0 | Highly creative | Marketing copy, artistic content |

### Mode Selection Logic

**Use `direct` when:**
- Simple input/output transformation
- No external knowledge needed
- Speed is priority
- Deterministic results desired

**Use `rag` when:**
- Need domain-specific knowledge
- Document/data context required
- Historical information relevant
- Expert knowledge necessary

**Use `hybrid` when:**
- Unsure which approach is best
- Query complexity varies
- Want automatic optimization
- Mixed requirements

---

## 🔍 Troubleshooting

### Common Issues

**Issue**: "Import Error - TidyLLM not available"
**Solution**:
```bash
# Ensure you're in the compliance-qa directory
cd /path/to/compliance-qa

# Run with proper Python path
PYTHONPATH=. python your_workflow.py
```

**Issue**: "Missing required input"
**Solution**: Check step dependencies
```python
# Verify requires/produces chain
Step 1: produces = ["data"]
Step 2: requires = ["data"]  # Must match exactly
```

**Issue**: "Chat manager initialization failed"
**Solution**: Check AWS credentials and infrastructure
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check TidyLLM infrastructure
python -c "from packages.tidyllm.services.unified_chat_manager import UnifiedChatManager; UnifiedChatManager()"
```

### Debug Mode

Generated scripts include verbose mode:
```bash
python workflow.py --verbose
```

This shows:
- Step-by-step execution details
- Model and configuration used
- Timing information
- Error details if failures occur

### Mock Mode Testing

When TidyLLM isn't available, scripts run in mock mode:
```python
# Mock responses for testing
return f"[Mock] Executed {self.step_name}: {prompt[:100]}"
```

This allows testing workflow logic without AI infrastructure.

---

## 📈 Performance Optimization

### Workflow Design Best Practices

**1. Minimize Model Switching:**
```yaml
# Good: Consistent model usage
Step 1-3: claude-3-haiku (preprocessing)
Step 4-5: claude-3-opus (final output)

# Avoid: Constant switching
Step 1: haiku → Step 2: opus → Step 3: haiku
```

**2. Optimize Token Usage:**
```yaml
# Use appropriate max_tokens
Data extraction: 500-1000 tokens
Analysis: 1500-2500 tokens
Final reports: 2000-4000 tokens
```

**3. Strategic Temperature Settings:**
```yaml
# Lower temperatures for consistency
Data processing: 0.1-0.3
# Higher for creativity
Content generation: 0.6-0.8
```

### Cost Optimization

**Model Cost Comparison:**
- **claude-3-haiku**: ~$0.01 per query (fastest, cheapest)
- **claude-3-sonnet**: ~$0.03 per query (balanced)
- **claude-3-opus**: ~$0.05 per query (highest quality)

**Optimization Strategy:**
1. Use haiku for preprocessing and validation
2. Use sonnet for main processing
3. Use opus only for final, critical outputs

---

## 🔄 Integration Patterns

### Chaining Generated Scripts

**Method 1: File-based Chaining**
```bash
# Script 1 outputs to file
python extract_data.py --output data.json

# Script 2 reads from file
python analyze_data.py --input data.json --output analysis.json

# Script 3 uses analysis
python generate_report.py --input analysis.json
```

**Method 2: Pipeline Scripts**
```python
# master_pipeline.py
import subprocess

# Run scripts in sequence
subprocess.run(["python", "extract_data.py", "--output", "data.json"])
subprocess.run(["python", "analyze_data.py", "--input", "data.json"])
subprocess.run(["python", "generate_report.py", "--input", "analysis.json"])
```

**Method 3: Python Import**
```python
# Import generated classes
from extract_data_workflow import ExtractDataPipeline
from analyze_data_workflow import AnalyzeDataPipeline

# Chain programmatically
extract_pipeline = ExtractDataPipeline()
extract_results = extract_pipeline.execute({"input": "data.txt"})

analyze_pipeline = AnalyzeDataPipeline()
final_results = analyze_pipeline.execute(extract_results["final_context"])
```

### Scheduling and Automation

**Cron Job Integration:**
```bash
# Daily report generation
0 9 * * * cd /path/to/workflows && python daily_report.py --input /data/latest.csv

# Weekly analysis
0 9 * * 1 cd /path/to/workflows && python weekly_analysis.py --output /reports/weekly.json
```

**CI/CD Integration:**
```yaml
# GitHub Actions example
name: Run Workflow
on:
  push:
    paths: ['data/**']
jobs:
  process:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Analysis
        run: python analysis_workflow.py --input data/latest.csv
```

---

## 📚 Additional Resources

### Related Documentation
- **[Chat Modes Overview](CHAT_MODES_OVERVIEW.md)**: Understanding chat mode combinations
- **[Chat Mode Recipes](CHAT_MODE_RECIPES.md)**: Domain-specific mode presets
- **[TidyLLM Architecture](../docs/architecture/)**: Understanding the underlying system

### Example Scripts Repository
```
compliance-qa/examples/workflows/
├── document_analysis.py      # Complete document processing
├── financial_reporting.py    # Financial analysis workflow
├── customer_support.py       # Support ticket processing
├── compliance_check.py       # Regulatory compliance
└── data_validation.py        # Data quality workflows
```

### Support and Community
- **Issues**: Report problems via the chat portal
- **Feature Requests**: Use the custom commands builder
- **Documentation**: All docs in `/docs` folder
- **Examples**: Pre-built workflows in portal

---

## 🎯 Quick Start Checklist

### First-Time Setup
- [ ] Open Chat Portal (http://localhost:8502)
- [ ] Navigate to "Modes Overview" tab
- [ ] Locate "Workflow Script Builder" section
- [ ] Try the "Document Analysis Example"
- [ ] Download and test the generated script

### Creating Your First Workflow
- [ ] Define your workflow purpose
- [ ] Map your process to 5 stages (OBSERVE → ORIENT → DECIDE → ACT → MONITOR)
- [ ] Choose appropriate models for each stage
- [ ] Set temperature based on task requirements
- [ ] Configure step dependencies (requires/produces)
- [ ] Generate and test the script

### Advanced Usage
- [ ] Create custom commands for reusable patterns
- [ ] Build multi-step pipelines
- [ ] Optimize for cost and performance
- [ ] Integrate with existing systems
- [ ] Set up automated scheduling

---

**Last Updated**: 2025-09-23
**Version**: 1.0.0
**Author**: TidyLLM Team
**System**: Workflow Script Generator v1.0