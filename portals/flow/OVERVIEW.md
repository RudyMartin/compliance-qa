# Flow Portal V4 - User Guide & Overview

## 🎯 What is Flow Portal?

Flow Portal is your intelligent workflow assistant that helps you build, manage, and optimize data processing pipelines using a visual card-based interface. Think of it as **LEGO blocks for AI workflows** - each card does one specific task, and you connect them together to create powerful automation.

## 🚀 Getting Started

### Launch the Portal

```bash
# Windows
launch.bat

# Or directly with Streamlit
streamlit run flow_portal_v4.py
```

The portal opens in your browser at `http://localhost:8501`

## 🗺️ Portal Navigation

The portal has **5 main tabs**, each serving a specific purpose:

```
📝 Create → 📚 Manage → ▶️ Run → 📈 Optimize → 🤖 Ask AI
```

### Project Selector (Top of Screen)

Before you start, select your working context:
- **➕ Create new workflow** - Start building a new workflow
- **global** - Shared workflows available to all projects
- **client_demo** - Example workflows to learn from
- **[your_project]** - Your specific project workflows

## 📝 Create Tab - Build Your Workflows

### Understanding Business Cards

Workflows are built from **Business Cards** - each card represents one action in your process. Cards follow the **OODA Loop** methodology:

1. **🔍 OBSERVE** - Gather information
   - Extract Document - Pull text from PDFs, Word docs
   - RAG Search - Search your knowledge base
   - Load Data - Import CSV, JSON, databases

2. **🧠 ORIENT** - Understand and analyze
   - Analyze Content - AI analyzes your data
   - Compare Documents - Find differences/similarities
   - Ask Expert - Get AI expert opinions

3. **✅ DECIDE** - Make decisions
   - Evaluate Options - Compare choices
   - Generate Insights - Create recommendations

4. **⚡ ACT** - Take action
   - Create Report - Generate documents
   - Send Results - Email or export data

### Building a Workflow - Step by Step

#### Method 1: Visual Builder (Recommended for Beginners)

1. **Name Your Workflow**
   ```
   Workflow Name: [Document Analysis Pipeline]
   ```

2. **Add Cards** (Click from library)
   - Click "📄 Extract Document" → Card appears in workflow
   - Click "💡 Analyze Content" → Added as step 2
   - Click "📝 Create Report" → Added as step 3

3. **Configure Each Card**
   - Click the card's expander (▼)
   - Set AI model (GPT-4, Claude, etc.)
   - Adjust parameters (temperature, output format)
   - Add custom prompts if needed

4. **Reorder Cards** (if needed)
   - Use ⬆⬇ arrows to move cards up/down

5. **Save Workflow**
   - Click "💾 Save Workflow"
   - Choose project location
   - Workflow is now reusable!

#### Method 2: Natural Language

1. Type what you want:
   ```
   "I need to extract data from invoices, validate the amounts,
   and create a summary report"
   ```

2. AI generates workflow:
   ```
   Suggested Cards:
   1. Extract Document (Invoice PDF)
   2. Analyze Content (Validate amounts)
   3. Create Report (Summary)
   ```

3. Review and adjust as needed

### Example Workflows

**Document Review Workflow:**
```
1. Extract Document → 2. RAG Search (similar docs) → 3. Compare Documents → 4. Generate Insights
```

**Data Analysis Pipeline:**
```
1. Load Data (CSV) → 2. Analyze Content → 3. Evaluate Options → 4. Create Report
```

## 📚 Manage Tab - Organize Your Workflows

### Workflow Library

Your workflows are organized like a library:

```
┌─────────────────────────────────────┐
│ 📁 client_demo                      │
│   📄 Risk Assessment v2.1           │
│      • 5 cards                      │
│      • Last run: 2 hours ago        │
│      • Success rate: 98%            │
│                                      │
│   📊 Financial Analysis v1.3        │
│      • 8 cards                      │
│      • Last run: Yesterday          │
│      • Success rate: 95%            │
└─────────────────────────────────────┘
```

### Key Features

**Version Control:**
- Every save creates a new version
- Roll back to previous versions
- Compare versions side-by-side

**Operations:**
- 🔄 **Clone** - Duplicate and modify
- 📤 **Export** - Share as JSON file
- 📥 **Import** - Load from JSON
- 🗑️ **Archive** - Hide unused workflows
- 📊 **Metrics** - View performance stats

### Organizing Workflows

**Use Tags:**
```
#finance #daily #critical #test
```

**Categories:**
- By department (Sales, HR, Finance)
- By frequency (Daily, Weekly, Ad-hoc)
- By priority (Critical, Standard, Low)

## ▶️ Run Tab - Execute Your Workflows

### Running a Workflow

1. **Select Workflow**
   ```
   Choose workflow: [Document Analysis v2.1 ▼]
   ```

2. **Provide Inputs**
   - Upload files (drag & drop)
   - Enter text/parameters
   - Connect data sources

3. **Choose Execution Mode**
   - **▶️ Standard** - Run normally
   - **🐛 Debug** - Step by step with inspection
   - **⚡ Batch** - Process multiple inputs
   - **🔄 Schedule** - Set up automation

4. **Monitor Execution**
   ```
   Progress: ████████░░ 80%
   Current Step: Analyzing Content...
   Time Elapsed: 3.2s
   ```

### Execution Controls

- **⏸️ Pause** - Temporarily stop
- **▶️ Resume** - Continue from pause
- **⏭️ Skip** - Skip current step
- **🔴 Stop** - Cancel execution
- **🔄 Retry** - Retry failed step

### Understanding the Output

Each card produces output that feeds into the next:

```
Card 1: Extract Document
└─ Output: 1,500 text chunks extracted ✅

Card 2: Analyze Content
└─ Output: Key insights identified ✅

Card 3: Create Report
└─ Output: report_2024_09_22.pdf ✅
```

## 📈 Optimize Tab - Improve Performance

### Performance Metrics

The system tracks key metrics:

```
Success Rate:  ████████████ 95% ↑2%
Avg Time:      ████████ 3.2s ↓0.5s
RL Score:      █████████ 0.87 ↑0.05
Cost/Run:      ███ $0.12 ↓$0.03
```

### Optimization Options

**Auto-Optimize (Recommended):**
1. Click "🎯 Apply RL Optimization"
2. System automatically tunes parameters
3. Review suggested changes
4. Apply or reject

**Manual Tuning:**
- Adjust AI temperature (creativity vs consistency)
- Change chunk sizes for processing
- Select different AI models
- Modify timeout settings

### A/B Testing

Compare two versions:
1. Create variant workflow
2. Run both versions with same data
3. Compare results
4. Keep the better performer

## 🤖 Ask AI Tab - Your Workflow Assistant

### What Can the AI Help With?

**Workflow Creation:**
```
You: "How do I process customer feedback forms?"
AI: "I'll help you create a workflow. You'll need:
     1. Extract Document card for the forms
     2. Analyze Content for sentiment analysis
     3. Create Report for summary"
     [Generate Workflow]
```

**Debugging:**
```
You: "My RAG search is timing out"
AI: "I see the issue. Your chunk size is too large.
     Try reducing from 2000 to 500 chunks.
     [Apply Fix]"
```

**Optimization:**
```
You: "How can I make this workflow faster?"
AI: "I notice Card 2 takes 80% of execution time.
     Consider using a faster model or caching.
     [Show Details]"
```

### Quick Actions

- **Generate Workflow** - Create from description
- **Debug Current** - Analyze running workflow
- **Suggest Improvements** - Get optimization tips
- **Explain Card** - Understand what a card does

## 💡 Best Practices

### Workflow Design

1. **Start Simple** - Begin with 2-3 cards, add complexity later
2. **Test Often** - Run after each major change
3. **Use Templates** - Start from existing workflows
4. **Name Clearly** - "Invoice_Processing_v2" not "Workflow1"

### Performance Tips

1. **Cache When Possible** - Reuse extracted data
2. **Batch Similar Operations** - Process multiple files together
3. **Choose Right Models** - GPT-3.5 for simple, GPT-4 for complex
4. **Set Timeouts** - Prevent hanging on large files

### Organization

1. **Version Regularly** - Save before major changes
2. **Document Purpose** - Add descriptions to workflows
3. **Use Consistent Naming** - [Department]_[Process]_[Version]
4. **Archive Old Versions** - Keep library clean

## 🎓 Example Use Cases

### Invoice Processing
```
1. Extract Document (PDF invoices)
2. Analyze Content (Extract amounts, dates)
3. Compare Documents (Check against POs)
4. Create Report (Exceptions report)
```

### Customer Feedback Analysis
```
1. Load Data (Survey responses)
2. Analyze Content (Sentiment analysis)
3. Generate Insights (Key themes)
4. Send Results (Email to team)
```

### Document Compliance Check
```
1. Extract Document (Policy document)
2. RAG Search (Compliance rules)
3. Compare Documents (Find gaps)
4. Create Report (Compliance report)
```

## 🆘 Troubleshooting

### Common Issues

**Workflow Won't Save:**
- Check workflow has a name
- Ensure at least one card added
- Verify project permissions

**Execution Fails:**
- Check input data format
- Verify AI API keys configured
- Review error message in output

**Slow Performance:**
- Reduce chunk size
- Use faster AI model
- Enable caching
- Check network connection

### Getting Help

1. **Ask AI Tab** - First stop for any questions
2. **Documentation** - Review this guide
3. **Examples** - Check client_demo workflows
4. **Export Logs** - Share with support team

## 🎯 Quick Reference

### Keyboard Shortcuts
- `Ctrl+S` - Save workflow
- `Ctrl+R` - Run workflow
- `Ctrl+Z` - Undo last action
- `Tab` - Navigate between fields

### Card Categories Quick Guide
- **Observe** = Input/Extraction
- **Orient** = Analysis/Understanding
- **Decide** = Evaluation/Decision
- **Act** = Output/Action

### Execution Modes
- **Standard** = Normal run
- **Debug** = Step-by-step
- **Batch** = Multiple inputs
- **Schedule** = Automated

### File Formats Supported
- Documents: PDF, DOCX, TXT, RTF
- Data: CSV, JSON, XML, Excel
- Images: PNG, JPG (with OCR)
- Outputs: PDF, HTML, JSON, CSV

---

**Pro Tip**: Start with the `client_demo` project to explore pre-built workflows and learn by example!

**Remember**: Every expert was once a beginner. Start simple, experiment, and gradually build more complex workflows as you learn.

---

*Version 4.0 | Last Updated: September 2025*