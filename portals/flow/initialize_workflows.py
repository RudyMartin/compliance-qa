"""
Initialize Workflows for Flow Portal V4
========================================
Populate the portal with test workflows from our test suite
"""

import json
import streamlit as st
from pathlib import Path

def get_test_workflows():
    """Get all test workflows including the big document processing ones"""

    workflows = {
        # The big document test workflow (3 workflows)
        "Document Test Suite": {
            "name": "Document Test Suite",
            "version": "2.0",
            "created": "today",
            "cards": [
                # Workflow 1: Basic Document Analysis
                {"id": "extract_doc", "name": "📄 Extract Document", "category": "observe", "ai_level": "None"},
                {"id": "extract_metadata", "name": "📊 Extract Metadata", "category": "observe", "ai_level": "None"},
                {"id": "analyze_content", "name": "💡 Analyze Content", "category": "orient", "ai_level": "Assist"},
                {"id": "extract_entities", "name": "🔍 Extract Entities", "category": "orient", "ai_level": "Assist"},
                {"id": "analyze_sentiment", "name": "😊 Analyze Sentiment", "category": "orient", "ai_level": "Auto"},
                {"id": "generate_insights", "name": "🎯 Generate Insights", "category": "decide", "ai_level": "Auto"},
                {"id": "create_report", "name": "📝 Create Report", "category": "act", "ai_level": "Assist"},
            ]
        },

        "Document Comparison": {
            "name": "Document Comparison",
            "version": "1.5",
            "created": "today",
            "cards": [
                {"id": "extract_doc1", "name": "📄 Extract First Doc", "category": "observe", "ai_level": "None"},
                {"id": "extract_doc2", "name": "📄 Extract Second Doc", "category": "observe", "ai_level": "None"},
                {"id": "compare_docs", "name": "🔄 Compare Documents", "category": "orient", "ai_level": "Assist"},
                {"id": "find_similarities", "name": "🔍 Find Similarities", "category": "orient", "ai_level": "Auto"},
                {"id": "generate_recommendations", "name": "💡 Generate Recommendations", "category": "decide", "ai_level": "Auto"},
                {"id": "create_comparison_report", "name": "📊 Create Comparison Report", "category": "act", "ai_level": "Assist"},
            ]
        },

        "RAG Knowledge Base": {
            "name": "RAG Knowledge Base",
            "version": "3.0",
            "created": "today",
            "cards": [
                {"id": "batch_extract", "name": "📚 Batch Extract Documents", "category": "observe", "ai_level": "None"},
                {"id": "create_chunks", "name": "✂️ Create Text Chunks", "category": "observe", "ai_level": "None"},
                {"id": "generate_embeddings", "name": "🧬 Generate Embeddings", "category": "orient", "ai_level": "None"},
                {"id": "create_vector_index", "name": "🗂️ Create Vector Index", "category": "orient", "ai_level": "None"},
                {"id": "test_rag_query", "name": "🔎 Test RAG Query", "category": "decide", "ai_level": "Assist"},
                {"id": "validate_responses", "name": "✅ Validate Responses", "category": "decide", "ai_level": "Auto"},
                {"id": "deploy_rag", "name": "🚀 Deploy RAG System", "category": "act", "ai_level": "None"},
            ]
        },

        # MVR Analysis Workflow
        "MVR Analysis": {
            "name": "MVR Analysis",
            "version": "4.1",
            "created": "today",
            "cards": [
                {"id": "mvr_extract", "name": "📄 Extract MVR Document", "category": "observe", "ai_level": "None"},
                {"id": "mvr_tag", "name": "🏷️ MVR Tagging", "category": "observe", "ai_level": "Assist"},
                {"id": "mvr_qa", "name": "❓ MVR QA Analysis", "category": "orient", "ai_level": "Auto"},
                {"id": "mvr_peer", "name": "👥 MVR Peer Review", "category": "decide", "ai_level": "Auto"},
                {"id": "mvr_report", "name": "📊 MVR Report Generation", "category": "act", "ai_level": "Assist"},
            ]
        },

        # Code Review Workflow
        "Code Review": {
            "name": "Code Review",
            "version": "2.2",
            "created": "today",
            "cards": [
                {"id": "extract_code", "name": "💻 Extract Code", "category": "observe", "ai_level": "None"},
                {"id": "analyze_complexity", "name": "📊 Analyze Complexity", "category": "orient", "ai_level": "None"},
                {"id": "check_standards", "name": "✅ Check Standards", "category": "orient", "ai_level": "Assist"},
                {"id": "security_scan", "name": "🔒 Security Scan", "category": "orient", "ai_level": "Auto"},
                {"id": "generate_review", "name": "📝 Generate Review", "category": "decide", "ai_level": "Auto"},
                {"id": "create_action_items", "name": "📋 Create Action Items", "category": "act", "ai_level": "Assist"},
            ]
        },

        # Financial Analysis
        "Financial Analysis": {
            "name": "Financial Analysis",
            "version": "1.8",
            "created": "today",
            "cards": [
                {"id": "load_financial_data", "name": "💰 Load Financial Data", "category": "observe", "ai_level": "None"},
                {"id": "extract_metrics", "name": "📈 Extract Metrics", "category": "observe", "ai_level": "None"},
                {"id": "analyze_trends", "name": "📊 Analyze Trends", "category": "orient", "ai_level": "Assist"},
                {"id": "risk_assessment", "name": "⚠️ Risk Assessment", "category": "decide", "ai_level": "Auto"},
                {"id": "generate_forecast", "name": "🔮 Generate Forecast", "category": "decide", "ai_level": "Auto"},
                {"id": "create_financial_report", "name": "📑 Create Financial Report", "category": "act", "ai_level": "Assist"},
            ]
        },

        # Compliance Check
        "Compliance Check": {
            "name": "Compliance Check",
            "version": "3.5",
            "created": "today",
            "cards": [
                {"id": "load_regulations", "name": "📜 Load Regulations", "category": "observe", "ai_level": "None"},
                {"id": "extract_requirements", "name": "📋 Extract Requirements", "category": "observe", "ai_level": "Assist"},
                {"id": "scan_documents", "name": "🔍 Scan Documents", "category": "orient", "ai_level": "None"},
                {"id": "check_compliance", "name": "✅ Check Compliance", "category": "decide", "ai_level": "Auto"},
                {"id": "identify_gaps", "name": "⚠️ Identify Gaps", "category": "decide", "ai_level": "Auto"},
                {"id": "generate_audit_report", "name": "📊 Generate Audit Report", "category": "act", "ai_level": "Assist"},
            ]
        },

        # Simple Test Workflows
        "Quick Document Test": {
            "name": "Quick Document Test",
            "version": "1.0",
            "created": "today",
            "cards": [
                {"id": "extract", "name": "📄 Extract Document", "category": "observe", "ai_level": "None"},
                {"id": "analyze", "name": "💡 Analyze Content", "category": "orient", "ai_level": "Assist"},
                {"id": "report", "name": "📝 Create Report", "category": "act", "ai_level": "Assist"},
            ]
        },

        "RAG Q&A Pipeline": {
            "name": "RAG Q&A Pipeline",
            "version": "1.2",
            "created": "today",
            "cards": [
                {"id": "load_knowledge", "name": "📚 Load Knowledge Base", "category": "observe", "ai_level": "None"},
                {"id": "rag_search", "name": "🔎 RAG Search", "category": "observe", "ai_level": "None"},
                {"id": "ask_expert", "name": "🤔 Ask Expert", "category": "orient", "ai_level": "Auto"},
                {"id": "format_answer", "name": "📝 Format Answer", "category": "act", "ai_level": "Assist"},
            ]
        },
    }

    return workflows


def save_workflows_to_session():
    """Save workflows to Streamlit session state file"""

    workflows = get_test_workflows()

    # Create session file that portal can load
    session_file = Path("portals/flow/.streamlit/session_workflows.json")
    session_file.parent.mkdir(parents=True, exist_ok=True)

    with open(session_file, 'w') as f:
        json.dump(workflows, f, indent=2)

    print(f"[OK] Saved {len(workflows)} workflows to {session_file}")
    return workflows


if __name__ == "__main__":
    print("=" * 60)
    print("INITIALIZING WORKFLOWS FOR FLOW PORTAL V4")
    print("=" * 60)

    workflows = save_workflows_to_session()

    print("\nWorkflows available:")
    for name, workflow in workflows.items():
        card_count = len(workflow.get('cards', []))
        print(f"  • {name}: {card_count} cards")

    print("\n" + "=" * 60)
    print("[SUCCESS] Workflows initialized successfully!")
    print("[INFO] Refresh the Flow Portal page to load these workflows")
    print("=" * 60)