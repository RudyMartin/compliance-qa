# Compliance QA Launchers Guide

## Web App Launchers (*_app.py)

These launch interactive web interfaces (Streamlit portals):

| Launcher | Description | Port | Type |
|----------|-------------|------|------|
| `start_setup_app.py` | Main setup and configuration portal | 8501 | Web Portal |
| `run_first_time_setup_app.py` | First-time setup (modular 5-tab wizard) | 8512 | Web Portal |
| `run_chat_app.py` | Chat Test Portal - Interactive chat interface | 8502 | Web Portal |
| `run_flow_app.py` | Flow Creator - Workflow management portal | 8550 | Web Portal |
| `run_rag_app.py` | RAG Portal - Knowledge base management | 8525 | Web Portal |
| `run_rag_creator_app.py` | RAG Creator V3 - Advanced RAG system builder | 8526 | Web Portal |
| `run_rag_unified_app.py` | Unified RAG Portal - Manages all 5 RAG systems | 8527 | Web Portal |

## CLI Tools (*_cli.py)

These are command-line tools, scripts, and servers:

### Root Directory
| Launcher | Description | Port | Type |
|----------|-------------|------|------|
| `run_mlflow_cli.py` | MLflow tracking server dashboard | 5000 | CLI/Server |
| `setup_aws_credentials_cli.py` | Interactive AWS credential setup | N/A | CLI Tool |

### Infrastructure Tools
| Tool | Description | Location |
|------|-------------|----------|
| `install_packages_cli.py` | Install core packages (tlm, tidyllm, tidyllm-sentence) | infrastructure/ |
| `make_scripts_cli.py` | Generate environment setup scripts from settings.yaml | infrastructure/ |
| `generate_template_cli.py` | Generate blank configuration template with placeholders | infrastructure/setup/ |

### Other CLI Tools
| Tool | Description | Location |
|------|-------------|----------|
| `workflow_cli.py` | Workflow management CLI | cli/ |
| `rag2dag_cli.py` | RAG to DAG conversion tool | cli/ |
| Various scripts | Analysis and debugging scripts | domain/scripts/ |

## How to Use

### From Root Directory (Recommended)
Always launch from the `C:\Users\marti\compliance-qa` directory:

```bash
# Web Apps (Streamlit Portals)
python start_setup_app.py       # Main setup portal
python run_chat_app.py          # Chat interface
python run_flow_app.py          # Flow creator
python run_rag_app.py           # RAG portal

# CLI Tools
python run_mlflow_cli.py              # MLflow server
python setup_aws_credentials_cli.py   # AWS setup wizard
python infrastructure/install_packages_cli.py  # Install packages
python infrastructure/make_scripts_cli.py      # Generate scripts
```

### Important Notes

1. **Always launch from root directory** - The launchers expect to find `infrastructure/`, `domain/`, and other folders at the root level.

2. **Web Portals** - These open in your browser automatically. If not, check the console output for the URL (e.g., http://localhost:8501)

3. **CLI Tools** - These run in the terminal. MLflow starts a server that you can access at http://localhost:5000

4. **Path Management** - All launchers use the PathManager utility for consistent path resolution.

5. **Port Conflicts** - If a port is already in use, you'll get an error. Check if another instance is already running.

## Troubleshooting

- **Import Errors**: Make sure you're launching from the root directory
- **Port Already in Use**: Kill the existing process or use a different port
- **Missing Dependencies**: Install required packages (streamlit, mlflow, etc.)
- **Settings Not Found**: Ensure `infrastructure/settings.yaml` exists