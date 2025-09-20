#!/usr/bin/env python3
"""
DSPy Compiler Service
=====================
Compiles markdown definitions into DSPy programs.
Handles parsing, validation, and code generation.
"""

import re
import yaml
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json
from pathlib import Path

@dataclass
class DSPyProgramSpec:
    """Specification for a DSPy program."""
    name: str
    objective: str
    inputs: Dict[str, str]
    outputs: Dict[str, str]
    process_steps: List[str]
    constraints: List[str]
    task_type: str  # analysis, action, calculation, etc.

class DSPyCompilerService:
    """Compiles markdown to DSPy programs."""

    def __init__(self):
        self.templates = self._load_templates()
        self.program_cache = {}

    def _load_templates(self) -> Dict[str, str]:
        """Load pre-defined templates."""
        return {
            "compliance_check": self._get_compliance_template(),
            "document_qa": self._get_document_qa_template(),
            "data_analysis": self._get_data_analysis_template(),
            "risk_assessment": self._get_risk_assessment_template(),
            "mvr_review": self._get_mvr_review_template()
        }

    def parse_markdown(self, markdown_text: str) -> Dict[str, Any]:
        """Parse markdown definition into structured format."""
        try:
            # Extract sections
            spec = self._extract_specification(markdown_text)

            # Generate DSPy program
            dspy_code = self._generate_dspy_code(spec)

            # Extract metadata
            signatures = self._extract_signatures(spec)
            modules = self._determine_modules(spec)

            return {
                'valid': True,
                'spec': spec,
                'dspy_program': dspy_code,
                'signatures': signatures,
                'modules': modules,
                'task_type': spec.task_type
            }

        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }

    def _extract_specification(self, markdown: str) -> DSPyProgramSpec:
        """Extract structured specification from markdown."""

        # Parse sections using regex
        name = self._extract_section(markdown, "^#\\s+(.+)$", default="Unnamed Program")
        objective = self._extract_section(markdown, "##\\s+Objective\\s*(.+?)(?=##|$)", default="")

        # Parse inputs
        inputs_text = self._extract_section(markdown, "##\\s+Input[s]?\\s*(.+?)(?=##|$)", default="")
        inputs = self._parse_field_list(inputs_text)

        # Parse outputs
        outputs_text = self._extract_section(markdown, "##\\s+Output[s]?\\s*(.+?)(?=##|$)", default="")
        outputs = self._parse_field_list(outputs_text)

        # Parse process steps
        process_text = self._extract_section(markdown, "##\\s+(?:Process|Steps)\\s*(.+?)(?=##|$)", default="")
        process_steps = self._parse_numbered_list(process_text)

        # Parse constraints
        constraints_text = self._extract_section(markdown, "##\\s+Constraint[s]?\\s*(.+?)(?=##|$)", default="")
        constraints = self._parse_bullet_list(constraints_text)

        # Determine task type
        task_type = self._determine_task_type(objective, process_steps)

        return DSPyProgramSpec(
            name=name.strip(),
            objective=objective.strip(),
            inputs=inputs,
            outputs=outputs,
            process_steps=process_steps,
            constraints=constraints,
            task_type=task_type
        )

    def _extract_section(self, text: str, pattern: str, default: str = "") -> str:
        """Extract a section using regex."""
        match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
        return match.group(1) if match else default

    def _parse_field_list(self, text: str) -> Dict[str, str]:
        """Parse a list of fields (name: description format)."""
        fields = {}
        lines = text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('-'):
                line = line[1:].strip()

            if ':' in line:
                name, desc = line.split(':', 1)
                fields[name.strip()] = desc.strip()
            elif line:
                # Simple field name without description
                fields[line.strip()] = f"{line.strip()} input"

        return fields

    def _parse_numbered_list(self, text: str) -> List[str]:
        """Parse numbered list items."""
        steps = []
        lines = text.strip().split('\n')

        for line in lines:
            line = line.strip()
            # Match patterns like "1.", "1)", "Step 1:", etc.
            if re.match(r'^\d+[\.)\s]', line):
                step_text = re.sub(r'^\d+[\.)\s]+(?:Step\s+\d+:?\s*)?', '', line)
                steps.append(step_text.strip())
            elif line.startswith('**') and line.endswith('**'):
                # Handle bold step headers
                steps.append(line.strip('*').strip())

        return steps

    def _parse_bullet_list(self, text: str) -> List[str]:
        """Parse bullet point list."""
        items = []
        lines = text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('*'):
                items.append(line[1:].strip())

        return items

    def _determine_task_type(self, objective: str, steps: List[str]) -> str:
        """Determine the type of task based on content."""
        objective_lower = objective.lower()
        steps_text = ' '.join(steps).lower()

        if 'analyz' in objective_lower or 'analyz' in steps_text:
            return 'analysis'
        elif 'generat' in objective_lower or 'create' in objective_lower:
            return 'generation'
        elif 'check' in objective_lower or 'validat' in objective_lower:
            return 'validation'
        elif 'calculat' in objective_lower or 'comput' in objective_lower:
            return 'calculation'
        else:
            return 'general'

    def _generate_dspy_code(self, spec: DSPyProgramSpec) -> str:
        """Generate DSPy Python code from specification."""

        code = f'''import dspy

class {self._to_class_name(spec.name)}(dspy.Signature):
    """
    {spec.objective}
    """

    # Input fields
'''

        for field_name, field_desc in spec.inputs.items():
            safe_name = self._to_variable_name(field_name)
            code += f'    {safe_name} = dspy.InputField(desc="{field_desc}")\n'

        code += '\n    # Output fields\n'

        for field_name, field_desc in spec.outputs.items():
            safe_name = self._to_variable_name(field_name)
            code += f'    {safe_name} = dspy.OutputField(desc="{field_desc}")\n'

        # Add module initialization
        module_type = self._get_module_type(spec.task_type)

        code += f'''

# Initialize the DSPy module
{self._to_variable_name(spec.name)}_module = dspy.{module_type}({self._to_class_name(spec.name)})

# Process steps as documentation
"""
Process Steps:
'''

        for i, step in enumerate(spec.process_steps, 1):
            code += f'{i}. {step}\n'

        if spec.constraints:
            code += '\nConstraints:\n'
            for constraint in spec.constraints:
                code += f'- {constraint}\n'

        code += '"""'

        return code

    def _to_class_name(self, name: str) -> str:
        """Convert name to valid Python class name."""
        # Remove special characters and convert to CamelCase
        words = re.findall(r'\w+', name)
        return ''.join(word.capitalize() for word in words)

    def _to_variable_name(self, name: str) -> str:
        """Convert name to valid Python variable name."""
        # Remove special characters and convert to snake_case
        name = re.sub(r'[^\w\s]', '', name)
        words = name.lower().split()
        return '_'.join(words)

    def _get_module_type(self, task_type: str) -> str:
        """Get appropriate DSPy module type for task."""
        module_map = {
            'analysis': 'ChainOfThought',
            'generation': 'ChainOfThought',
            'validation': 'ReAct',
            'calculation': 'ProgramOfThought',
            'general': 'Predict'
        }
        return module_map.get(task_type, 'ChainOfThought')

    def _extract_signatures(self, spec: DSPyProgramSpec) -> List[str]:
        """Extract signature information."""
        signatures = []

        for input_name in spec.inputs:
            signatures.append(f"Input: {input_name}")

        for output_name in spec.outputs:
            signatures.append(f"Output: {output_name}")

        return signatures

    def _determine_modules(self, spec: DSPyProgramSpec) -> List[str]:
        """Determine which DSPy modules to use."""
        modules = [self._get_module_type(spec.task_type)]

        # Add additional modules based on task characteristics
        if len(spec.process_steps) > 3:
            modules.append("ChainOfThought")

        if any('reason' in step.lower() for step in spec.process_steps):
            modules.append("ReAct")

        return list(set(modules))

    def save_program(self, name: str, description: str, markdown: str, dspy_program: str) -> bool:
        """Save a DSPy program to the library."""
        try:
            program_id = self._generate_program_id(name)

            self.program_cache[program_id] = {
                'id': program_id,
                'name': name,
                'description': description,
                'markdown': markdown,
                'dspy_program': dspy_program,
                'created_at': Path.cwd()  # Would use datetime in production
            }

            return True
        except Exception:
            return False

    def _generate_program_id(self, name: str) -> str:
        """Generate unique program ID."""
        import hashlib
        return hashlib.md5(name.encode()).hexdigest()[:8]

    def list_saved_programs(self) -> List[Dict[str, Any]]:
        """List all saved programs."""
        return list(self.program_cache.values())

    def delete_program(self, program_id: str) -> bool:
        """Delete a saved program."""
        if program_id in self.program_cache:
            del self.program_cache[program_id]
            return True
        return False

    # Template methods
    def _get_compliance_template(self) -> str:
        return """# Compliance Validation

## Objective
Check documents against regulatory requirements.

## Inputs
- document: The document to validate
- standards: Compliance standards to check against

## Process
1. Extract relevant sections from document
2. Check each requirement against content
3. Identify gaps and missing information
4. Calculate compliance score

## Outputs
- compliance_status: COMPLIANT or NON-COMPLIANT
- score: Compliance percentage
- gaps: List of missing requirements
- recommendations: How to achieve compliance

## Constraints
- Must check all mandatory requirements
- Provide specific evidence for each finding
- Include regulatory references"""

    def _get_document_qa_template(self) -> str:
        return """# Document Question Answering

## Objective
Answer questions about uploaded documents accurately.

## Inputs
- document: Document to analyze
- question: User's question

## Process
1. Parse and understand the question
2. Find relevant sections in document
3. Extract key information
4. Formulate comprehensive answer

## Outputs
- answer: Direct answer to the question
- confidence: Confidence score (0-1)
- sources: Document sections used
- additional_context: Related information

## Constraints
- Answer must be based on document content
- Cite specific sections
- Acknowledge if information not found"""

    def _get_data_analysis_template(self) -> str:
        return """# Data Analysis

## Objective
Analyze data and provide insights.

## Inputs
- data: Dataset to analyze
- analysis_type: Type of analysis requested

## Process
1. Load and validate data
2. Perform statistical analysis
3. Identify patterns and anomalies
4. Generate insights

## Outputs
- summary: Executive summary
- statistics: Key metrics
- insights: Main findings
- visualizations: Chart specifications

## Constraints
- Handle missing data appropriately
- Provide confidence intervals
- Flag any data quality issues"""

    def _get_risk_assessment_template(self) -> str:
        return """# Risk Assessment

## Objective
Assess risks in the provided context.

## Inputs
- context: Situation or document to assess
- risk_framework: Framework to apply (e.g., operational, credit, market)
- threshold: Risk tolerance level

## Process
1. Identify potential risk factors
2. Assess likelihood and impact
3. Calculate risk scores
4. Prioritize by severity

## Outputs
- risk_level: Overall risk rating (Low/Medium/High/Critical)
- risk_factors: List of identified risks
- scores: Individual risk scores
- mitigation: Recommended actions

## Constraints
- Use established risk frameworks
- Provide quantitative scores where possible
- Include both inherent and residual risk"""

    def _get_mvr_review_template(self) -> str:
        return """# MVR Document Review

## Objective
Review Model Validation Report for compliance and completeness.

## Inputs
- mvr_document: The MVR to review
- validation_standards: MVS/VST standards to check

## Process
1. Extract model documentation sections
2. Check methodology completeness
3. Validate testing procedures
4. Assess compliance with standards

## Outputs
- validation_status: APPROVED or NEEDS_REVISION
- findings: List of issues found
- compliance_scores: Score for each standard
- action_items: Required corrections

## Constraints
- Must cover all MVS 5.4.3 requirements
- Check VST Section 3-5 compliance
- Provide specific remediation steps"""