#!/usr/bin/env python3
"""
Setup Portal - Special Edition
==============================
Complete setup portal designed for 12th graders with clear step-by-step guidance.
All 6 basic setup functions integrated with obvious next steps.
Special Edition for student-friendly installation.
"""

import streamlit as st
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
        page_title="Setup Portal - Special Edition",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def render_header():
    """Render the portal header."""
    st.title("🚀 Setup Portal - Special Edition")
    st.markdown("**Welcome! Let's set up your AI system step by step.**")

    # Quick status overview
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        wizard_result = setup_service.installation_wizard()
        if wizard_result['overall_status'] == 'ready':
            st.success("✅ System Ready")
        else:
            st.error("❌ Needs Setup")

    with col2:
        dep_result = setup_service.dependency_check()
        if dep_result['overall_status'] == 'ready':
            st.success("✅ Software OK")
        else:
            st.warning("⚠️ Missing Software")

    with col3:
        chat_result = setup_service.tidyllm_basic_setup()
        model_count = chat_result.get('model_count', 0)
        if model_count > 0:
            st.success(f"✅ {model_count} AI Models")
        else:
            st.error("❌ No AI Models")

    with col4:
        health_result = setup_service.health_check()
        if health_result['overall_status'] == 'healthy':
            st.success("✅ All Systems GO")
        else:
            st.warning("⚠️ System Issues")

    st.markdown("---")

def render_step_1_system_check():
    """Step 1: Check if everything is ready."""
    st.header("Step 1️⃣: Check Your System")
    st.markdown("**First, let's see if your computer is ready for AI!**")

    if st.button("🔍 CHECK MY SYSTEM NOW", type="primary", use_container_width=True):
        with st.spinner("Checking your system... This will take a few seconds..."):
            wizard_results = setup_service.installation_wizard()
            # Store results in session state so they persist
            st.session_state['step1_results'] = wizard_results

    # Display results if they exist in session state
    if 'step1_results' in st.session_state:
        wizard_results = st.session_state['step1_results']
        results = wizard_results['results']
        status = wizard_results['overall_status']

        st.markdown("### 📊 System Check Results:")

        if status == 'ready':
            st.success("🎉 **GREAT NEWS!** Your system is ready to go!")
        else:
            st.warning("⚠️ **Your system needs some setup.** Don't worry - we'll help you fix it!")

        # Show detailed results
        for check, passed in results.items():
            if isinstance(passed, bool):
                check_name = check.replace('_', ' ').title()
                if passed:
                    st.success(f"✅ **{check_name}**: Ready to go!")
                else:
                    st.error(f"❌ **{check_name}**: Needs your attention")

                    # Provide specific help for each issue
                    if check == 'python_version':
                        st.info("💡 **Fix:** You need Python 3.8 or newer. Ask your teacher for help installing Python.")
                    elif check == 'required_directories':
                        st.info("💡 **Fix:** Some folders are missing. Make sure you downloaded the complete project.")
                    elif check == 'settings_yaml_exists':
                        st.info("💡 **Fix:** The settings.yaml file is missing. Ask your teacher for the configuration file.")
                    elif check == 'database_connection':
                        st.info("💡 **Fix:** Can't connect to the database. Check your internet connection.")
                    elif check == 'aws_credentials':
                        st.info("💡 **Fix:** AWS credentials are missing. Ask your teacher for the access keys.")

        st.info(f"📋 **Summary:** {wizard_results['summary']}")

        # Next step guidance
        if status == 'ready':
            st.success("🎯 **NEXT STEP:** Go to Step 2 to check your software!")
        else:
            st.warning("🎯 **NEXT STEP:** Fix the red ❌ items above, then try again.")

        # Add a button to re-check
        if st.button("🔄 Check Again", use_container_width=True):
            del st.session_state['step1_results']
            st.rerun()

def render_step_2_software_check():
    """Step 2: Check required software."""
    st.header("Step 2️⃣: Check Required Software")
    st.markdown("**Let's make sure you have all the programs you need!**")

    if st.button("🔧 CHECK SOFTWARE NOW", type="primary", use_container_width=True):
        with st.spinner("Checking required software..."):
            dep_results = setup_service.dependency_check()
            # Store results in session state so they persist
            st.session_state['step2_results'] = dep_results

    # Display results if they exist in session state
    if 'step2_results' in st.session_state:
        dep_results = st.session_state['step2_results']
        results = dep_results['results']
        status = dep_results['overall_status']

        st.markdown("### 💻 Software & Configuration Check Results:")

        if status == 'ready':
            st.success("🎉 **PERFECT!** All required software is installed and configured!")
        else:
            st.warning("⚠️ **Some software or configuration is missing.** We'll help you fix it!")

        # Show detailed results
        for check, passed in results.items():
            if isinstance(passed, bool):
                check_name = check.replace('_', ' ').title()
                if passed:
                    if check == 'aws_credentials_configured':
                        st.success(f"✅ **{check_name}**: Configured and ready!")
                    else:
                        st.success(f"✅ **{check_name}**: Installed and ready!")
                else:
                    if check == 'aws_credentials_configured':
                        st.error(f"❌ **{check_name}**: Not configured")
                    elif check == 'file_permissions':
                        st.error(f"❌ **{check_name}**: Insufficient permissions")
                    else:
                        st.error(f"❌ **{check_name}**: Not installed")

                    # Provide specific installation help
                    if check == 'postgresql_available':
                        st.info("💡 **Fix:** PostgreSQL database is missing. Ask your teacher to help install it.")
                    elif check == 'aws_credentials_configured':
                        st.info("💡 **Fix:** AWS credentials are missing. Check settings.yaml or ask your teacher for AWS access keys.")
                    elif check == 'python_packages_installed':
                        st.info("💡 **Fix:** Some Python packages are missing. Try running: pip install -r requirements.txt")
                    elif check == 'file_permissions':
                        st.info("💡 **Fix:** File permissions issue. Ask your teacher to check folder permissions.")

        st.info(f"📋 **Summary:** {dep_results['summary']}")

        # Next step guidance
        if status == 'ready':
            st.success("🎯 **NEXT STEP:** Go to Step 3 to set up AI chat!")
        else:
            st.warning("🎯 **NEXT STEP:** Install the missing software above, then try again.")

        # Add a button to re-check
        if st.button("🔄 Check Again", use_container_width=True, key="step2_check_again"):
            del st.session_state['step2_results']
            st.rerun()

def render_step_3_chat_setup():
    """Step 3: Set up chat features."""
    st.header("Step 3️⃣: Set Up AI Chat")
    st.markdown("**Time to set up your AI chat with multiple models!**")

    if st.button("🤖 CHECK AI CHAT SETUP", type="primary", use_container_width=True):
        with st.spinner("Checking AI chat setup..."):
            chat_results = setup_service.tidyllm_basic_setup()
            # Store results in session state so they persist
            st.session_state['step3_results'] = chat_results

    # Display results if they exist in session state
    if 'step3_results' in st.session_state:
        chat_results = st.session_state['step3_results']
        results = chat_results['results']
        model_count = chat_results.get('model_count', 0)
        status = chat_results['overall_status']

        st.markdown("### 🤖 AI Chat Setup Results:")

        if status == 'configured':
            st.success(f"🎉 **AMAZING!** Your AI chat is ready with {model_count} different models!")
        else:
            st.warning("⚠️ **AI chat needs configuration.** Let's fix this!")

        # Show AI models available
        if model_count > 0:
            st.info(f"🤖 **You have {model_count} AI models available:**")
            st.markdown("""
            - **Claude-3-Haiku**: Fastest model, great for quick questions
            - **Claude-3-Sonnet**: Balanced model, good for most tasks
            - **Claude-3.5-Sonnet**: Latest model, enhanced capabilities
            - **Claude-3-Opus**: Most powerful model, best for complex tasks
            """)

        # Show detailed results
        for check, passed in results.items():
            if isinstance(passed, bool):
                check_name = check.replace('_', ' ').title()
                if passed:
                    st.success(f"✅ **{check_name}**: Configured perfectly!")
                else:
                    st.error(f"❌ **{check_name}**: Not configured")

                    # Provide specific help
                    if check == 'bedrock_models_configured':
                        st.info("💡 **Fix:** AI models are not set up. Ask your teacher to configure AWS Bedrock.")
                    elif check == 'basic_chat_settings':
                        st.info("💡 **Fix:** Chat settings are missing. Check the settings.yaml file.")
                    elif check == 'default_timeouts_set':
                        st.info("💡 **Fix:** Timeout settings are missing. Ask your teacher to configure timeouts.")
                    elif check == 'basic_mlflow_tracking':
                        st.info("💡 **Fix:** MLflow tracking is not set up. Check MLflow configuration.")

        st.info(f"📋 **Summary:** {chat_results['summary']}")

        # Next step guidance
        if status == 'configured':
            st.success("🎯 **NEXT STEP:** Go to Step 4 for final health check!")
        else:
            st.warning("🎯 **NEXT STEP:** Fix the AI configuration issues above.")

        # Add a button to re-check
        if st.button("🔄 Check Again", use_container_width=True, key="step3_check_again"):
            del st.session_state['step3_results']
            st.rerun()

def render_step_4_health_check():
    """Step 4: Final health check."""
    st.header("Step 4️⃣: Final Health Check")
    st.markdown("**Let's make sure everything is working perfectly!**")

    if st.button("💚 TEST EVERYTHING NOW", type="primary", use_container_width=True):
        with st.spinner("Testing all systems... This might take a minute..."):
            health_results = setup_service.health_check()
            # Store results in session state so they persist
            st.session_state['step4_results'] = health_results

    # Display results if they exist in session state
    if 'step4_results' in st.session_state:
        health_results = st.session_state['step4_results']
        results = health_results['results']
        status = health_results['overall_status']

        st.markdown("### 💚 System Health Results:")

        if status == 'healthy':
            st.success("🎉 **PERFECT!** Everything is working beautifully!")
        else:
            st.warning("⚠️ **Some systems aren't working properly.** Let's see what needs fixing...")

        # Show detailed results
        for check, passed in results.items():
            if isinstance(passed, bool):
                check_name = check.replace('_', ' ').title()
                if passed:
                    st.success(f"✅ **{check_name}**: Working perfectly!")
                else:
                    st.error(f"❌ **{check_name}**: Having problems")

                    # Provide specific help
                    if check == 'database_connection_status':
                        st.info("💡 **Fix:** Database connection failed. Check your internet or ask your teacher.")
                    elif check == 'aws_service_connectivity':
                        st.info("💡 **Fix:** AWS connection failed. Check AWS credentials with your teacher.")
                    elif check == 'mlflow_tracking_status':
                        st.info("💡 **Fix:** MLflow is not working. Ask your teacher to check MLflow setup.")
                    elif check == 'bedrock_model_accessibility':
                        st.info("💡 **Fix:** AI models are not accessible. Check AWS Bedrock configuration.")
                    elif check == 'basic_chat_functionality':
                        st.info("💡 **Fix:** Chat is not working. Fix AWS and Bedrock issues first.")

        st.info(f"📋 **Summary:** {health_results['summary']}")

        # Next step guidance
        if status == 'healthy':
            st.success("🎯 **NEXT STEP:** You're ready! Check out the available portals below!")
        else:
            st.warning("🎯 **NEXT STEP:** Fix the issues above, then test again.")

        # Add a button to re-check
        if st.button("🔄 Check Again", use_container_width=True, key="step4_check_again"):
            del st.session_state['step4_results']
            st.rerun()

def render_step_5_portal_guide():
    """Step 5: Portal guide."""
    st.header("Step 5️⃣: Explore Available Portals")
    st.markdown("**Great! Now you can explore all the different AI tools available!**")

    portal_data = setup_service.portal_guide()

    if portal_data['overall_status'] == 'available':
        portals = portal_data['portals']
        descriptions = portal_data['portal_descriptions']

        st.success(f"🚪 **{portal_data['active_portals']} out of {portal_data['total_portals']} portals are currently running!**")

        # Organize portals by category
        categories = portal_data['categories']

        for category, category_portals in categories.items():
            st.subheader(f"📁 {category} Tools")

            for portal in category_portals:
                name = portal['name']
                port = portal['port']
                active = portal.get('active', False)
                description = descriptions.get(name, 'Portal functionality')

                col1, col2, col3 = st.columns([2, 4, 1])

                with col1:
                    if active:
                        st.success(f"🟢 **{name}**")
                    else:
                        st.error(f"🔴 **{name}**")

                with col2:
                    st.write(f"📝 {description}")
                    if not active:
                        st.caption("💡 Ask your teacher to start this portal if you need it")

                with col3:
                    if active:
                        st.link_button("🚀 Open", f"http://localhost:{port}")
                    else:
                        st.write("⏹️ Stopped")

            st.markdown("---")

    # Load example data option
    st.subheader("📚 Load Example Data")
    st.markdown("**Want to try some examples? Load sample data to get started!**")

    if st.button("📚 LOAD EXAMPLES NOW", type="primary", use_container_width=True):
        with st.spinner("Loading example data..."):
            example_results = setup_service.load_examples()

            if example_results['overall_status'] == 'loaded':
                st.success("✅ **Example data loaded successfully!** You can now try the AI tools with sample conversations.")
            else:
                st.error("❌ **Failed to load examples.** Ask your teacher for help.")

            st.info(f"📋 **Summary:** {example_results['summary']}")

def render_quick_actions():
    """Render quick action buttons."""
    st.header("⚡ Quick Actions")
    st.markdown("**Need to do something quickly? Use these buttons!**")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 REFRESH ALL STATUS", use_container_width=True):
            st.rerun()

    with col2:
        if st.button("🆘 GET HELP", use_container_width=True):
            st.info("""
            **Need Help?**
            1. 📧 Ask your teacher
            2. 📖 Check the documentation
            3. 👥 Ask a classmate
            4. 🔄 Try refreshing the page
            """)

    with col3:
        if st.button("📊 SYSTEM STATUS", use_container_width=True):
            env_summary = setup_service.get_environment_summary()
            st.json(env_summary)

def main():
    """Main application."""
    set_page_config()
    render_header()

    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "1️⃣ System Check",
        "2️⃣ Software Check",
        "3️⃣ AI Chat Setup",
        "4️⃣ Health Check",
        "5️⃣ Explore Portals",
        "⚡ Quick Actions"
    ])

    with tab1:
        render_step_1_system_check()

    with tab2:
        render_step_2_software_check()

    with tab3:
        render_step_3_chat_setup()

    with tab4:
        render_step_4_health_check()

    with tab5:
        render_step_5_portal_guide()

    with tab6:
        render_quick_actions()

    # Footer with helpful information
    st.markdown("---")
    st.markdown("""
    ### 📋 What Each Step Does:
    - **Step 1**: Checks if your computer has everything it needs
    - **Step 2**: Makes sure required software is installed
    - **Step 3**: Sets up AI chat with 4 different models
    - **Step 4**: Tests that everything works together
    - **Step 5**: Shows you all the AI tools you can use

    ### 🎯 Remember:
    - **Green ✅** means everything is working
    - **Red ❌** means something needs to be fixed
    - **Yellow ⚠️** means there might be a small issue
    - When you see problems, ask your teacher for help!
    """)

if __name__ == "__main__":
    main()