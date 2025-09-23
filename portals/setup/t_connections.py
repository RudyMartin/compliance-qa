"""
Tab 3: Connections - Configure MLflow and database connections
"""
import streamlit as st


def render(setup_service, settings):
    """Step 3: Configure database and cloud connections."""
    st.header("Step 3️⃣: Connections")
    st.markdown(
        "**Configure your MLflow tracking server and database connections.**"
    )

    # MLflow Configuration Section
    st.markdown("### 🎯 MLflow Configuration")

    mlflow_config = settings.get("integrations", {}).get("mlflow", {})
    backend_store = mlflow_config.get("backend_store_uri", "auto_select")
    artifact_store = mlflow_config.get("artifact_store", "")

    col1, col2 = st.columns(2)

    with col1:
        # Backend Store Configuration
        st.markdown("**Backend Store (Metrics & Parameters)**")
        backend_options = [
            "Inherit from Primary Database",
            "Custom PostgreSQL URI",
            "Local SQLite (Development)",
        ]

        if backend_store == "auto_select":
            current_backend = backend_options[0]
        elif backend_store.startswith("postgresql://"):
            current_backend = backend_options[1]
        else:
            current_backend = backend_options[2]

        backend_choice = st.radio(
            "Select Backend Store:",
            backend_options,
            index=backend_options.index(current_backend),
        )

        if backend_choice == "Custom PostgreSQL URI":
            custom_uri = st.text_input(
                "PostgreSQL URI",
                value=backend_store if backend_store != "auto_select" else "",
                placeholder="postgresql://user:pass@host:5432/db",
                type="password",
            )

    with col2:
        # Artifact Store Configuration
        st.markdown("**Artifact Store (Models & Files)**")
        st.info("Currently using S3 for artifact storage")

        if artifact_store:
            if artifact_store.startswith("s3://"):
                st.success(f"✅ S3 configured: {artifact_store}")
            else:
                st.warning(f"⚠️ Local storage: {artifact_store}")
        else:
            st.warning("⚠️ No artifact store configured")

        if st.button("🔧 Configure S3 Artifacts"):
            st.info("S3 configuration is available in the System Check tab")

    # MLflow Status Check
    st.markdown("---")
    st.markdown("### 🔍 MLflow Status")

    if st.button("🔍 Check MLflow Connection", type="primary", use_container_width=True):
        with st.spinner("Checking MLflow backend..."):
            try:
                import psycopg2
                from urllib.parse import urlparse

                # Check if MLflow is using PostgreSQL backend
                if "postgresql_primary" in settings.get("credentials", {}):
                    pg = settings["credentials"]["postgresql_primary"]

                    try:
                        conn = psycopg2.connect(
                            host=pg["host"],
                            port=pg["port"],
                            database=pg["database"],
                            user=pg["username"],
                            password=pg["password"],
                        )
                        cur = conn.cursor()

                        # Check for MLflow tables
                        cur.execute("""
                            SELECT COUNT(*) FROM pg_tables
                            WHERE schemaname = 'public'
                            AND (tablename LIKE '%experiment%' OR tablename LIKE '%run%'
                                 OR tablename LIKE '%metric%' OR tablename LIKE '%model%'
                                 OR tablename LIKE '%tag%' OR tablename LIKE '%param%'
                                 OR tablename LIKE '%dataset%' OR tablename LIKE '%input%'
                                 OR tablename LIKE '%trace%' OR tablename LIKE '%registered%')
                        """)
                        mlflow_table_count = cur.fetchone()[0]

                        # MLflow 2.0+ has ~23 tables, older versions had ~15
                        if mlflow_table_count >= 20:
                            st.success(f"✅ MLflow backend fully configured")
                            st.info(f"Found {mlflow_table_count} MLflow tables (Complete installation)")
                        elif mlflow_table_count >= 15:
                            st.success(f"✅ MLflow backend connected")
                            st.info(f"Found {mlflow_table_count} MLflow tables (Standard installation)")
                        elif mlflow_table_count >= 4:
                            st.warning(f"⚠️ MLflow partially configured: {mlflow_table_count} tables found")
                            st.info("Some MLflow features may not work. Consider restoring schema.")
                        else:
                            st.error(f"❌ MLflow tables missing: Only {mlflow_table_count} tables found")
                            st.info("Use Database Tools tab to restore MLflow schema")

                        cur.close()
                        conn.close()

                    except Exception as e:
                        st.error(f"❌ Could not connect to PostgreSQL: {str(e)}")
                else:
                    st.warning("PostgreSQL credentials not configured")

            except ImportError:
                st.error("psycopg2 not installed. Run: pip install psycopg2-binary")
            except Exception as e:
                st.error(f"Error checking MLflow: {str(e)}")

    # Save Configuration
    st.markdown("---")
    if st.button("💾 Save MLflow Configuration", type="secondary", use_container_width=True):
        try:
            # Update settings based on backend choice
            if backend_choice == "Inherit from Primary Database":
                settings["integrations"]["mlflow"]["backend_store_uri"] = "auto_select"
            elif backend_choice == "Custom PostgreSQL URI" and "custom_uri" in locals():
                settings["integrations"]["mlflow"]["backend_store_uri"] = custom_uri

            # Save settings
            import yaml
            from infrastructure.yaml_loader import get_settings_loader

            loader = get_settings_loader()
            with open(loader.settings_path, "w") as f:
                yaml.safe_dump(settings, f, default_flow_style=False, indent=2)

            st.success("✅ MLflow configuration saved!")
            st.info("Restart any running MLflow processes for changes to take effect")

        except Exception as e:
            st.error(f"Failed to save configuration: {str(e)}")

    # Additional Integrations Info
    st.markdown("---")
    st.subheader("🔮 Future Integrations")
    st.info("""
    Coming soon:
    - **LDAP**: Enterprise authentication
    - **SSO**: Single sign-on integration
    - **Kafka**: Event streaming
    - **Redis**: Caching layer
    - **Datadog**: Monitoring and observability
    """)

    st.success("✅ Basic connections configured! For database maintenance, see the Database Tools tab.")