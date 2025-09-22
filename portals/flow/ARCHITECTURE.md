# Flow Portal V4 - Technical Architecture

## 🏛️ Architectural Overview

Flow Portal V4 implements a **hexagonal clean architecture** with clear separation of concerns, modular components, and AI-first design principles.

```
┌─────────────────────────────────────────────────────────────────┐
│                         Presentation Layer                        │
│                    (Streamlit UI - flow_portal_v4.py)            │
├─────────────────────────────────────────────────────────────────┤
│                          Tab Modules                              │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                 │
│  │Create│ │Manage│ │ Run  │ │Optimize│ │Ask AI│                 │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘                 │
├─────────────────────────────────────────────────────────────────┤
│                       Application Services                        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │Card Library │ │Workflow Engine│ │RL Optimizer │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
├─────────────────────────────────────────────────────────────────┤
│                         Domain Core                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │Business Cards│ │  Workflows   │ │   Metrics    │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
├─────────────────────────────────────────────────────────────────┤
│                      Infrastructure Layer                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ File System  │ │ AI Providers │ │ RAG Systems  │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Directory Structure

```
portals/flow/
├── flow_portal_v4.py              # Main entry point
├── t_*.py                         # Tab modules (UI layer)
├── utils/                         # Shared utilities
│   ├── path_utils.py             # Path management
│   ├── script_discovery.py       # Dynamic module loading
│   ├── project_selector.py      # Project management
│   ├── data_handling.py         # Data operations
│   ├── fallback_patterns.py     # Error recovery
│   └── streamlit_helpers.py     # UI utilities
├── tidyllm/                      # Core framework
│   ├── workflows/               # Workflow storage
│   │   ├── global/             # Shared workflows
│   │   └── projects/           # Project-specific
│   ├── common/                 # Common utilities
│   └── domain/                 # Domain logic
└── portals/                     # Additional portal configs
```

## 🎯 Core Design Patterns

### 1. Tabfile Architecture Pattern

Each tab is a self-contained module with standard interface:

```python
# Tab Module Structure (t_*.py)
"""
Tab Name - Brief Description
"""
import streamlit as st
from typing import Dict, List, Any

def render_[tab_name]_tab():
    """Main entry point for tab rendering"""
    # Tab-specific initialization
    _initialize_tab_state()

    # Render UI components
    _render_header()
    _render_main_content()
    _render_footer()

def _initialize_tab_state():
    """Initialize session state for this tab"""
    if 'tab_state' not in st.session_state:
        st.session_state.tab_state = {}

# Private helper functions
def _render_header(): ...
def _render_main_content(): ...
def _render_footer(): ...
```

### 2. Business Card Pattern

Cards are composable units of functionality:

```python
class BusinessCard:
    """Atomic unit of workflow functionality"""

    def __init__(self, card_id: str, category: str):
        self.id = card_id
        self.category = category  # observe/orient/decide/act
        self.inputs = []          # Required inputs
        self.outputs = []         # Produced outputs
        self.ai_config = {}       # AI model configuration
        self.parameters = {}      # Card-specific parameters

    def validate(self, context: Dict) -> bool:
        """Validate card can execute in given context"""
        return all(inp in context for inp in self.inputs)

    def execute(self, context: Dict) -> Dict:
        """Execute card logic"""
        # 1. Action phase (data processing)
        action_result = self._perform_action(context)

        # 2. AI enhancement phase (if enabled)
        if self.ai_config.get('enabled'):
            ai_result = self._apply_ai(action_result)
            return ai_result

        return action_result
```

### 3. Workflow Composition Pattern

```python
class Workflow:
    """Composable workflow from cards"""

    def __init__(self, name: str):
        self.name = name
        self.cards = []          # List of BusinessCard instances
        self.context = {}        # Shared execution context
        self.metrics = {}        # Performance metrics

    def add_card(self, card: BusinessCard) -> bool:
        """Add card with validation"""
        if card.validate(self.context):
            self.cards.append(card)
            # Update context with card outputs
            self.context.update({out: None for out in card.outputs})
            return True
        return False

    def execute(self, inputs: Dict) -> Dict:
        """Execute workflow"""
        self.context.update(inputs)

        for card in self.cards:
            try:
                result = card.execute(self.context)
                self.context.update(result)
            except Exception as e:
                # Error recovery with fallback patterns
                self._handle_error(card, e)

        return self.context
```

## 🔌 Integration Points

### AI Provider Integration

```python
class AIProviderAdapter:
    """Adapter pattern for AI providers"""

    providers = {
        'openai': OpenAIProvider,
        'anthropic': AnthropicProvider,
        'local': LocalLLMProvider
    }

    def get_provider(self, provider_name: str):
        """Factory method for provider selection"""
        return self.providers[provider_name]()
```

### RAG System Integration

```python
class UnifiedRAGManager:
    """Unified interface for multiple RAG systems"""

    def __init__(self):
        self.systems = {
            'postgres_rag': PostgresRAGAdapter(),
            'ai_powered': AIPoweredRAGAdapter(),
            'llama_index': LlamaIndexAdapter(),
            'dspy': DSPyRAGAdapter(),
            'embedchain': EmbedchainAdapter(),
            'vector_db': VectorDBAdapter()
        }

    def query(self, system: str, query: str, **kwargs):
        """Route query to appropriate RAG system"""
        return self.systems[system].query(query, **kwargs)
```

## 🚀 Performance Optimizations

### 1. Lazy Loading Pattern

```python
# Main portal only loads active tab
def load_tab_module(tab_name: str):
    """Dynamic import for performance"""
    module = importlib.import_module(f't_{tab_name}')
    return module.render_tab
```

### 2. Caching Strategy

```python
@st.cache_data(ttl=3600)
def load_workflow_library(project: str):
    """Cache workflow data with TTL"""
    return load_workflows_from_disk(project)

@st.cache_resource
def get_ai_client():
    """Cache expensive AI client initialization"""
    return initialize_ai_client()
```

### 3. Async Execution

```python
async def execute_cards_parallel(cards: List[BusinessCard]):
    """Execute independent cards in parallel"""
    tasks = []
    for card in cards:
        if not card.depends_on:  # No dependencies
            tasks.append(asyncio.create_task(card.execute_async()))

    results = await asyncio.gather(*tasks)
    return results
```

## 🔐 Security Architecture

### Authentication & Authorization

```python
class SecurityManager:
    """Handle security concerns"""

    def validate_workflow(self, workflow: Dict) -> bool:
        """Validate workflow doesn't contain malicious code"""
        # Check for dangerous operations
        # Validate AI prompts for injection attacks
        # Verify file paths are within allowed directories
        pass

    def sanitize_inputs(self, inputs: Dict) -> Dict:
        """Sanitize user inputs"""
        # Remove potential script injections
        # Validate data types
        # Apply rate limiting
        pass
```

### Data Protection

- **Encryption at Rest**: Sensitive workflow data encrypted
- **Secure AI Communication**: TLS for all AI provider calls
- **Input Validation**: All user inputs sanitized
- **Path Traversal Prevention**: File operations restricted to allowed directories

## 📊 State Management

### Session State Architecture

```python
# Global session state structure
st.session_state = {
    'selected_project': str,          # Current project
    'workflows': Dict[str, Workflow], # Loaded workflows
    'current_workflow': Workflow,     # Active workflow
    'execution_state': Dict,          # Execution context
    'navigate_to_create': bool,       # Navigation flags
    'selected_cards': List[Card],     # Create tab state
    'optimization_metrics': Dict,     # Optimize tab state
    'ai_conversation': List[Dict],    # Ask AI tab history
}
```

### State Synchronization

```python
def sync_state_to_disk():
    """Persist critical state"""
    state_to_save = {
        'project': st.session_state.selected_project,
        'workflow': st.session_state.current_workflow,
        'timestamp': datetime.now()
    }
    save_to_json('.streamlit/session_state.json', state_to_save)

def restore_state_from_disk():
    """Restore state on reload"""
    if Path('.streamlit/session_state.json').exists():
        saved_state = load_from_json('.streamlit/session_state.json')
        st.session_state.update(saved_state)
```

## 🧪 Testing Architecture

### Unit Testing

```python
# Test individual cards
class TestBusinessCards(unittest.TestCase):
    def test_extract_document_card(self):
        card = ExtractDocumentCard()
        result = card.execute({'file': 'test.pdf'})
        self.assertIn('extracted_text', result)
```

### Integration Testing

```python
# Test workflow execution
class TestWorkflowExecution(unittest.TestCase):
    def test_complete_workflow(self):
        workflow = Workflow('test_workflow')
        workflow.add_card(ExtractCard())
        workflow.add_card(AnalyzeCard())
        result = workflow.execute({'input': 'data'})
        self.assertIsNotNone(result)
```

### Performance Testing

```python
# Benchmark critical paths
@pytest.mark.benchmark
def test_workflow_performance(benchmark):
    workflow = create_complex_workflow()
    result = benchmark(workflow.execute, test_data)
    assert result['execution_time'] < 5.0  # seconds
```

## 🔄 Deployment Architecture

### Container Structure

```dockerfile
FROM python:3.9-slim

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY portals/flow /app/portals/flow
COPY tidyllm /app/tidyllm

# Set working directory
WORKDIR /app/portals/flow

# Launch application
CMD ["streamlit", "run", "flow_portal_v4.py", "--server.port=8501"]
```

### Scalability Considerations

1. **Horizontal Scaling**: Stateless design allows multiple instances
2. **Load Balancing**: Round-robin distribution of requests
3. **Caching Layer**: Redis for shared state across instances
4. **Queue System**: Celery for async workflow execution
5. **Database**: PostgreSQL for persistent storage

## 📈 Monitoring & Observability

### Metrics Collection

```python
class MetricsCollector:
    """Collect and export metrics"""

    def track_execution(self, workflow: str, duration: float, success: bool):
        """Track workflow execution metrics"""
        metrics = {
            'workflow': workflow,
            'duration': duration,
            'success': success,
            'timestamp': datetime.now(),
            'project': st.session_state.selected_project
        }
        self.export_to_prometheus(metrics)
```

### Logging Strategy

```python
import logging

# Structured logging
logger = logging.getLogger(__name__)
logger.info("Workflow execution started", extra={
    'workflow_id': workflow.id,
    'user': user_id,
    'cards_count': len(workflow.cards)
})
```

## 🔮 Future Architecture Enhancements

### Planned Improvements

1. **Microservices Migration**: Separate card execution engine
2. **Event Sourcing**: Complete audit trail of all operations
3. **CQRS Pattern**: Separate read/write models for optimization
4. **GraphQL API**: For external integrations
5. **WebSocket Support**: Real-time execution updates
6. **Plugin Architecture**: Third-party card development

### Technology Considerations

- **Rust Backend**: High-performance card execution
- **WebAssembly**: Client-side card execution
- **Kubernetes**: Container orchestration
- **Apache Kafka**: Event streaming
- **TimescaleDB**: Time-series metrics storage

---

**Architecture Version**: 4.0
**Design Patterns**: Hexagonal, OODA Loop, Adapter, Factory, Observer
**Key Technologies**: Python, Streamlit, TidyLLM, AI/ML, RAG Systems
**Performance Target**: <1s load time, <5s workflow execution