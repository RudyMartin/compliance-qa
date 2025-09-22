# Workflow Creation Guide - Three Levels of AI Assistance

## Overview: Choose Your Level of Control

TidyLLM offers three distinct approaches to creating workflows, each with different levels of AI involvement. Choose based on how much control you want versus how much you want AI to decide.

---

## 🎯 Level 1: Action Steps (Full User Control)
**AI Involvement: Minimal - You build everything**

### What It Is
- Drag-and-drop pre-defined action blocks
- You control every step and parameter
- Like building with LEGO blocks

### Best For
- Users who know exactly what they want
- Compliance-critical workflows
- Standardized business processes

### How It Works
1. Select from library of action steps (ingest_docs, extract_terms, etc.)
2. Arrange them in your desired order
3. Configure each step's parameters manually
4. Save as reusable workflow

### Example
```
[Ingest Docs] → [Extract Key Terms] → [Score Risk] → [Generate Report]
```

---

## 📝 Level 2: Template Prompts (Guided AI Assistance)
**AI Involvement: Moderate - AI fills in the details**

### What It Is
- Start with prompt templates
- AI helps complete and optimize the workflow
- You guide, AI assists

### Best For
- Users who know the general approach
- Iterative refinement workflows
- Balanced control and automation

### How It Works
1. Choose a prompt template (e.g., "Analyze {document_type} for {risk_factors}")
2. Fill in the variables
3. AI suggests appropriate action steps
4. You approve or modify

### Example
Template: "Process invoice for compliance"
AI Suggests: Appropriate extraction fields, validation rules, and output format

---

## 🤖 Level 3: Ask AI (Full AI Automation)
**AI Involvement: Maximum - AI designs everything**

### What It Is
- Describe your goal in natural language
- AI creates the entire workflow
- Minimal user configuration needed

### Best For
- Exploratory workflows
- Quick prototypes
- When you want AI's best recommendation

### How It Works
1. Describe what you want: "I need to analyze customer feedback for sentiment"
2. AI creates complete workflow with all steps
3. Review and deploy

### Example
User: "Create a workflow to process insurance claims"
AI Creates: Complete workflow with document ingestion, data extraction, validation, risk scoring, and approval routing

---

## Quick Decision Guide

| Question | Action Steps | Template Prompts | Ask AI |
|----------|--------------|------------------|---------|
| Do you know exact steps? | ✅ | ⚠️ | ❌ |
| Need compliance control? | ✅ | ⚠️ | ❌ |
| Want AI suggestions? | ❌ | ✅ | ✅ |
| Building a prototype? | ❌ | ✅ | ✅ |
| Trust AI completely? | ❌ | ⚠️ | ✅ |

---

## Storage & Management

### Where Action Steps Are Stored
```
domain/
  workflows/
    projects/
      {workflow_id}/
        action_steps/     # Your custom action steps
        criteria/         # Evaluation criteria
        templates/        # Prompt templates
        inputs/          # Input files
```

### Import/Export Features
- **Export**: Bundle your action steps for sharing
- **Import**: Load action steps from:
  - actions_spec.json (system templates)
  - Business Builder blocks
  - Other projects (shared library)
  - Custom JSON files

---

## Integration with DSPy

All three levels ultimately generate DSPy signatures for execution:

1. **Action Steps** → Direct mapping to DSPy modules
2. **Template Prompts** → AI generates DSPy signatures from templates
3. **Ask AI** → Complete DSPy workflow generation

This ensures consistent execution regardless of creation method.

---

## Tips for Success

### Start Simple
- Begin with Action Steps to understand the system
- Move to Templates as you gain confidence
- Use Ask AI for experimentation

### Combine Approaches
- Create base with Action Steps
- Enhance with Template Prompts
- Let Ask AI suggest optimizations

### Version Control
- Export your workflows regularly
- Keep templates in version control
- Document custom action steps

---

## Summary

The three-tier system gives you complete flexibility:
- **Control freaks**: Use Action Steps
- **Collaborators**: Use Template Prompts
- **Innovators**: Use Ask AI

Choose your comfort level and build powerful workflows!