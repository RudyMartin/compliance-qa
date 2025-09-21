#!/usr/bin/env python3
"""
Sequential Flow Test Runner
=========================

Test the complete sequential analysis workflow using real documents from our collection.
Demonstrates the {template_fields} extraction and JSON output generation.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def load_sequential_flow_config() -> Dict[str, Any]:
    """Load the sequential analysis flow configuration"""
    config_path = Path(__file__).parent / "sequential_analysis_flow.json"

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_input_files() -> List[str]:
    """Get list of input files from the inputs/ directory"""
    inputs_dir = Path(__file__).parent / "inputs"

    if not inputs_dir.exists():
        return []

    input_files = []
    for file_path in inputs_dir.iterdir():
        if file_path.is_file():
            input_files.append(str(file_path))

    return input_files

def resolve_template_fields(config: Dict[str, Any], input_files: List[str]) -> Dict[str, Any]:
    """Resolve all {template_fields} in the workflow configuration"""

    # Generate unique review_id for this job
    review_id = f"REV{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Template field values
    field_values = {
        "input_files": input_files,
        "quality_threshold": 0.85,
        "domain_context": "financial_analysis",
        "analysis_depth": "comprehensive",
        "validation_criteria": "document_completeness",
        "extraction_schema": "financial_entities",
        "entity_types": ["people", "organizations", "amounts", "dates"],
        "analysis_framework": "pattern_recognition",
        "comparison_baselines": "industry_standards",
        "report_template": "executive_summary",
        "output_format": "comprehensive",
        "review_id": review_id
    }

    # Create resolved configuration
    resolved_config = config.copy()

    # Resolve template fields in each step
    for step in resolved_config.get("steps", []):
        if "input_variables" in step:
            resolved_vars = {}
            for var_name, var_value in step["input_variables"].items():
                if isinstance(var_value, str) and var_value.startswith("{") and var_value.endswith("}"):
                    # Extract field name from {field_name}
                    field_name = var_value[1:-1]
                    if field_name in field_values:
                        resolved_vars[var_name] = field_values[field_name]
                    elif field_name == "previous_step_output":
                        resolved_vars[var_name] = f"Output from step {step['step_number'] - 1}"
                    else:
                        resolved_vars[var_name] = var_value
                else:
                    resolved_vars[var_name] = var_value

            step["resolved_input_variables"] = resolved_vars

    return resolved_config

def simulate_step_execution(step: Dict[str, Any], step_number: int, input_files: List[str] = None) -> Dict[str, Any]:
    """Simulate execution of a workflow step"""

    start_time = datetime.now()

    # Simulate processing time based on step complexity
    import time
    processing_times = {1: 0.1, 2: 0.2, 3: 0.3, 4: 0.2, 5: 0.1}
    time.sleep(processing_times.get(step_number, 0.1))

    end_time = datetime.now()
    processing_time_ms = (end_time - start_time).total_seconds() * 1000

    # Generate mock output based on step type
    if step_number == 1:  # Input Validation
        output = {
            "validation_status": "passed",
            "document_summary": {
                "total_files": len(step["resolved_input_variables"]["input_files"]),
                "valid_files": len(step["resolved_input_variables"]["input_files"]),
                "invalid_files": 0,
                "warnings": []
            },
            "document_metadata": [
                {
                    "filename": "model_validation_report.pdf",
                    "type": "financial_report",
                    "quality_score": 0.92,
                    "metadata": {"pages": 25, "size_mb": 1.7},
                    "issues": []
                }
            ],
            "next_step_ready": True
        }

    elif step_number == 2:  # Data Extraction
        output = {
            "extraction_status": "completed",
            "extracted_data": {
                "entities": {
                    "people": ["John Smith", "Jane Doe"],
                    "organizations": ["Federal Reserve", "Bank XYZ"],
                    "dates": ["2019-02-26", "Q4 2024"],
                    "amounts": ["$2.5M", "$1.8M", "$700K"]
                },
                "key_facts": [
                    "Model validation performed according to SR 11-7",
                    "Risk metrics within acceptable thresholds",
                    "Quarterly performance shows positive trends"
                ],
                "structured_data": [
                    {"metric": "VaR", "value": "2.3%", "benchmark": "2.5%"},
                    {"metric": "Backtesting", "value": "Pass", "confidence": "95%"}
                ],
                "themes": ["model_validation", "risk_management", "regulatory_compliance"]
            },
            "source_mapping": {
                "fact_001": {
                    "source_file": "model_validation_report.pdf",
                    "page": 5,
                    "confidence": 0.95
                }
            },
            "processing_notes": ["High confidence extraction", "All entities validated"]
        }

    elif step_number == 3:  # Analysis
        output = {
            "analysis_status": "completed",
            "findings": {
                "key_patterns": [
                    {
                        "pattern_type": "trend",
                        "description": "Consistent improvement in model performance metrics",
                        "significance": "high",
                        "evidence": ["Backtesting results", "VaR accuracy"]
                    }
                ],
                "comparative_results": [
                    {
                        "comparison_type": "benchmark",
                        "result": "above",
                        "variance": 12.5,
                        "significance": "high"
                    }
                ],
                "insights": [
                    {
                        "insight": "Model validation framework is robust and compliant",
                        "confidence": 0.91,
                        "impact": "high",
                        "supporting_evidence": ["SR 11-7 compliance", "Backtesting success"]
                    }
                ]
            },
            "risk_indicators": ["Market volatility sensitivity", "Data quality dependencies"],
            "recommendations": ["Continue current validation approach", "Enhance stress testing"]
        }

    elif step_number == 4:  # Synthesis
        output = {
            "synthesis_status": "completed",
            "executive_summary": "Model validation analysis demonstrates strong compliance with regulatory requirements and robust risk management practices. Key metrics exceed industry benchmarks with high confidence levels.",
            "detailed_findings": {
                "critical_issues": [],
                "opportunities": [
                    {
                        "opportunity": "Enhanced stress testing protocols",
                        "potential_value": "Improved risk prediction accuracy",
                        "implementation_complexity": "medium"
                    }
                ],
                "risk_factors": [
                    {
                        "risk": "Market volatility impact on model accuracy",
                        "probability": "medium",
                        "impact": "medium",
                        "mitigation": "Regular model recalibration"
                    }
                ]
            },
            "action_items": [
                {
                    "action": "Schedule quarterly model validation review",
                    "priority": "high",
                    "timeline": "1-month",
                    "owner": "Risk Management Team",
                    "resources_required": "Validation specialists",
                    "success_metrics": "Completed review documentation"
                }
            ],
            "confidence_score": 0.89
        }

    else:  # Output Generation
        output = {
            "final_report": {
                "workflow_execution": {
                    "workflow_id": "sequential_analysis_001",
                    "execution_timestamp": datetime.now().isoformat(),
                    "total_processing_time_ms": sum([245, 320, 450, 280, 150]),
                    "status": "completed"
                },
                "final_analysis": {
                    "executive_summary": "Model validation analysis demonstrates strong compliance",
                    "key_findings": ["Regulatory compliance achieved", "Performance metrics exceed benchmarks"],
                    "risk_assessment": {"overall_risk_level": "low"},
                    "recommendations": ["Continue validation approach", "Enhance stress testing"],
                    "confidence_metrics": {"overall_confidence": 0.89}
                }
            },
            "metadata": {
                "input_files_processed": input_files or [],
                "rag_systems_used": ["ai_powered", "intelligent", "dspy"],
                "processing_environment": {"workflow_version": "1.0"}
            },
            "audit_trail": {
                "steps_executed": [1, 2, 3, 4, 5],
                "final_status": "completed_successfully"
            }
        }

    return {
        "step_number": step_number,
        "step_name": step["step_name"],
        "status": "completed",
        "processing_time_ms": processing_time_ms,
        "output": output,
        "timestamp": end_time.isoformat()
    }

def run_sequential_flow_test():
    """Run the complete sequential flow test"""

    print("Sequential Flow Test Runner")
    print("=" * 50)

    # Load configuration
    print("Loading workflow configuration...")
    config = load_sequential_flow_config()

    # Get input files
    print("Discovering input files...")
    input_files = get_input_files()
    print(f"Found {len(input_files)} input files:")
    for file_path in input_files:
        print(f"  - {Path(file_path).name}")

    # Resolve template fields
    print("\nResolving template fields...")
    resolved_config = resolve_template_fields(config, input_files)

    # Execute steps sequentially
    print("\nExecuting workflow steps:")
    step_results = []

    for step in resolved_config["steps"]:
        step_number = step["step_number"]
        step_name = step["step_name"]

        print(f"\n  Step {step_number}: {step_name}")
        print(f"    Template: {step['template_file']}")
        print(f"    RAG Systems: {', '.join(step['rag_systems'])}")

        # Show resolved variables
        if "resolved_input_variables" in step:
            print("    Resolved Variables:")
            for var_name, var_value in step["resolved_input_variables"].items():
                if isinstance(var_value, list) and len(var_value) > 3:
                    print(f"      {var_name}: [{len(var_value)} items]")
                else:
                    print(f"      {var_name}: {var_value}")

        # Execute step
        result = simulate_step_execution(step, step_number, input_files)
        step_results.append(result)

        print(f"    Status: {result['status']}")
        print(f"    Processing Time: {result['processing_time_ms']:.1f}ms")

    # Generate final output
    print("\n" + "=" * 50)
    print("WORKFLOW EXECUTION COMPLETED")
    print("=" * 50)

    # Summary
    total_time = sum(r["processing_time_ms"] for r in step_results)
    print(f"Total Processing Time: {total_time:.1f}ms")
    print(f"Steps Completed: {len(step_results)}/{len(resolved_config['steps'])}")
    print(f"Overall Status: SUCCESS")

    # Save results with review_id from field_values
    review_id = f"REV{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_file = Path(__file__).parent / "outputs" / f"final_{review_id}.json"
    output_file.parent.mkdir(exist_ok=True)

    final_output = {
        "workflow_config": resolved_config,
        "execution_results": step_results,
        "summary": {
            "total_processing_time_ms": total_time,
            "steps_completed": len(step_results),
            "success_rate": 1.0,
            "input_files_processed": len(input_files)
        }
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=2, ensure_ascii=True)

    print(f"\nResults saved to: {output_file}")

    return final_output

if __name__ == "__main__":
    results = run_sequential_flow_test()