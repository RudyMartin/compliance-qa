# TidyLLM - Pure LLM & Vector Intelligence Library

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Pure Python library for LLM operations, RAG pipelines, and vector-based intelligence**
> Clean, reusable components without infrastructure dependencies.

## 🎯 Core Focus

```
TidyLLM = LLM + RAG + Vector Intelligence + Document Services
```

- **🤖 LLM Interface**: Chat, completion, and prompt engineering
- **📚 RAG Pipelines**: Retrieval-augmented generation orchestration
- **🔍 Vector Intelligence**: Embeddings, similarity search, vector operations
- **📄 Document Services**: Chunking, extraction, preprocessing for LLMs
- **✨ No Infrastructure**: Pure algorithms, no database/cloud dependencies

## ✅ Pure Library Architecture

TidyLLM is truly a pure library with NO infrastructure dependencies. Test it yourself:

```bash
python test_tidyllm_pure.py
```

**Test Results Confirm**:
- ✅ Core imports work without infrastructure
- ✅ Configuration uses injection pattern (no direct infrastructure imports)
- ✅ Pure text processing and RAG algorithms work independently
- ✅ Infrastructure packages (mlflow, psycopg2, boto3) available in environment but NOT imported by TidyLLM

TidyLLM is a clean, pure library focused on LLM/RAG/vector intelligence with configuration injected by the application layer.

## ⚡ Quick Start

```bash
pip install tidyllm
```

```python
from tidyllm import Chat, RAG, VectorStore

# Pure LLM interaction
chat = Chat()
response = chat.complete("Explain RAG in simple terms")

# RAG pipeline
rag = RAG()
rag.add_documents(["document.pdf"])
answer = rag.query("What are the key points?")

# Vector operations
vectors = VectorStore()
vectors.add_texts(["text1", "text2", "text3"])
similar = vectors.find_similar("query", k=3)

# Access enterprise gateways
ai_gateway = tidy.get_gateway('ai_processing')
db_gateway = tidy.get_gateway('database')
file_gateway = tidy.get_gateway('file_storage')

# DSPy-optimized workflows
from tidyllm.flow.agreements import CorporateAgreement
agreement = CorporateAgreement.document_processing()
setup = agreement.activate()

# Process documents with advanced RAG
from tidyllm.knowledge_systems import DocumentProcessor, EmbeddingProcessor
doc_processor = DocumentProcessor()
embed_processor = EmbeddingProcessor()

# Extract and embed documents
chunks = doc_processor.process_file("your_document.pdf")
embeddings = embed_processor.batch_embed([chunk.text for chunk in chunks])
```

## 🏗️ Enterprise Architecture

### Gateway System
```python
# AI Processing Gateway
ai_gateway = tidyllm.AIProcessingGateway(
    provider_config={'openai': {'api_key': 'your-key'}},
    fallback_providers=['anthropic', 'cohere']
)

# Database Gateway (supports multiple DBs)
db_gateway = tidyllm.DatabaseGateway({
    'primary': 'postgresql://user:pass@host:5432/db',
    'cache': 'redis://localhost:6379',
    'vector': 'pinecone://your-index'
})

# File Storage Gateway
storage_gateway = tidyllm.FileStorageGateway({
    's3': {'bucket': 'your-bucket', 'region': 'us-east-1'},
    'local': {'path': '/data/storage'}
})
```

### Knowledge Systems
```python
from tidyllm.knowledge_systems import DomainRAG, EnhancedExtraction

# Domain-specific RAG system
rag = DomainRAG(
    embedding_model='sentence-transformers/all-MiniLM-L6-v2',
    vector_store=db_gateway.get_vector_store(),
    chunk_size=512,
    overlap=100
)

# Enhanced document extraction
extractor = EnhancedExtraction()
documents = extractor.process_directory("./documents/", 
                                      formats=['pdf', 'docx', 'txt'])
```

### DSPy Workflow Orchestration
```python
from tidyllm.flow import execute_flow_command
from tidyllm.flow.agreements import DeveloperAgreement

# Predefined DSPy workflows
result = execute_flow_command("[Document Analysis]", {
    'input_dir': './documents',
    'output_format': 'structured_json',
    'include_entities': True
})

# Developer-friendly DSPy experiments
dev_agreement = DeveloperAgreement.ai_experimentation()
dspy_gateway = dev_agreement.get_gateway()
```

## 🧠 What's Inside

### Core Components

| Component | Description | Use Case |
|-----------|-------------|----------|
| **Gateways** | Unified API interfaces | AI services, databases, storage |
| **Knowledge Systems** | RAG and document processing | Enterprise search, QA systems |
| **Flow Agreements** | Pre-configured workflows | Corporate, developer, research use |
| **DSPy Integration** | Advanced prompt optimization | Production AI workflows |
| **CLI Interface** | Command-line tools | Automation and scripting |

### Gateway Types

```python
# Available gateways
gateways = tidyllm.get_global_registry()

# AI Processing
ai_gw = gateways.get('ai_processing')
response = ai_gw.chat("Analyze this document for key insights")

# Corporate LLM (compliance-aware)
corp_gw = gateways.get('corporate_llm') 
filtered_response = corp_gw.safe_completion(prompt, compliance_rules)

# Workflow Optimizer
optimizer = gateways.get('workflow_optimizer')
optimized_flow = optimizer.optimize_pipeline(steps)
```

## 🎓 Educational Examples

### Building a Corporate RAG System
```python
import tidyllm

# Enterprise setup with compliance
from tidyllm.flow.agreements import CorporateAgreement
corp_setup = CorporateAgreement.document_processing("ACME Corp").activate()

# Process confidential documents
processor = tidyllm.knowledge_systems.DocumentProcessor(
    chunk_size=1000,
    security_level='confidential'
)

# Extract with metadata preservation
chunks = processor.process_file("confidential_report.pdf")
embeddings = corp_setup.embed_processor.embed_chunks(chunks)

# Store in secure vector database
corp_setup.vector_store.store_embeddings(embeddings, metadata={
    'classification': 'confidential',
    'department': 'finance'
})
```

### DSPy-Powered Research Workflow
```python
from tidyllm.flow.agreements import DeveloperAgreement

# Set up research environment
research_env = DeveloperAgreement.ai_experimentation().activate()

# DSPy workflow for paper analysis
import dspy
from tidyllm.knowledge_systems import ResearchFramework

# Configure DSPy
dspy.configure(lm=research_env.llm, rm=research_env.retriever)

# Define research signature
class PaperAnalysis(dspy.Signature):
    """Analyze academic paper for key contributions and methodology"""
    paper_text = dspy.InputField()
    contributions = dspy.OutputField(desc="Key contributions")
    methodology = dspy.OutputField(desc="Research methodology")
    limitations = dspy.OutputField(desc="Study limitations")

# Execute with optimization
analyzer = dspy.ChainOfThought(PaperAnalysis)
result = analyzer(paper_text="Your academic paper content...")
```

## 🏭 Production Features

### Enterprise Security
- **Access Control**: Role-based gateway permissions
- **Audit Logging**: Complete request/response tracking  
- **Data Privacy**: GDPR/CCPA compliance tools
- **Encryption**: End-to-end data protection

### Scalability
- **Load Balancing**: Multi-provider fallbacks
- **Caching**: Intelligent response caching
- **Rate Limiting**: API usage management
- **Monitoring**: Performance metrics and alerting

### Integration
- **REST APIs**: HTTP endpoints for all gateways
- **Database Support**: PostgreSQL, MongoDB, Redis, Vector DBs
- **Cloud Storage**: AWS S3, Azure Blob, Google Cloud
- **AI Providers**: OpenAI, Anthropic, Cohere, local models

## 📦 TidyLLM Ecosystem

TidyLLM works seamlessly with the entire ecosystem:

```bash
# Core ML algorithms (zero dependencies)
pip install tlm

# Sentence embeddings  
pip install tidyllm-sentence

# Full enterprise platform
pip install tidyllm
```

**Dependency Chain**: `tlm` → `tidyllm-sentence` → `tidyllm`

## 🎯 Perfect For

- **🏢 Enterprise AI**: Production workflows with compliance
- **🔬 Research**: DSPy experimentation and optimization
- **📚 Education**: Learn enterprise AI architecture patterns
- **🚀 Startups**: Rapid AI prototype to production
- **🏫 Teaching**: Demonstrate real-world AI systems

## 🚀 Getting Started

1. **Install TidyLLM**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ tidyllm
   ```

2. **Initialize your environment**:
   ```python
   import tidyllm
   
   # Quick start with defaults
   tidy = tidyllm.TidyLLMInterface()
   
   # Or use pre-configured agreements
   from tidyllm.flow.agreements import CorporateAgreement
   setup = CorporateAgreement.document_processing().activate()
   ```

3. **Explore the CLI**:
   ```bash
   tidyllm --help
   tidyllm init-project my-ai-app
   tidyllm run-workflow document-analysis
   ```

## 🤝 Contributing

Part of the [TidyLLM ecosystem](https://github.com/RudyMartin/TidyLLM). Contributions welcome!

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by the TidyLLM Team**  
*DSPy-optimized workflows, enterprise-ready, educational by design*