# Portal Requirements & Functions Documentation

## 1. CHAT PORTAL (Priority 1)

### Required Backend Functions:
```python
# Core Chat Functions
- initialize_chat_manager() -> ChatManager
- get_available_models() -> List[str]  # Returns 4 Claude models
- get_chat_modes() -> List[str]  # direct, rag, dspy, hybrid, custom
- send_message(message: str, model: str, mode: str, params: dict) -> str
- stream_message(message: str, model: str, mode: str, params: dict) -> Generator
- clear_conversation() -> bool
- save_conversation(filename: str) -> bool
- load_conversation(filename: str) -> List[dict]
- get_conversation_history() -> List[dict]
- export_to_mlflow() -> bool
```

### Required UI Components:
- Model selector dropdown (4 Claude models)
- Chat mode selector (5 modes)
- Temperature slider (0.0-1.0)
- Max tokens slider (100-4000)
- Top-p slider (0.0-1.0)
- Reasoning toggle
- Streaming toggle
- History toggle
- Message input box
- Send button
- Clear button
- Export button

### Tests Needed:
1. Test model initialization
2. Test each chat mode
3. Test parameter validation
4. Test message sending
5. Test streaming
6. Test conversation management
7. Test MLflow export
8. Test error handling

---

## 2. RAG PORTAL (Priority 2)

### Required Backend Functions:
```python
# Document Management
- upload_document(file) -> bool
- list_documents() -> List[dict]
- delete_document(doc_id: str) -> bool
- preview_document(doc_id: str) -> str

# Embedding Functions
- generate_embeddings(doc_id: str) -> bool
- get_embedding_status() -> dict
- configure_embedding_model(model: str) -> bool

# Vector Database
- store_embeddings(embeddings) -> bool
- search_similar(query: str, k: int) -> List[dict]
- get_vector_db_stats() -> dict

# RAG Pipeline
- configure_rag_pipeline(config: dict) -> bool
- test_rag_query(query: str) -> dict
- get_rag_metrics() -> dict
```

### Required UI Components:
- Document upload area
- Document list with actions
- Embedding model selector
- Chunking strategy selector
- Vector DB configuration
- Search interface
- Results display
- Pipeline configuration
- Metrics dashboard

### Tests Needed:
1. Test document upload
2. Test embedding generation
3. Test vector storage
4. Test similarity search
5. Test RAG pipeline
6. Test different chunking strategies
7. Test retrieval accuracy

---

## 3. WORKFLOW PORTAL (Priority 3)

### Required Backend Functions:
```python
# Flow Management
- create_flow(name: str, description: str) -> str
- list_flows() -> List[dict]
- get_flow(flow_id: str) -> dict
- delete_flow(flow_id: str) -> bool
- duplicate_flow(flow_id: str) -> str

# Node Operations
- add_node(flow_id: str, node_type: str, config: dict) -> str
- remove_node(flow_id: str, node_id: str) -> bool
- connect_nodes(flow_id: str, source: str, target: str) -> bool
- configure_node(flow_id: str, node_id: str, config: dict) -> bool

# Execution
- validate_flow(flow_id: str) -> dict
- execute_flow(flow_id: str, input_data: dict) -> dict
- get_execution_status(execution_id: str) -> dict
- get_execution_logs(execution_id: str) -> List[str]

# Templates
- get_flow_templates() -> List[dict]
- create_from_template(template_id: str) -> str
```

### Required UI Components:
- Flow designer canvas
- Node palette
- Properties panel
- Connection tool
- Validation indicator
- Execute button
- Logs viewer
- Template gallery
- Save/Load buttons

### Tests Needed:
1. Test flow creation
2. Test node operations
3. Test connections
4. Test flow validation
5. Test flow execution
6. Test template usage
7. Test error handling

---

## 4. QA PORTAL

### Required Backend Functions:
```python
# QA Processing
- analyze_document(doc) -> dict
- classify_findings(findings: List) -> dict
- generate_score(analysis: dict) -> float
- create_report(analysis: dict) -> str

# Compliance
- check_compliance(doc, rules) -> dict
- get_compliance_rules() -> List[dict]
- update_rules(rules: dict) -> bool
```

### Required UI Components:
- Document upload
- Analysis dashboard
- Findings list
- Score display
- Report generator
- Rules editor

---

## 5. DSPY PORTAL

### Required Backend Functions:
```python
# DSPy Configuration
- compile_dspy_program(config: str) -> dict
- optimize_prompts(program: dict) -> dict
- evaluate_performance(program: dict) -> dict
- save_program(program: dict) -> bool
```

### Required UI Components:
- DSPy editor
- Compile button
- Optimization panel
- Metrics display
- Save/Load

---

## 6. SETUP PORTAL (COMPLETED)

### Already Implemented:
- installation_wizard()
- dependency_check()
- database_initialization()
- tidyllm_basic_setup()
- health_check()
- load_examples()
- portal_guide()

### UI Already Has:
- Step-by-step wizard
- Check buttons
- Results persistence
- Portal guide
- Clear next steps

---

## IMPLEMENTATION PLAN

### Phase 1: Chat Portal (NOW)
1. ✅ Document required functions
2. Run functional tests
3. Create chat service if needed
4. Build Streamlit UI
5. Test complete portal

### Phase 2: RAG Portal
1. Document functions
2. Create functional tests
3. Build RAG service
4. Create Streamlit UI
5. Integration testing

### Phase 3: Workflow Portal
1. Document functions
2. Create functional tests
3. Build workflow engine
4. Create visual designer
5. End-to-end testing

### Phase 4: Remaining Portals
1. QA Portal
2. DSPy Portal
3. Final integration

---

## SUCCESS CRITERIA

Each portal must have:
- ✅ All backend functions working
- ✅ Real tests passing (no mocks)
- ✅ Streamlit UI with all components
- ✅ Error handling
- ✅ User-friendly interface
- ✅ Clear documentation