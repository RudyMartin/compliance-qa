# Flow Portal V4 - Intelligent Workflow Management System

## 🚀 Quick Start

```bash
# Launch the Flow Portal
streamlit run flow_portal_v4.py

# Or use the launcher scripts
./launch.bat          # Windows
./launch_special.bat  # Windows (special setup)
```

## 📋 Overview

Flow Portal V4 is an AI-enhanced workflow management system that enables users to build, manage, run, and optimize intelligent workflows using a card-based visual interface. Built with Streamlit and powered by advanced AI capabilities, it provides an intuitive way to create complex data processing pipelines.

### Key Features

- **🎨 Visual Card Builder**: Drag-and-drop interface for workflow creation
- **🤖 AI-Powered Assistance**: Built-in AI helps generate, debug, and optimize workflows
- **📊 Real-time Monitoring**: Live execution tracking with granular control
- **📈 RL Optimization**: Automatic performance improvement using reinforcement learning
- **🔄 Version Control**: Full workflow versioning and rollback capabilities
- **🏢 Multi-Project Support**: Organize workflows across different projects and domains

## 🏗️ System Architecture

The Flow Portal follows a **modular tabfile architecture** for optimal performance and maintainability:

```
flow_portal_v4.py (Main Entry - 276 lines)
    ├── t_create_flow_v4.py     (Create Tab)
    ├── t_manage_flows_enhanced.py (Manage Tab)
    ├── t_run_flows_v4.py       (Run Tab)
    ├── t_optimize_flows_v4.py  (Optimize Tab)
    └── t_ask_ai_v4.py          (Ask AI Tab)
```

### Core Components

1. **Business Builder Cards**: Reusable workflow components following OODA Loop methodology
   - Observe: Data extraction and ingestion
   - Orient: Analysis and understanding
   - Decide: Decision making and insights
   - Act: Actions and outputs

2. **Unified Managers**: Centralized services for consistency
   - `UnifiedStepsManager`: Card library and execution
   - `UnifiedRAGManager`: RAG system integration
   - `RLFactorOptimizer`: Reinforcement learning optimization

3. **Project Structure**: Organized workflow storage
   ```
   tidyllm/workflows/
   ├── global/               # Shared workflows
   └── projects/            # Project-specific workflows
       ├── client_demo/
       ├── alex_qaqc/
       └── [your_project]/
   ```

## 🎯 Main Features by Tab

### 📝 Create Tab
Build workflows using three modes:
- **Visual Builder**: Drag-and-drop cards with live validation
- **Template Mode**: Pre-built industry-specific workflows
- **Natural Language**: Describe workflow → AI generates structure

### 📚 Manage Tab
Comprehensive workflow library management:
- Version control with diff viewing
- Performance metrics and analytics
- Import/export capabilities
- A/B testing framework
- Workflow templates and sharing

### ▶️ Run Tab
Execute workflows with full control:
- Real-time execution monitoring
- Step-by-step debugging mode
- Batch processing support
- Scheduled automation
- Human-in-the-loop decisions

### 📈 Optimize Tab
Performance enhancement through:
- RL-based parameter tuning
- Model performance comparison
- Bottleneck analysis
- Cost optimization
- Statistical A/B testing

### 🤖 Ask AI Tab
Intelligent assistant providing:
- Natural language workflow generation
- Error diagnosis and fixes
- Performance recommendations
- Context-aware suggestions
- Documentation assistance

## 💻 Technical Stack

- **Frontend**: Streamlit (wide layout, responsive design)
- **AI Integration**:
  - GPT-4 / Claude-3 / Local LLMs
  - DSPy for reasoning chains
  - 6 RAG systems (postgres, ai_powered, llama_index, etc.)
- **Data Processing**: TidyLLM framework
- **Storage**: JSON-based workflow persistence
- **Optimization**: RL factors with automatic tuning

## 🔧 Configuration

### Project Selection
The portal supports multiple projects with isolated workflows:

```python
# Projects are automatically discovered from:
tidyllm/workflows/projects/[project_name]/

# Special projects:
- global: Shared workflows available to all
- client_demo: Example workflows for demonstration
```

### Workflow Storage Format
Workflows are stored as JSON with full metadata:

```json
{
  "name": "Document Analysis",
  "version": "1.0",
  "cards": [
    {
      "id": "extract_document",
      "type": "observe",
      "ai_config": {...},
      "parameters": {...}
    }
  ],
  "metrics": {
    "success_rate": 0.95,
    "avg_execution_time": 3.2,
    "rl_score": 0.87
  }
}
```

## 🚦 Current Status

### Git Status Summary
- **Branch**: master
- **Modified**: TidyLLM package integration
- **New Files**:
  - HTML documentation (FLOW_PORTAL_V4_DESIGN.html, README.html, etc.)
  - Core portal files (flow_portal_v4.py and tab files)
- **Deleted**: Legacy v3 files and test outputs

### Recent Updates
- Enhanced modular architecture with tabfile system
- Added project selector with "Create new workflow" option
- Improved AI integration across all tabs
- Performance optimizations for large workflows
- Better error handling and user feedback

## 🎨 UI/UX Design Principles

1. **Progressive Disclosure**: Simple interface with advanced options available when needed
2. **Visual Feedback**: Real-time status updates and progress indicators
3. **Consistent Navigation**: 5-tab structure maintained across all operations
4. **Responsive Layout**: Wide layout optimized for workflow visualization
5. **Contextual Help**: Inline documentation and AI assistance

## 🔒 Security & Best Practices

- No hardcoded credentials
- Isolated project environments
- Audit logging for all operations
- Safe AI model interactions
- Input validation and sanitization

## 📈 Performance Metrics

- **Load Time**: <1 second (modular architecture)
- **Memory Usage**: ~50MB base, scales with workflow complexity
- **Execution**: Parallel card processing where possible
- **Optimization**: RL improvements typically 15-30% performance gain

## 🛠️ Development

### Adding New Cards
Cards are defined in the unified manager and follow a standard interface:

```python
class BusinessCard:
    def __init__(self, card_id, category, name):
        self.id = card_id
        self.category = category  # observe/orient/decide/act
        self.name = name
        self.ai_enabled = True
        self.parameters = {}
```

### Extending Functionality
New features should follow the modular pattern:
1. Create new tab file (t_feature_name.py)
2. Add render function
3. Import in main portal
4. Add to navigation

## 📚 Documentation

- **Architecture Details**: See ARCHITECTURE.md
- **User Guide**: See OVERVIEW.md
- **Design Specification**: FLOW_PORTAL_V4_DESIGN.md
- **Migration Guide**: MODULAR_VS_MONOLITHIC.md

## 🤝 Support

For issues or questions about the Flow Portal:
1. Check the Ask AI tab for immediate assistance
2. Review existing workflows in the Manage tab
3. Consult the documentation files
4. Create detailed error reports with workflow exports

## 📊 Roadmap

### Near Term
- [ ] Cloud workflow sharing
- [ ] Advanced scheduling with cron expressions
- [ ] Webhook triggers for workflows
- [ ] Mobile-responsive design

### Long Term
- [ ] Distributed execution across multiple nodes
- [ ] Visual workflow designer with flowchart view
- [ ] Plugin system for custom cards
- [ ] Enterprise SSO integration

---

**Version**: 4.0
**Last Updated**: September 2025
**License**: Proprietary
**Status**: Production Ready