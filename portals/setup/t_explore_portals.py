"""
Tab 6: Explore Portals - Discover available AI tools
"""
import streamlit as st
import subprocess
import os


def render(setup_service):
    """Step 6: Portal guide."""
    st.header("Step 6️⃣: Explore Your Portals")
    st.markdown("**Great! Now you can explore all the different AI tools available!**")

    portal_info = setup_service.portal_guide()

    if portal_info and 'portals' in portal_info:
        portal_data = portal_info['portals']
        st.success(f"🎉 **Found {len(portal_data)} AI Portals Ready to Use!**")

        # Use categories from portal_info if available, otherwise group by active status
        if 'categories' in portal_info:
            categories = portal_info['categories']
        else:
            # Group portals by active status as fallback
            categories = {
                'Active Portals': [p for p in portal_data if p.get('active', False)],
                'Inactive Portals': [p for p in portal_data if not p.get('active', False)]
            }

        # Display portals by category
        for category, portals in categories.items():
            if portals:  # Only show categories with portals
                st.markdown(f"### {category}")

                # Create columns for portal cards (3 per row)
                for i in range(0, len(portals), 3):
                    cols = st.columns(3)
                    for j, col in enumerate(cols):
                        if i + j < len(portals):
                            portal = portals[i + j]
                            with col:
                                render_portal_card(portal)

    else:
        st.warning("⚠️ No portals found. Make sure you're in the right directory!")

    # Quick launch section
    st.markdown("---")
    st.markdown("### 🚀 Quick Launch")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💬 Launch Chat Portal", type="primary", use_container_width=True):
            launch_portal("run_chat_app.py")

    with col2:
        if st.button("🔄 Launch Flow Portal", type="secondary", use_container_width=True):
            launch_portal("run_flow_app.py")

    with col3:
        if st.button("🤖 Launch RAG Portal", type="secondary", use_container_width=True):
            launch_portal("run_rag_app.py")

    # Portal descriptions
    st.markdown("---")
    st.markdown("### 📚 Portal Descriptions")

    with st.expander("💬 **Chat Portal** - Interactive AI Chat"):
        st.markdown("""
        The Chat Portal provides:
        - Real-time AI conversations
        - Multiple model support (Claude, GPT, etc.)
        - Context management
        - Conversation history
        - Export capabilities

        **Best for:** General AI assistance, Q&A, brainstorming
        """)

    with st.expander("🔄 **Flow Portal** - Workflow Automation"):
        st.markdown("""
        The Flow Portal enables:
        - Visual workflow design
        - Multi-step AI processes
        - Data pipeline creation
        - Batch processing
        - Integration with external services

        **Best for:** Complex tasks, automation, data processing
        """)

    with st.expander("🤖 **RAG Portal** - Knowledge-Augmented AI"):
        st.markdown("""
        The RAG Portal offers:
        - Document ingestion and indexing
        - Semantic search
        - Knowledge-grounded responses
        - Source attribution
        - Custom knowledge bases

        **Best for:** Document Q&A, research, knowledge management
        """)

    with st.expander("🛠️ **Setup Portal** - System Configuration"):
        st.markdown("""
        The Setup Portal (this portal) provides:
        - System health checks
        - Database maintenance
        - Configuration management
        - Service integration
        - Troubleshooting tools

        **Best for:** System administration, initial setup, maintenance
        """)

    # Tips section
    st.markdown("---")
    st.info("""
    ### 💡 **Portal Tips:**
    - Each portal runs on a different port (8501, 8502, etc.)
    - You can run multiple portals simultaneously
    - Check the console for the portal URL after launching
    - Use Ctrl+C in the terminal to stop a portal
    """)


def render_portal_card(portal):
    """Render a single portal card."""
    with st.container():
        # Determine status icon
        status_icon = "✅" if portal.get('active', False) else "🔄"
        portal_icon = "🔧"  # Default icon

        # Card styling with border
        st.markdown(
            f"""
            <div style="
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
                background-color: #f9f9f9;
            ">
                <h4>{portal_icon} {portal.get('name', 'Unknown Portal')} {status_icon}</h4>
                <p style="color: #666; font-size: 14px;">
                    Port: {portal.get('port', 'Auto')}
                </p>
                <p style="color: #888; font-size: 12px;">
                    Status: {'Active' if portal.get('active', False) else 'Inactive'}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Launch button (only for active portals)
        if portal.get('active', False):
            portal_name = portal.get('name', 'Portal')
            launch_script = f"run_{portal_name.lower()}_app.py"

            if st.button(
                f"Launch {portal_name}",
                key=f"launch_{portal_name}",
                use_container_width=True
            ):
                launch_portal(launch_script)


def launch_portal(script_file):
    """Launch a portal script."""
    try:
        # Check if file exists
        if not os.path.exists(script_file):
            st.error(f"❌ Portal file not found: {script_file}")
            return

        # Launch in background
        if os.name == 'nt':  # Windows
            subprocess.Popen(
                f'start cmd /k python {script_file}',
                shell=True
            )
        else:  # Unix/Linux/Mac
            subprocess.Popen(
                f'gnome-terminal -- python {script_file}',
                shell=True
            )

        st.success(f"✅ Launching {script_file}...")
        st.info("Check your terminal/console for the portal URL")

    except Exception as e:
        st.error(f"❌ Failed to launch portal: {str(e)}")
        st.info("Try running manually from terminal: python " + script_file)