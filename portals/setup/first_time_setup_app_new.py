"""
Streamlit portal for first-time setup and configuration.
This is the simplified version using modular tab files.
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import tab modules
from portals.setup import (
    t_system_check,
    t_prerequisites,
    t_connections,
    t_ai_models,
    t_health_check,
    t_explore_portals
)

# Page configuration
st.set_page_config(
    page_title="AI Portal Setup Wizard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better UI
st.markdown(
    """
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-left: 20px;
        padding-right: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def check_step_completion():
    """Check which setup steps have been completed."""
    step1_done = "step1_results" in st.session_state
    step2_done = "step2_results" in st.session_state
    step3_done = "step3_results" in st.session_state
    step4_done = "step4_results" in st.session_state

    return step1_done, step2_done, step3_done, step4_done


def main():
    """Main application entry point."""
    st.title("🚀 AI Portal Setup Wizard")
    st.markdown("**Welcome! Let's get your AI portal ready to use.**")

    # Initialize setup service with PathManager
    try:
        from domain.services.setup_service import SetupService
        from common.utilities.path_manager import get_path_manager

        path_mgr = get_path_manager()
        root_path = Path(path_mgr.root_folder)
        setup_service = SetupService(root_path)
    except ImportError as e:
        st.error(f"❌ Could not load setup service: {str(e)}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error initializing setup service: {str(e)}")
        st.stop()

    # Load settings for some tabs
    try:
        from infrastructure.yaml_loader import get_settings_loader
        settings_loader = get_settings_loader()
        settings = settings_loader._load_settings()
    except Exception as e:
        st.warning(f"⚠️ Could not load settings: {str(e)}")
        settings = {}

    # Check step completion for visual feedback
    step1_done, step2_done, step3_done, step4_done = check_step_completion()

    # Tab labels with proper numbering and descriptions
    tab_labels = [
        "1️⃣ System & AWS Setup",
        "2️⃣ Software & Database Tools",
        "3️⃣ MLflow Config",
        "4️⃣ AI Models (Bedrock)",
        "5️⃣ Health Check",
        "6️⃣ Explore Portals",
    ]

    # Create tabs
    tabs = st.tabs(tab_labels)

    # Render each tab
    with tabs[0]:
        t_system_check.render(setup_service)

    with tabs[1]:
        t_prerequisites.render(setup_service, settings)

    with tabs[2]:
        t_connections.render(setup_service, settings)

    with tabs[3]:
        t_ai_models.render(setup_service)

    with tabs[4]:
        t_health_check.render(setup_service)

    with tabs[5]:
        t_explore_portals.render(setup_service)

    # Footer
    st.markdown("---")
    st.caption("AI Portal Setup Wizard v2.0 | Simplified Modular Edition")


# PGVector maintenance stays in main file for now
def render_pgvector_maintenance(settings):
    """PGVector database maintenance - keeping in main file to avoid breaking."""
    with st.expander("🔮 **PGVector Database Maintenance**", expanded=False):
        pgvector_container = st.container(border=True)
        with pgvector_container:
            st.info("Vector database operations and optimization")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("📊 Check PGVector Tables", type="secondary", use_container_width=True):
                    check_pgvector_tables(settings)

            with col2:
                if st.button("🔧 Optimize Vector Indexes", type="secondary", use_container_width=True):
                    optimize_pgvector(settings)


def check_pgvector_tables(settings):
    """Check pgvector tables - simplified version."""
    with st.spinner("Checking pgvector tables..."):
        try:
            import psycopg2

            if 'postgresql_primary' in settings.get('credentials', {}):
                pg = settings['credentials']['postgresql_primary']

                conn = psycopg2.connect(
                    host=pg['host'],
                    port=pg['port'],
                    database=pg['database'],
                    user=pg['username'],
                    password=pg['password']
                )

                cur = conn.cursor()

                # Check pgvector extension
                cur.execute("""
                    SELECT installed_version
                    FROM pg_available_extensions
                    WHERE name = 'vector'
                """)
                vector_version = cur.fetchone()

                if vector_version and vector_version[0]:
                    st.success(f"✅ PGVector Extension v{vector_version[0]}")
                else:
                    st.warning("⚠️ PGVector extension not installed")

                cur.close()
                conn.close()

        except Exception as e:
            st.error(f"Error checking pgvector: {str(e)}")


def optimize_pgvector(settings):
    """Optimize pgvector indexes - simplified version."""
    with st.spinner("Optimizing vector indexes..."):
        try:
            import psycopg2

            if 'postgresql_primary' in settings.get('credentials', {}):
                pg = settings['credentials']['postgresql_primary']

                conn = psycopg2.connect(
                    host=pg['host'],
                    port=pg['port'],
                    database=pg['database'],
                    user=pg['username'],
                    password=pg['password']
                )

                cur = conn.cursor()

                # Get vector tables
                cur.execute("""
                    SELECT tablename
                    FROM pg_tables t
                    JOIN pg_class c ON c.relname = t.tablename
                    WHERE t.schemaname = 'public'
                    AND EXISTS (
                        SELECT 1 FROM pg_attribute a
                        JOIN pg_type typ ON a.atttypid = typ.oid
                        WHERE a.attrelid = c.oid
                        AND typ.typname = 'vector'
                    )
                """)

                vector_tables = cur.fetchall()

                if vector_tables:
                    for (table_name,) in vector_tables:
                        try:
                            cur.execute(f"REINDEX TABLE {table_name}")
                            cur.execute(f"ANALYZE {table_name}")
                        except:
                            pass

                    conn.commit()
                    st.success(f"✅ Optimized {len(vector_tables)} vector table(s)")
                else:
                    st.info("No vector tables found to optimize")

                cur.close()
                conn.close()

        except Exception as e:
            st.error(f"Error optimizing: {str(e)}")


if __name__ == "__main__":
    main()