# QA-Shipping System

A comprehensive AI-powered Quality Assurance and Compliance system built with hexagonal architecture for regulatory document processing, workflow automation, and multi-model AI orchestration.

## 🏗️ Architecture Overview

The system implements a 4-layer hexagonal (ports & adapters) architecture:

```
qa-shipping/
├── adapters/          # External interface implementations
│   ├── primary/       # User-facing adapters (CLI, API)
│   └── secondary/     # Infrastructure adapters (DB, external services)
├── application/       # Application services and use cases
│   ├── services/      # Application-level orchestration
│   └── use_cases/     # Business use case implementations
├── domain/            # Core business logic
│   ├── models/        # Domain entities and value objects
│   ├── services/      # Domain services
│   ├── ports/         # Interface definitions
│   └── workflows/     # Business workflow definitions
├── infrastructure/    # Technical infrastructure
│   ├── factories/     # Object creation and DI
│   └── services/      # Infrastructure services
├── common/            # Shared utilities
│   └── utilities/     # Common utility functions (path_manager, etc.)
├── portals/           # User interfaces
│   ├── chat/          # Streamlit chat interface
│   ├── flow/          # Workflow management UI
│   └── mlflow/        # MLflow experiment tracking
└── packages/          # External package dependencies
    ├── tlm/               # TLM package (separate repo)
    ├── tidyllm/           # TidyLLM package (separate repo)
    └── tidyllm-sentence/  # TidyLLM-Sentence package (separate repo)
```

## 📦 Package Dependencies

This system depends on three specialized packages, each maintained as separate repositories:

### 1. **TLM** (Tidy Language Models)
- **Repository**: [github.com/RudyMartin/tlm](https://github.com/RudyMartin/tlm)
- **Purpose**: Core LLM interface and model management
- **Features**: Unified API for multiple LLM providers, token management, prompt optimization
- **Special**: 100% Pure Python (no NumPy) - Faster performance with fewer bugs
- **Use Cases Where TLM Shines**:
  - Serverless functions - Minimal cold start
  - Edge deployment - No binary dependencies
  - Rapid prototyping - No setup headaches
  - Teaching/Learning - Readable, debuggable code
  - CI/CD pipelines - No build complications

### 2. **TidyLLM**
- **Repository**: [github.com/RudyMartin/TidyLLM](https://github.com/RudyMartin/TidyLLM)
- **Purpose**: Advanced LLM workflow orchestration
- **Features**: Chain-of-thought processing, document analysis, compliance checking

### 3. **TidyLLM-Sentence**
- **Repository**: [github.com/RudyMartin/tidyllm-sentence](https://github.com/RudyMartin/tidyllm-sentence)
- **Purpose**: Sentence-level embeddings and similarity analysis
- **Features**: Multiple embedding methods (TF-IDF, LSA, Transformer, Word2Vec)

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- Git
- pip or conda

### Step 1: Clone Main Repository
```bash
git clone https://github.com/RudyMartin/compliance-qa.git
cd qa-shipping
```

### Step 2: Install Package Dependencies

The system requires three package dependencies. You can install them either from PyPI or from source:

#### Option A: Install from PyPI (Recommended for users)
```bash
pip install tlm tidyllm tidyllm-sentence
```

#### Option B: Install from Source (Recommended for developers)
```bash
# Create packages directory
mkdir -p packages
cd packages

# Clone and install TLM
git clone https://github.com/RudyMartin/tlm.git
cd tlm
pip install -e .
cd ..

# Clone and install TidyLLM
git clone https://github.com/RudyMartin/TidyLLM.git
cd tidyllm
pip install -e .
cd ..

# Clone and install TidyLLM-Sentence
git clone https://github.com/RudyMartin/tidyllm-sentence.git
cd tidyllm-sentence
pip install -e .
cd ../..
```

### Step 3: Install Main System Requirements
```bash
# From qa-shipping root directory
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables
```bash
# Create .env file
cp .env.example .env

# Edit .env and add your API keys:
# - OPENAI_API_KEY=your-openai-key
# - ANTHROPIC_API_KEY=your-anthropic-key
# - AWS_ACCESS_KEY_ID=your-aws-key
# - AWS_SECRET_ACCESS_KEY=your-aws-secret
```

## 💻 Local Development Setup

### 1. Development Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

### 2. Running Tests
```bash
# Run all tests
pytest

# Run specific test module
pytest tests/domain/

# Run with coverage
pytest --cov=domain --cov=application
```

### 3. Code Quality Tools
```bash
# Format code
black .
ruff format .

# Lint code
ruff check .
mypy .

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

## 🎨 Streamlit UI Instructions

The system includes several Streamlit-based user interfaces for different functionalities:

### 1. Chat Portal (Main Interface)

The Chat Portal provides an interactive AI assistant for QA and compliance tasks:

```bash
# Start the Chat Portal
streamlit run portals/chat/unified_chat_portal.py

# Or with specific port
streamlit run portals/chat/unified_chat_portal.py --server.port 8501
```

**Features:**
- 💬 Interactive chat with AI models
- 📄 Document upload and analysis
- 🔍 Compliance checking
- 📊 Results visualization
- 💾 Session management

**Usage:**
1. Open browser to `http://localhost:8501`
2. Select AI model from sidebar (Claude Haiku/Sonnet/Opus)
3. Upload documents using the file uploader
4. Type questions or commands in the chat input
5. View results and download reports

### 2. Flow Portal (Workflow Management)

The Flow Portal manages and executes business workflows:

```bash
# Start the Flow Portal
streamlit run portals/flow/flow_portal_v4.py --server.port 8502
```

**Features:**
- 🔄 Workflow creation and editing
- ▶️ Workflow execution monitoring
- 📈 Performance metrics
- 🎯 A/B testing interface

**Workflow Types:**
- **Prompt Flows**: Single-prompt AI interactions
- **Step Flows**: Multi-step sequential workflows
- **Action Flows**: Complex business process automation

### 3. MLflow Dashboard (Experiment Tracking)

Track AI model experiments and performance:

```bash
# Start MLflow server
python portals/mlflow/start_mlflow_dashboard.py

# Access at http://localhost:5000
```

**Features:**
- 📊 Experiment tracking
- 🎯 Model performance comparison
- 📈 Metrics visualization
- 🗂️ Artifact storage

## 🎯 Key Features

### 1. Document Processing
- Multi-format support (PDF, Excel, JSON, CSV)
- Automatic content extraction
- Structure analysis
- Compliance checking against regulatory standards

### 2. AI Model Orchestration
- Multi-model support (OpenAI, Anthropic, Bedrock)
- A/B testing framework
- Performance optimization
- Cost tracking

### 3. Compliance & QA
- MVR (Model Validation Report) processing
- Regulatory compliance checking (MVS, VST standards)
- Automated QA checklists
- Finding classification and reporting

### 4. Workflow Automation
- Visual workflow builder
- Sequential and parallel execution
- Error handling and retry logic
- Audit trail generation

## 📝 Example Usage

### Basic Document Analysis
```python
from domain.services.model_risk_analysis import analyze_document

# Analyze a regulatory document
result = analyze_document(
    file_path="documents/mvr_report.pdf",
    compliance_standard="MVS_5.4.3"
)

print(f"Compliance Score: {result.compliance_score}")
print(f"Findings: {result.findings}")
```

### Running A/B Tests
```python
from domain.services.dual_ai_ab_testing import run_ab_test

# Compare different model configurations
results = run_ab_test(
    query="Analyze risk factors in this portfolio",
    models=["claude-haiku", "claude-sonnet"],
    document="portfolio_report.pdf"
)

print(f"Best performing model: {results.winner}")
print(f"Performance improvement: {results.improvement}%")
```

### Using the Chat Interface
```python
from portals.chat.chat_workflow_interface import ChatInterface

# Initialize chat interface
chat = ChatInterface()

# Process user query
response = chat.process_query(
    "Check this document for MVS compliance",
    uploaded_file="document.pdf"
)

print(response.answer)
print(f"Confidence: {response.confidence}")
```

## 🔧 Configuration

### System Configuration
Edit `infrastructure/config.yaml`:
```yaml
system:
  environment: development
  log_level: INFO

ai_models:
  default: claude-sonnet
  available:
    - claude-haiku
    - claude-sonnet
    - claude-opus
    - gpt-4

compliance:
  standards:
    - MVS_5.4.3
    - VST_3.0
    - SR_11-7
```

### Portal Configuration
Each portal has its own configuration in `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[server]
maxUploadSize = 200
enableCORS = false
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all three packages (tlm, tidyllm, tidyllm-sentence) are installed
   - Check Python path includes the packages directory

2. **API Key Errors**
   - Verify .env file exists and contains valid API keys
   - Check environment variables are loaded: `echo $ANTHROPIC_API_KEY`

3. **Streamlit Connection Issues**
   - Check if port is already in use: `lsof -i:8501`
   - Try different port: `streamlit run app.py --server.port 8502`

4. **Memory Issues**
   - Increase Python heap size: `export PYTHONMAXHEAP=4g`
   - Use smaller batch sizes in configuration

## 📚 Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Workflow Development](docs/WORKFLOWS.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Streamlit for UI components
- Powered by Anthropic Claude and OpenAI GPT models
- Uses MLflow for experiment tracking

## 📞 Support

For questions or issues:
- Create an issue in the repository
- Check the [FAQ](docs/FAQ.md)

---
*Last Updated: September 2025*