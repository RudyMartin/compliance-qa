#!/usr/bin/env python3
"""
Lean QA Portal
==============
Thin Streamlit interface for QA workflows.
All processing logic is in QAWorkflowService.
"""

import streamlit as st
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent to path
qa_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(qa_root))

from domain.services.qa_workflow_service import QAWorkflowService

# Initialize service
qa_service = QAWorkflowService()

def set_page_config():
    """Configure Streamlit page."""
    st.set_page_config(
        page_title="QA Portal - Compliance QA",
        page_icon="✅",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def render_header():
    """Render portal header."""
    st.title("✅ QA Workflow Portal")
    st.markdown("**Compliance Checking & Workflow Management**")
    st.markdown("---")

def render_workflow_overview():
    """Render workflow overview using service."""
    st.subheader("📋 Available Workflows")

    workflows = qa_service.get_available_workflows()

    col1, col2 = st.columns(2)

    for idx, workflow in enumerate(workflows):
        with col1 if idx % 2 == 0 else col2:
            with st.expander(f"**{workflow['name']}**", expanded=False):
                st.write(f"**Description:** {workflow['description']}")
                st.write(f"**Steps:** {workflow['steps']}")
                if workflow.get('standards'):
                    st.write(f"**Standards:** {', '.join(workflow['standards'])}")

                if st.button(f"Run {workflow['name']}", key=f"run_{workflow['id']}"):
                    st.session_state[f'run_{workflow["id"]}'] = True
                    st.rerun()

def render_mvr_processing():
    """Render MVR processing interface."""
    st.subheader("📄 MVR Document Processing")

    col1, col2 = st.columns([2, 1])

    with col1:
        document_id = st.text_input("Document ID", value="MVR_2025_001")
        document_path = st.text_input("Document Path", value="sample_mvr.pdf")

    with col2:
        st.write("**Standards to Check:**")
        standards = st.multiselect(
            "Select Standards",
            options=qa_service.get_compliance_standards(),
            default=['MVS', 'VST']
        )

    if st.button("🚀 Process MVR", type="primary"):
        with st.spinner("Processing MVR document..."):
            result = qa_service.process_mvr(
                document_path,
                context={'document_id': document_id}
            )
            st.session_state['mvr_result'] = result

    # Display results
    if 'mvr_result' in st.session_state:
        result = st.session_state['mvr_result']
        render_mvr_results(result)

def render_mvr_results(result: Dict[str, Any]):
    """Render MVR processing results."""
    st.success(f"✅ Processing Complete - {result['status']}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Processing Time", f"{result['processing_time_ms']} ms")
    with col2:
        st.metric("Findings", len(result.get('findings', [])))
    with col3:
        st.metric("Audit Trail", result['audit_trail_id'])

    # Compliance checks
    st.write("**Compliance Results:**")
    for standard, status in result.get('compliance_checks', {}).items():
        icon = "✅" if status == 'COMPLIANT' else "⚠️"
        st.write(f"{icon} {standard}: {status}")

    # Findings
    if result.get('findings'):
        st.write("**Findings:**")
        for finding in result['findings']:
            severity_color = {
                'critical': 'red',
                'high': 'orange',
                'medium': 'yellow',
                'low': 'blue'
            }.get(finding['severity'], 'gray')

            st.markdown(f"**[{finding['severity'].upper()}]** {finding['description']}")
            st.write(f"   Requirement: {finding['requirement']}")
            st.write(f"   Recommendation: {finding['recommendation']}")

def render_compliance_checking():
    """Render compliance checking interface."""
    st.subheader("🔍 Compliance Checking")

    document = st.text_area("Document Content", height=100, placeholder="Paste document content or path...")

    standards = st.multiselect(
        "Standards to Check",
        options=['MVS_5.4.3', 'MVS_5.4.3.1', 'MVS_5.4.3.2', 'MVS_5.4.3.3',
                'VST_Section_3', 'VST_Section_4', 'VST_Section_5'],
        default=['MVS_5.4.3', 'VST_Section_3']
    )

    if st.button("🔍 Check Compliance"):
        with st.spinner("Checking compliance..."):
            result = qa_service.check_compliance(document, standards)
            st.session_state['compliance_result'] = result

    # Display results
    if 'compliance_result' in st.session_state:
        result = st.session_state['compliance_result']
        render_compliance_results(result)

def render_compliance_results(result: Dict[str, Any]):
    """Render compliance checking results."""
    status = result['overall_status']
    if status == 'COMPLIANT':
        st.success(f"✅ Overall Status: {status}")
    else:
        st.warning(f"⚠️ Overall Status: {status}")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Requirements Checked", result['requirements_checked'])
    with col2:
        st.metric("Compliant", f"{result['compliant_count']}/{result['requirements_checked']}")

    # Detailed results
    st.write("**Detailed Results:**")
    for standard, details in result.get('details', {}).items():
        icon = "✅" if details['status'] == 'COMPLIANT' else "⚠️"
        st.write(f"{icon} **{standard}**: {details['status']} (Confidence: {details['confidence']:.0%})")
        if details.get('issues'):
            for issue in details['issues']:
                st.write(f"   - {issue}")

def render_finding_classification():
    """Render finding classification interface."""
    st.subheader("🏷️ Finding Classification")

    # Sample findings for demo
    sample_findings = [
        {'id': 'F001', 'severity': 'high', 'description': 'Missing documentation'},
        {'id': 'F002', 'severity': 'medium', 'description': 'Process improvement needed'},
        {'id': 'F003', 'severity': 'low', 'description': 'Minor formatting issue'}
    ]

    st.write("**Sample Findings:**")
    for finding in sample_findings:
        st.write(f"- [{finding['severity']}] {finding['description']}")

    if st.button("🏷️ Classify Findings"):
        with st.spinner("Classifying findings..."):
            result = qa_service.classify_findings(sample_findings)
            st.session_state['classification_result'] = result

    # Display results
    if 'classification_result' in st.session_state:
        result = st.session_state['classification_result']
        render_classification_results(result)

def render_classification_results(result: Dict[str, Any]):
    """Render finding classification results."""
    st.write("**Classification Results:**")

    col1, col2, col3, col4 = st.columns(4)

    classification = result['classification']
    with col1:
        st.metric("Critical", classification['critical'])
    with col2:
        st.metric("High", classification['high'])
    with col3:
        st.metric("Medium", classification['medium'])
    with col4:
        st.metric("Low", classification['low'])

    if result.get('auto_escalated'):
        st.warning(f"⚠️ Auto-escalated: {', '.join(result['auto_escalated'])}")

    # Regulatory impact
    st.write("**Regulatory Impact:**")
    for reg, impact in result.get('regulatory_impact', {}).items():
        color = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(impact, '⚪')
        st.write(f"{color} {reg}: {impact}")

def render_qa_checklist():
    """Render QA checklist interface."""
    st.subheader("📋 QA Checklist")

    document = st.text_input("Document to Check", value="sample_document.pdf")
    version = st.selectbox("Checklist Version", ["v2024.3", "v2024.2", "v2024.1"])

    if st.button("📋 Run Checklist"):
        with st.spinner("Running QA checklist..."):
            result = qa_service.run_qa_checklist(document, version)
            st.session_state['checklist_result'] = result

    # Display results
    if 'checklist_result' in st.session_state:
        result = st.session_state['checklist_result']
        render_checklist_results(result)

def render_checklist_results(result: Dict[str, Any]):
    """Render QA checklist results."""
    status = result['overall_status']
    if status == 'PASS':
        st.success(f"✅ Overall Status: {status}")
    elif status == 'CONDITIONAL_PASS':
        st.warning(f"⚠️ Overall Status: {status}")
    else:
        st.error(f"❌ Overall Status: {status}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Items", result['total_items'])
    with col2:
        st.metric("Passed", result['passed'])
    with col3:
        st.metric("Failed", result['failed'])
    with col4:
        st.metric("Completion", f"{result['completion_percentage']}%")

    st.info(f"💡 Next Action: {result['next_action']}")

def render_audit_report():
    """Render audit report generation."""
    st.subheader("📊 Audit Report")

    if st.button("📊 Generate Audit Report"):
        # Collect all workflow results from session
        workflow_results = []

        if 'mvr_result' in st.session_state:
            workflow_results.append(st.session_state['mvr_result'])
        if 'classification_result' in st.session_state:
            workflow_results.append(st.session_state['classification_result'])

        if workflow_results:
            report = qa_service.generate_audit_report(workflow_results)
            st.session_state['audit_report'] = report
        else:
            st.warning("No workflow results available. Run some workflows first.")

    # Display report
    if 'audit_report' in st.session_state:
        report = st.session_state['audit_report']

        st.success(f"✅ Report Generated: {report['report_id']}")

        st.write("**Executive Summary:**")
        st.info(report['executive_summary'])

        st.write("**Severity Summary:**")
        col1, col2, col3, col4 = st.columns(4)

        severity = report['severity_summary']
        with col1:
            st.metric("Critical", severity['critical'])
        with col2:
            st.metric("High", severity['high'])
        with col3:
            st.metric("Medium", severity['medium'])
        with col4:
            st.metric("Low", severity['low'])

        st.write("**Recommendations:**")
        for rec in report['recommendations']:
            st.write(f"• {rec}")

def main():
    """Main application."""
    set_page_config()
    render_header()

    # Sidebar navigation
    with st.sidebar:
        st.title("✅ QA Menu")

        page = st.selectbox(
            "Select Function:",
            ["Overview", "MVR Processing", "Compliance Check", "Finding Classification", "QA Checklist", "Audit Report"]
        )

        st.markdown("---")

        if st.button("🔄 Refresh"):
            st.rerun()

        st.markdown("---")
        st.write("**Service Info:**")
        st.write("Standards:", ', '.join(qa_service.get_compliance_standards()[:3]))
        st.write("Severity Levels:", ', '.join(qa_service.get_severity_levels()))

    # Render selected page
    if page == "Overview":
        render_workflow_overview()
    elif page == "MVR Processing":
        render_mvr_processing()
    elif page == "Compliance Check":
        render_compliance_checking()
    elif page == "Finding Classification":
        render_finding_classification()
    elif page == "QA Checklist":
        render_qa_checklist()
    elif page == "Audit Report":
        render_audit_report()

    # Handle workflow runs from overview
    for workflow in qa_service.get_available_workflows():
        if st.session_state.get(f'run_{workflow["id"]}'):
            st.session_state[f'run_{workflow["id"]}'] = False
            if workflow['id'] == 'mvr_processing':
                render_mvr_processing()
            elif workflow['id'] == 'compliance_checking':
                render_compliance_checking()
            elif workflow['id'] == 'finding_classification':
                render_finding_classification()
            elif workflow['id'] == 'qa_checklist':
                render_qa_checklist()

if __name__ == "__main__":
    main()