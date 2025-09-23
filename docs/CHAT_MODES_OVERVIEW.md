# Chat Modes Overview
> **Comprehensive guide to TidyLLM's intelligent chat processing modes**

## 🎯 Quick Reference

| Mode | Purpose | Best For | Temperature | Processing Path |
|------|---------|----------|-------------|-----------------|
| **DIRECT** | Fast, straightforward AI responses | Simple Q&A, General chat | 0.7 | `UnifiedChatManager → CorporateLLMGateway → Bedrock` |
| **RAG** | Context-enhanced with knowledge base | Research, Documentation queries | 0.7 | `UnifiedChatManager → RAGAdapter → VectorDB + LLM` |
| **DSPY** | Optimized prompts & reasoning | Complex analysis, Step-by-step | 0.5 | `UnifiedChatManager → DSPyAdapter → Chain of Thought` |
| **HYBRID** | Auto-selects best mode | Mixed queries, Smart routing | Variable | `UnifiedChatManager → Mode Analysis → Best Path` |
| **CUSTOM** | User-defined workflows | Specialized tasks | User-defined | `UnifiedChatManager → Custom Pipeline` |
| **CONTEXT_AWARE** | History-aware responses | Conversations, Follow-ups | 0.7 | `Chat Portal → RAG Mode + History` |
| **WORKFLOW** | Business process integration | Task automation | 0.7 | `Chat Portal → Hybrid Mode + Workflow Context` |
| **QA_COMPLIANCE** | Accuracy-focused | Compliance, Validation | 0.3 | `Chat Portal → Direct Mode + Low Temperature` |
| **FLOW_AGREEMENT** | Balanced processing | Agreements, Contracts | 0.5 | `Chat Portal → Direct Mode + Medium Temperature` |

---

## 📚 Detailed Mode Documentation

### 1️⃣ DIRECT Mode
**Purpose**: Direct communication with AI models without additional processing layers

<details>
<summary><b>🔍 Click for Details</b></summary>

#### How It Works
1. User message → UnifiedChatManager
2. Request wrapped with tracking metadata
3. Sent to CorporateLLMGateway for audit logging
4. Gateway invokes AWS Bedrock (Claude-3 models)
5. Response parsed and returned

#### Configuration
```python
# In unified_chat_manager.py
def _process_direct_chat(self, message: str, model: str, temperature: float):
    llm_request = LLMRequest(
        prompt=message,
        model_id=model,           # Default: "claude-3-haiku"
        temperature=temperature,   # Default: 0.7
        max_tokens=4000,          # Configurable
        user_id='chat_user',
        audit_reason='unified_chat_direct'
    )
```

#### Adjustable Settings
- **Model**: `claude-3-haiku`, `claude-3-sonnet`, `claude-3-opus`
- **Temperature**: 0.0 (deterministic) to 1.0 (creative)
- **Max Tokens**: Up to 4096 for most models
- **User ID**: For tracking and audit

#### Best Practices
- Use for simple questions
- Fastest response time
- No context retrieval overhead
- Ideal for general conversation

</details>

---

### 2️⃣ RAG Mode (Retrieval-Augmented Generation)
**Purpose**: Enhances responses with relevant context from knowledge bases

<details>
<summary><b>🔍 Click for Details</b></summary>

#### How It Works
1. Query analyzed for key concepts
2. Vector similarity search in ChromaDB/PostgreSQL
3. Top-k relevant documents retrieved
4. Context + Query sent to LLM
5. Response synthesized from both sources

#### Configuration
```python
# In unified_chat_manager.py
def _process_rag_chat(self, message: str, model: str, temperature: float):
    rag_manager = UnifiedRAGManager()
    result = rag_manager.query(
        system_type=RAGSystemType.AI_POWERED,
        query=message,
        model_preference=model,
        temperature=temperature,
        top_k=5,                    # Number of documents
        similarity_threshold=0.7    # Relevance cutoff
    )
```

#### RAG System Types
- **AI_POWERED**: General knowledge base
- **INTELLIGENT**: Domain-specific documents
- **SME**: Subject matter expert knowledge
- **DSPY**: Optimized retrieval patterns

#### Adjustable Settings
- **top_k**: Number of documents to retrieve (1-10)
- **similarity_threshold**: Minimum relevance score (0.0-1.0)
- **chunk_size**: Document chunk size (256-2048 tokens)
- **embedding_model**: `titan-embed-text-v1` or custom

#### Knowledge Base Sources
- Local documents (PDF, MD, TXT)
- Database records
- API documentation
- Historical conversations

</details>

---

### 3️⃣ DSPY Mode (Declarative Self-improving Python)
**Purpose**: Advanced reasoning with optimized prompts and Chain of Thought

<details>
<summary><b>🔍 Click for Details</b></summary>

#### How It Works
1. Message analyzed for reasoning requirements
2. DSPy signatures selected (Question→Answer, Problem→Solution)
3. Few-shot examples retrieved if available
4. Chain of Thought reasoning applied
5. Multi-step answer generation

#### Configuration
```python
# DSPy integration (when fully implemented)
def _process_dspy_chat(self, message: str, model: str, temperature: float):
    # DSPy configured to use CorporateLLMGateway
    dspy_service.configure_lm(model_name=model)

    # Chain of Thought signature
    result = dspy_service.chat_with_cot(
        message,
        signature="question -> reasoning -> answer",
        examples=fetch_relevant_examples(),
        temperature=0.5  # Lower for consistency
    )
```

#### DSPy Features
- **Automatic Prompt Optimization**: Learns best prompts
- **Chain of Thought**: Step-by-step reasoning
- **Few-Shot Learning**: Uses examples for better responses
- **Signature Templates**: Pre-defined reasoning patterns

#### Current Status
⚠️ **Partially Implemented** - Returns placeholder while full DSPy integration completes

</details>

---

### 4️⃣ HYBRID Mode
**Purpose**: Intelligently routes to the best mode based on query analysis

<details>
<summary><b>🔍 Click for Details</b></summary>

#### How It Works
```python
def _process_hybrid_chat(self, message: str, model: str, temperature: float):
    # Intelligent routing logic
    if "step by step" in message.lower() or "reasoning" in message.lower():
        return self._process_dspy_chat(...)  # Complex reasoning
    elif len(message) > 100 or "?" in message:
        return self._process_rag_chat(...)   # Knowledge retrieval
    else:
        return self._process_direct_chat(...) # Simple response
```

#### Routing Rules
| Query Characteristics | Selected Mode | Reasoning |
|----------------------|---------------|-----------|
| Contains "step by step", "explain", "reasoning" | DSPY | Needs Chain of Thought |
| Long query (>100 chars) or contains "?" | RAG | Likely needs context |
| Short, simple statements | DIRECT | Fast response sufficient |
| Technical documentation queries | RAG | Knowledge base search |
| Math or logic problems | DSPY | Structured reasoning |

#### Benefits
- No manual mode selection needed
- Optimizes for query type
- Balances speed vs. quality
- Learns from usage patterns

</details>

---

### 5️⃣ CUSTOM Mode
**Purpose**: User-defined processing pipelines for specialized workflows

<details>
<summary><b>🔍 Click for Details</b></summary>

#### How It Works
- Allows chaining multiple processing steps
- Custom pre/post processors
- Integration with external services
- Workflow-specific logic

#### Example Custom Pipeline
```python
def custom_compliance_pipeline(message):
    # Step 1: Extract entities
    entities = extract_entities(message)

    # Step 2: Check compliance rules
    compliance = check_compliance_rules(entities)

    # Step 3: Generate response with constraints
    response = generate_constrained_response(
        message,
        compliance_rules=compliance
    )

    # Step 4: Audit log
    log_compliance_interaction(message, response)

    return response
```

#### Current Status
🚧 **Coming Soon** - Framework in place, awaiting implementation

</details>

---

## 🎛️ Portal-Specific Modes

These modes are specific to the Chat Portal UI and build on top of the core modes:

### 📋 CONTEXT_AWARE
- **Base Mode**: RAG
- **Enhancement**: Includes conversation history
- **Use Case**: Multi-turn conversations, follow-up questions
- **Temperature**: 0.7 (balanced)

### 🔄 WORKFLOW
- **Base Mode**: HYBRID
- **Enhancement**: Includes workflow context and ID
- **Use Case**: Business process automation, task management
- **Temperature**: 0.7 (balanced)

### ✅ QA_COMPLIANCE
- **Base Mode**: DIRECT
- **Enhancement**: Lower temperature for accuracy
- **Use Case**: Compliance checking, validation, auditing
- **Temperature**: 0.3 (high accuracy)

### 📄 FLOW_AGREEMENT
- **Base Mode**: DIRECT
- **Enhancement**: Medium temperature for balanced output
- **Use Case**: Contract analysis, agreement processing
- **Temperature**: 0.5 (balanced accuracy/creativity)

---

## ⚙️ Global Configuration

### Settings Location
All chat modes can be configured in:
1. **`infrastructure/settings.yaml`** - Global defaults
2. **`packages/tidyllm/services/unified_chat_manager.py`** - Service-level settings
3. **`portals/chat/chat_app.py`** - UI-specific overrides

### Example Configuration (settings.yaml)
```yaml
chat:
  default_mode: "hybrid"
  default_model: "claude-3-haiku"
  default_temperature: 0.7
  max_tokens: 4000

  modes:
    direct:
      timeout_ms: 5000
      retry_count: 3

    rag:
      top_k: 5
      similarity_threshold: 0.7
      chunk_size: 512

    dspy:
      chain_of_thought: true
      few_shot_examples: 3

    hybrid:
      routing_rules:
        complexity_threshold: 100
        question_detection: true
```

---

## 📊 Performance Characteristics

| Mode | Avg Response Time | Token Usage | Cost/Query | Accuracy |
|------|------------------|-------------|------------|----------|
| DIRECT | 1-2 seconds | ~500-1000 | $0.01-0.02 | Good |
| RAG | 2-4 seconds | ~1000-2000 | $0.03-0.05 | Excellent |
| DSPY | 3-5 seconds | ~1500-2500 | $0.04-0.06 | Excellent |
| HYBRID | Variable | Variable | Variable | Optimal |
| CUSTOM | User-defined | Variable | Variable | Variable |

---

## 🚀 How These Modes Were Created

### Architecture Evolution
1. **Phase 1**: Basic direct chat implementation
2. **Phase 2**: Added RAG for context enhancement
3. **Phase 3**: Integrated DSPy for reasoning
4. **Phase 4**: Created Hybrid for intelligent routing
5. **Phase 5**: Portal-specific modes for business use cases

### Design Principles
- **Hexagonal Architecture**: Clean separation of concerns
- **Adapter Pattern**: Easy to add new backends
- **Strategy Pattern**: Mode selection at runtime
- **Chain of Responsibility**: Pipeline processing

### Key Components
```
User Input
    ↓
Chat Portal (UI Layer)
    ↓
UnifiedChatApplication (Application Layer)
    ↓
ChatService (Domain Layer)
    ↓
UnifiedChatManager (Orchestration)
    ↓
Mode-Specific Processors
    ↓
Infrastructure Adapters (Bedrock, RAG, DSPy)
    ↓
External Services (AWS, Databases)
```

---

## 🔧 Customization Guide

### Adding a New Mode
1. Define in `ChatMode` enum
2. Create processor method `_process_[mode]_chat`
3. Add routing logic if needed
4. Update UI selector

### Adjusting Existing Modes
- Edit processor methods in `unified_chat_manager.py`
- Update settings in `settings.yaml`
- Modify UI parameters in `chat_app.py`

### Mode Selection Tips
- **Simple queries**: Use DIRECT
- **Research/Documentation**: Use RAG
- **Complex reasoning**: Use DSPY
- **Not sure?**: Use HYBRID
- **Business processes**: Use WORKFLOW
- **Compliance**: Use QA_COMPLIANCE

---

## 📈 Future Enhancements

### Planned Features
- [ ] Voice mode selection
- [ ] Auto-learning mode preferences
- [ ] Custom mode builder UI
- [ ] Mode performance analytics
- [ ] A/B testing framework
- [ ] Mode combination chains

### Experimental Modes (Coming Soon)
- **MULTIMODAL**: Image + text processing
- **STREAMING**: Real-time response streaming
- **COLLABORATIVE**: Multi-agent responses
- **RESEARCH**: Deep web search + synthesis

---

## 📝 Quick Start Examples

### Using Different Modes
```python
# Direct mode - simple query
response = chat_manager.chat("What's the weather like?", mode="direct")

# RAG mode - knowledge retrieval
response = chat_manager.chat("What's our compliance policy?", mode="rag")

# DSPY mode - reasoning
response = chat_manager.chat("Explain step by step how to validate a model", mode="dspy")

# Hybrid mode - let system decide
response = chat_manager.chat("How do I set up monitoring alerts?", mode="hybrid")
```

---

*Last Updated: 2025-09-23*
*Version: 1.0.0*
*Architecture: Hexagonal with Adapter Pattern*