#!/usr/bin/env python3
"""
Lean Setup Portal
=================
Thin Streamlit interface that uses SetupService for all logic.
All processing is done in the service layer.
"""

import streamlit as st
import asyncio
import sys
from pathlib import Path

# Add parent to path
qa_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(qa_root))

from domain.services.setup_service import SetupService

# Initialize service
setup_service = SetupService(qa_root)

def set_page_config():
    """Configure the Streamlit page."""
    st.set_page_config(
        page_title="Setup Portal - Compliance QA",
        page_icon="⚙️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def render_header():
    """Render the portal header."""
    arch_info = setup_service.get_architecture_info()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("⚙️ Setup Portal")
        st.markdown("**System Configuration & Credential Management**")
        st.markdown(f"*{arch_info['description']}*")
        st.markdown("---")

def render_system_status():
    """Render system status using service."""
    st.subheader("📊 System Status")

    # Get data from service
    env_summary = setup_service.get_environment_summary()
    portal_count = setup_service.discover_active_portals()
    pool_status = setup_service.check_connection_pool_status()
    arch_info = setup_service.get_architecture_info()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🌍 Environment", env_summary.get('environment', 'Unknown'))

    with col2:
        health_ok = all(env_summary.get('validation_results', {}).values())
        st.metric("💚 Health", "OK" if health_ok else "Issues")

    with col3:
        st.metric("🚪 Active Portals", f"{portal_count}/7")

    with col4:
        st.metric("🏗️ Architecture", arch_info['name'])

def render_environment_variables():
    """Render environment variable status using service."""
    st.write("**Environment Variables:**")

    # Get data from service
    env_vars = setup_service.check_environment_variables()

    st.write("**Required Variables:**")
    for var_name, description, is_set in env_vars['required']:
        if is_set:
            st.success(f"✅ {var_name}: Set ({description})")
        else:
            st.error(f"❌ {var_name}: Not set - {description}")

    st.write("**Optional Variables:**")
    for var_name, description, is_set in env_vars['optional']:
        if is_set:
            st.success(f"✅ {var_name}: Set ({description})")
        else:
            st.warning(f"⚠️ {var_name}: Not set - {description}")

def render_validation():
    """Render validation interface using service."""
    st.write("**System Validation:**")

    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("🔬 Run Full Validation", type="primary"):
            with st.spinner("Validating..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    report = loop.run_until_complete(setup_service.validate_all_credentials())
                    st.session_state['validation_report'] = report
                except Exception as e:
                    st.error(f"Validation failed: {e}")

        if st.button("⚡ Quick Health Check"):
            with st.spinner("Checking..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    healthy = loop.run_until_complete(setup_service.quick_health_check())
                    if healthy:
                        st.success("✅ Essential services healthy")
                    else:
                        st.error("❌ Essential services unavailable")
                except Exception as e:
                    st.error(f"Health check failed: {e}")

    with col2:
        if 'validation_report' in st.session_state:
            report = st.session_state['validation_report']
            render_validation_report(report)

def render_validation_report(report):
    """Render validation report."""
    status = report.get('overall_status', 'unknown')
    if status == 'healthy':
        st.success(f"🎉 System Status: {status.upper()}")
    elif status == 'degraded':
        st.warning(f"⚠️ System Status: {status.upper()}")
    else:
        st.error(f"❌ System Status: {status.upper()}")

    # Summary
    summary = report.get('summary', {})
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Checks", summary.get('total_checks', 0))
    with col2:
        st.metric("Successful", summary.get('successful', 0))
    with col3:
        st.metric("Errors", summary.get('errors', 0))

def render_portal_discovery():
    """Render portal discovery using service."""
    st.subheader("🚪 Portal Management")

    portals = setup_service.get_known_portals()

    active_portals = [p for p in portals if p['active']]
    inactive_portals = [p for p in portals if not p['active']]

    col1, col2 = st.columns(2)

    with col1:
        st.write("**🟢 Active Portals:**")
        for portal in active_portals:
            st.write(f"✅ **{portal['name']}** (Port {portal['port']})")
            st.link_button(f"Open {portal['name']}", f"http://localhost:{portal['port']}")

    with col2:
        st.write("**🔴 Inactive Portals:**")
        for portal in inactive_portals:
            st.write(f"❌ **{portal['name']}** (Port {portal['port']})")

def render_quick_setup():
    """Render quick setup actions using service."""
    st.subheader("🚀 Quick Setup")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📦 Install All Packages", use_container_width=True):
            with st.spinner("Installing..."):
                if setup_service.install_all_packages():
                    st.success("✅ All packages installed!")
                    st.balloons()
                else:
                    st.error("❌ Installation failed!")

        if st.button("🌍 Setup Environment", use_container_width=True):
            with st.spinner("Setting up..."):
                if setup_service.perform_environment_setup():
                    st.success("✅ Environment setup completed!")
                else:
                    st.error("❌ Setup failed!")

    with col2:
        if st.button("📜 Generate Scripts", use_container_width=True):
            with st.spinner("Generating..."):
                if setup_service.generate_all_scripts():
                    st.success("✅ Scripts generated!")
                else:
                    st.error("❌ Generation failed!")

        if st.button("🔄 Sync Credentials", use_container_width=True):
            with st.spinner("Syncing..."):
                result = setup_service.sync_credential_state()
                if result.get('success'):
                    st.success("✅ Credentials synced!")
                else:
                    st.error(f"❌ Sync failed: {result.get('error')}")

def render_first_time_setup():
    """Render first-time setup wizard for 12th graders."""
    st.title("🚀 Welcome! Let's Get You Started")
    st.markdown("**This is your FIRST TIME using this system? Follow these simple steps:**")

    # Step 1: Installation Wizard
    st.subheader("Step 1️⃣: Check if Everything is Ready")
    if st.button("🔍 Check My System", type="primary", use_container_width=True):
        with st.spinner("Checking your system..."):
            wizard_results = setup_service.installation_wizard()

            results = wizard_results['results']
            status = wizard_results['overall_status']

            if status == 'ready':
                st.success("🎉 Great! Your system is ready to go!")
            else:
                st.warning("⚠️ Your system needs some setup. Don't worry, we'll help you!")

            st.write("**What we checked:**")
            for check, passed in results.items():
                if isinstance(passed, bool):
                    if passed:
                        st.success(f"✅ {check.replace('_', ' ').title()}: Ready")
                    else:
                        st.error(f"❌ {check.replace('_', ' ').title()}: Needs attention")

            st.info(f"**Summary:** {wizard_results['summary']}")

            if status != 'ready':
                st.warning("👆 See the red ❌ items? Those need to be fixed before you can continue.")

    # Step 2: Dependencies
    st.subheader("Step 2️⃣: Check Required Software")
    if st.button("🔧 Check Dependencies", use_container_width=True):
        with st.spinner("Checking required software..."):
            dep_results = setup_service.dependency_check()

            results = dep_results['results']
            status = dep_results['overall_status']

            if status == 'ready':
                st.success("🎉 All required software is installed!")
            else:
                st.warning("⚠️ Some software is missing. You'll need to install it.")

            st.write("**Required software check:**")
            for check, passed in results.items():
                if isinstance(passed, bool):
                    if passed:
                        st.success(f"✅ {check.replace('_', ' ').title()}: Installed")
                    else:
                        st.error(f"❌ {check.replace('_', ' ').title()}: Missing")

            st.info(f"**Summary:** {dep_results['summary']}")

    # Step 3: Chat Setup
    st.subheader("Step 3️⃣: Set Up Chat Features")
    if st.button("🤖 Check Chat Setup", use_container_width=True):
        with st.spinner("Checking chat features..."):
            chat_results = setup_service.tidyllm_basic_setup()

            results = chat_results['results']
            model_count = chat_results.get('model_count', 0)

            if chat_results['overall_status'] == 'configured':
                st.success(f"🎉 Chat is ready! You have {model_count} AI models available!")
            else:
                st.warning("⚠️ Chat features need configuration.")

            st.write("**Chat features check:**")
            for check, passed in results.items():
                if isinstance(passed, bool):
                    if passed:
                        st.success(f"✅ {check.replace('_', ' ').title()}: Configured")
                    else:
                        st.error(f"❌ {check.replace('_', ' ').title()}: Not configured")

            if model_count > 0:
                st.info(f"🤖 **You have {model_count} AI models available for chat!**")

    # Step 4: Health Check
    st.subheader("Step 4️⃣: Final Health Check")
    if st.button("💚 Check Everything Works", use_container_width=True):
        with st.spinner("Testing all systems..."):
            health_results = setup_service.health_check()

            results = health_results['results']
            status = health_results['overall_status']

            if status == 'healthy':
                st.success("🎉 Everything is working perfectly!")
                st.balloons()
            else:
                st.warning("⚠️ Some systems aren't working properly.")

            st.write("**System health check:**")
            for check, passed in results.items():
                if isinstance(passed, bool):
                    if passed:
                        st.success(f"✅ {check.replace('_', ' ').title()}: Working")
                    else:
                        st.error(f"❌ {check.replace('_', ' ').title()}: Not working")

            st.info(f"**Summary:** {health_results['summary']}")

    # Next Steps
    st.subheader("🎯 What's Next?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚪 See All Portals", use_container_width=True):
            st.session_state['show_portal_guide'] = True

    with col2:
        if st.button("📚 Load Example Data", use_container_width=True):
            with st.spinner("Loading examples..."):
                example_results = setup_service.load_examples()
                if example_results['overall_status'] == 'loaded':
                    st.success("✅ Example data loaded!")
                else:
                    st.error("❌ Failed to load examples")

    # Show portal guide if requested
    if st.session_state.get('show_portal_guide', False):
        render_portal_guide_simple()

def render_portal_guide_simple():
    """Render simple portal guide for students."""
    st.subheader("🚪 Available Portals")

    portal_data = setup_service.portal_guide()

    if portal_data['overall_status'] == 'available':
        portals = portal_data['portals']
        descriptions = portal_data['portal_descriptions']

        st.info(f"**{portal_data['active_portals']}/{portal_data['total_portals']} portals are currently running**")

        # Show each portal with simple description
        for portal in portals:
            name = portal['name']
            port = portal['port']
            active = portal.get('active', False)
            description = descriptions.get(name, 'Portal functionality')

            col1, col2, col3 = st.columns([2, 3, 1])

            with col1:
                if active:
                    st.success(f"🟢 **{name}**")
                else:
                    st.error(f"🔴 **{name}**")

            with col2:
                st.write(description)

            with col3:
                if active:
                    st.link_button("Open", f"http://localhost:{port}")
                else:
                    st.write("Not running")

def render_health_check():
    """Render comprehensive health check using service."""
    st.subheader("🏥 System Health")

    if st.button("🔬 Run Complete Health Check", use_container_width=True):
        with st.spinner("Checking all systems..."):
            results = setup_service.perform_comprehensive_health_check()

            col1, col2 = st.columns(2)

            with col1:
                st.write("**✅ Passing:**")
                for component, status in results.items():
                    if status:
                        st.write(f"✅ {component}")

            with col2:
                st.write("**❌ Failing:**")
                for component, status in results.items():
                    if not status:
                        st.write(f"❌ {component}")

def main():
    """Main application."""
    set_page_config()
    render_header()

    # Sidebar navigation
    with st.sidebar:
        st.title("🔧 Setup Menu")

        page = st.selectbox(
            "Select Section:",
            ["🚀 First-Time Setup", "System Status", "Environment", "Validation", "Portals", "Quick Setup", "Health Check"]
        )

        st.markdown("---")

        if st.button("🔄 Refresh"):
            st.rerun()

        st.markdown("---")
        st.write("**Portal Info:**")
        st.write("Port: 8511")
        st.write("Category: Infrastructure")
        st.write("Architecture: Lean/Service-based")

    # Render selected page
    if page == "🚀 First-Time Setup":
        render_first_time_setup()
    elif page == "System Status":
        render_system_status()
    elif page == "Environment":
        render_environment_variables()
    elif page == "Validation":
        render_validation()
    elif page == "Portals":
        render_portal_discovery()
    elif page == "Quick Setup":
        render_quick_setup()
    elif page == "Health Check":
        render_health_check()

if __name__ == "__main__":
    main()