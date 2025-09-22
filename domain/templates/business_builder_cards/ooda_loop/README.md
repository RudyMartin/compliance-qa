# Business Builder Cards - OODA Loop Organization

## Overview

The Business Builder cards are organized using the OODA Loop framework (Observe, Orient, Decide, Act, Loop) to provide a structured approach to intelligent workflow creation and execution.

## OODA Loop Stages

### 🔍 **Observe Stage** (`/observe/`)
**Purpose**: Data gathering, monitoring, and initial processing
- **Focus**: Raw data acquisition and preparation
- **AI Involvement**: Moderate (quality assessment)
- **Cards**: Document extraction, unified document analysis
- **Outputs**: Raw data, extracted content, embeddings, metadata

### 🧠 **Orient Stage** (`/orient/`)
**Purpose**: Analysis, pattern recognition, and content understanding
- **Focus**: Understanding and contextualizing data
- **AI Involvement**: High (complex reasoning and pattern recognition)
- **Cards**: Content intelligence, entity extraction, sentiment analysis
- **Outputs**: Entities, classifications, patterns, relationships, context

### 💡 **Decide Stage** (`/decide/`)
**Purpose**: Decision-making, strategy formation, and recommendation generation
- **Focus**: Strategic decision-making and planning
- **AI Involvement**: Very High (strategic thinking and decision support)
- **Cards**: Insight synthesis, strategic recommendations
- **Outputs**: Decisions, strategies, recommendations, action plans, priorities

### ⚡ **Act Stage** (`/act/`)
**Purpose**: Execution, implementation, and action orchestration
- **Focus**: Implementation and execution
- **AI Involvement**: Moderate (monitoring and coordination)
- **Cards**: Workflow execution, action implementation
- **Outputs**: Results, outcomes, deliverables, metrics, status

### 🔄 **Loop Stage** (`/loop/`)
**Purpose**: Feedback, optimization, and continuous improvement
- **Focus**: Learning and optimization
- **AI Involvement**: Very High (learning algorithms and strategic improvement)
- **Cards**: RL optimization, performance analysis, feedback loops
- **Outputs**: Feedback, optimizations, improvements, learning, adaptations

## Unified Actions Architecture

All cards in this OODA organization use the **Unified Actions** architecture, which combines:
- **TidyLLM Functions**: Sovereign code for data processing and technical operations
- **AI Prompts**: Intelligence layer for analysis, reasoning, and decision-making

This revolutionary approach allows each card to seamlessly integrate technical processing with AI intelligence in a single step.

## Card Types

### Standard Cards
- Single-purpose actions (like the original `extract_document_text`)
- Traditional action-only or prompt-only steps

### Unified Cards
- **NEW**: Combine TidyLLM functions + AI analysis in one step
- Both `action` and `prompt` phases in the same step definition
- Optimal for complex workflows requiring both processing and intelligence

## Usage Patterns

### Linear OODA Flow
```
Observe → Orient → Decide → Act → Loop
```

### Parallel Processing
- Multiple Observe cards can run in parallel
- Orient cards can process different aspects simultaneously
- Decide stage synthesizes all inputs

### Iterative Improvement
- Loop stage feeds back to earlier stages
- RL optimization improves future cycles
- Continuous learning and adaptation

## Business Value

This OODA organization provides:
1. **Structured Thinking**: Clear progression from data to action
2. **Situational Awareness**: Comprehensive understanding before action
3. **Strategic Alignment**: Decisions based on thorough analysis
4. **Adaptive Learning**: Continuous improvement through feedback
5. **Unified Intelligence**: TidyLLM + AI integration for optimal performance

## Integration with Flow Creator V3

The OODA Loop organization seamlessly integrates with our Flow Creator V3 Modular system, providing business users with an intuitive framework for building intelligent workflows that progress naturally from observation to optimized action.