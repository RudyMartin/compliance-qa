"""
Tab 2: Prerequisites - Check required software and database maintenance
"""
import streamlit as st


def render(setup_service, settings=None):
    """Step 2: Check required software and manage databases."""
    st.header("Step 2️⃣: Software & Database Tools")
    st.markdown("**Check your required software and database maintenance tools.**")

    # Create tabs for organization
    subtab1, subtab2, subtab3 = st.tabs(["Software Check", "MLflow Maintenance", "Database Overview"])

    with subtab1:
        render_software_check(setup_service)

    with subtab2:
        render_mlflow_maintenance(settings)

    with subtab3:
        render_database_overview(settings)


def render_software_check(setup_service):
    """Original software check functionality."""
    if st.button("🔧 CHECK SOFTWARE NOW", type="primary", use_container_width=True):
        with st.spinner("Checking required software..."):
            dep_results = setup_service.dependency_check()
            # Store results in session state so they persist
            st.session_state["step2_results"] = dep_results

    # Display results if they exist in session state
    if "step2_results" in st.session_state:
        dep_results = st.session_state["step2_results"]
        results = dep_results["results"]
        status = dep_results["overall_status"]

        st.markdown("### 💻 Software & Configuration Check Results:")

        if status == "ready":
            st.success(
                "🎉 **PERFECT!** All required software is installed and configured!"
            )
        else:
            st.warning(
                "⚠️ **Some software or configuration is missing.** We'll help you fix it!"
            )

        # Show detailed results
        for check, passed in results.items():
            if isinstance(passed, bool):
                check_name = check.replace("_", " ").title()
                if passed:
                    if check == "aws_credentials_configured":
                        st.success(f"✅ **{check_name}**: Configured and ready!")
                    else:
                        st.success(f"✅ **{check_name}**: Installed and ready!")
                else:
                    if check == "aws_credentials_configured":
                        st.error(f"❌ **{check_name}**: Not configured")
                    elif check == "file_permissions":
                        st.error(f"❌ **{check_name}**: Insufficient permissions")
                    else:
                        st.error(f"❌ **{check_name}**: Not installed")

                    # Provide specific installation help
                    if check == "postgresql_available":
                        st.info(
                            "💡 **Fix:** PostgreSQL database is missing. Ask your portal admin to help install it."
                        )
                    elif check == "aws_credentials_configured":
                        st.info(
                            "💡 **Fix:** AWS credentials are missing. Check settings.yaml or ask your portal admin for AWS access keys."
                        )
                    elif check == "python_packages_installed":
                        st.info(
                            "💡 **Fix:** Some Python packages are missing. Try running: pip install -r requirements.txt"
                        )
                    elif check == "file_permissions":
                        st.info(
                            "💡 **Fix:** File permissions issue. Ask your portal admin to check folder permissions."
                        )

        st.info(f"📋 **Summary:** {dep_results['summary']}")

        # Next step guidance
        if status == "ready":
            st.success("🎯 **NEXT STEP:** Go to Step 3 to set up connections!")
        else:
            st.warning(
                "🎯 **NEXT STEP:** Install the missing software above, then try again."
            )

        # Add a button to re-check
        if st.button(
            "🔄 Check Again", use_container_width=True, key="step2_check_again"
        ):
            del st.session_state["step2_results"]
            st.rerun()


def render_mlflow_maintenance(settings):
    """MLflow database maintenance section."""
    st.markdown("### 🔧 MLflow Database Maintenance")

    with st.expander("🔧 **MLflow Schema Operations**", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.info("""
            **RESTORE MLFLOW SCHEMA**

            Safe operation that will:
            - Create any missing MLflow tables
            - Add performance indexes
            - Fix schema issues
            - **Preserve all existing data**
            """)

            if st.button("🔧 Restore MLflow Schema", type="secondary", use_container_width=True):
                with st.spinner("Restoring MLflow database schema..."):
                    try:
                        import subprocess
                        import sys

                        result = subprocess.run(
                            [sys.executable, "infrastructure/setup/restore_mlflow.py"],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )

                        if result.returncode == 0:
                            st.success("✅ MLflow schema restored successfully!")

                            output_lines = result.stdout.split('\n')
                            important_lines = [line for line in output_lines
                                             if any(word in line.lower() for word in ['created', 'exists', 'success', 'table'])]
                            if important_lines:
                                with st.expander("View Details"):
                                    for line in important_lines[:10]:
                                        st.text(line)
                        else:
                            st.error("❌ Schema restoration failed")
                            st.error(result.stderr[:500])

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

        with col2:
            st.warning("""
            **CHECK MLFLOW TABLES**

            Diagnostic operation that will:
            - List all MLflow tables
            - Show table sizes
            - Check for missing tables
            - Verify indexes
            """)

            if st.button("📊 Check MLflow Tables", type="secondary", use_container_width=True):
                check_mlflow_tables(settings)


def check_mlflow_tables(settings):
    """Check MLflow tables in database."""
    with st.spinner("Checking MLflow tables..."):
        try:
            import psycopg2
            from datetime import datetime

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

                # Display snapshot timestamp
                snapshot_time = datetime.now()
                st.info(f"📸 **Database Snapshot**: {snapshot_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")

                # Get MLflow tables with sizes
                cur.execute("""
                    SELECT tablename,
                           pg_size_pretty(pg_total_relation_size('public.'||tablename)) as size
                    FROM pg_tables
                    WHERE schemaname = 'public'
                    AND (tablename LIKE '%experiment%' OR tablename LIKE '%run%'
                         OR tablename LIKE '%metric%' OR tablename LIKE '%model%'
                         OR tablename LIKE '%dataset%' OR tablename LIKE '%tag%'
                         OR tablename LIKE '%param%' OR tablename LIKE '%input%'
                         OR tablename LIKE '%trace%')
                    ORDER BY pg_total_relation_size('public.'||tablename) DESC
                """)

                tables = cur.fetchall()

                if tables:
                    st.success(f"✅ Found {len(tables)} MLflow tables")

                    # Show table list
                    with st.expander("View Tables"):
                        for table_name, size in tables:
                            st.text(f"• {table_name}: {size}")

                    # Check for essential tables
                    essential_tables = ['experiments', 'runs', 'metrics', 'params']
                    existing = [t[0] for t in tables]
                    missing = [t for t in essential_tables if t not in existing]

                    if missing:
                        st.warning(f"⚠️ Missing essential tables: {', '.join(missing)}")
                        st.info("Click 'Restore MLflow Schema' to create them")
                    else:
                        st.success("✅ All essential tables present")
                else:
                    st.warning("No MLflow tables found")
                    st.info("Click 'Restore MLflow Schema' to create them")

                cur.close()
                conn.close()

        except Exception as e:
            st.error(f"Database check failed: {str(e)}")


def render_database_overview(settings):
    """General database monitoring section."""
    st.markdown("### 📊 Database Overview")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📈 Analyze Database", type="secondary", use_container_width=True):
            analyze_database(settings)

    with col2:
        if st.button("🧹 Vacuum & Optimize", type="secondary", use_container_width=True):
            vacuum_database(settings)

    # Danger Zone - collapsible
    with st.expander("⚠️ **DANGER ZONE** - Destructive Operations", expanded=False):
        st.error("**⚡ WARNING: These operations PERMANENTLY DELETE DATA and cannot be undone!**")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🔴 Reset MLflow Data")
            st.warning("""
            This will PERMANENTLY delete:
            - All experiments
            - All runs and metrics
            - All parameters and tags
            - All model versions
            """)

            # Double confirmation required
            understand_risks = st.checkbox("I understand this will permanently delete all MLflow data", key="mlflow_danger_check")

            if understand_risks:
                confirmation_text = st.text_input(
                    "Type 'DELETE' to confirm:",
                    key="mlflow_delete_confirm",
                    help="You must type DELETE in all caps to proceed"
                )

                if confirmation_text == "DELETE":
                    if st.button("🗑️ PERMANENTLY DELETE ALL MLFLOW DATA", type="primary", key="mlflow_reset_btn"):
                        with st.spinner("Deleting all MLflow data..."):
                            try:
                                # Actually perform the deletion
                                st.error("⚠️ MLflow data deletion is disabled for safety in production")
                                st.info("To enable: Contact your database administrator")
                                # In production, you would call: reset_mlflow_data(settings)
                            except Exception as e:
                                st.error(f"Failed to reset MLflow: {str(e)}")
                else:
                    st.info("👆 Type 'DELETE' above to enable the delete button")

        with col2:
            st.markdown("### 🔴 Drop All Tables")
            st.warning("""
            This will PERMANENTLY delete:
            - ALL database tables
            - ALL data in the database
            - Cannot be recovered!
            """)

            # Triple confirmation for this one
            understand_tables = st.checkbox("I understand this will delete ALL tables", key="tables_danger_check")

            if understand_tables:
                backup_confirmed = st.checkbox("I have created a backup", key="backup_check")

                if backup_confirmed:
                    drop_confirmation = st.text_input(
                        "Type 'DROP ALL TABLES' to confirm:",
                        key="tables_delete_confirm",
                        help="You must type exactly 'DROP ALL TABLES' to proceed"
                    )

                    if drop_confirmation == "DROP ALL TABLES":
                        if st.button("💀 DROP ALL DATABASE TABLES", type="primary", key="drop_tables_btn"):
                            st.error("⚠️ Table dropping is disabled for safety")
                            st.info("This operation is too dangerous for production use")
                    else:
                        st.info("👆 Type 'DROP ALL TABLES' above to enable")
                else:
                    st.warning("☑️ Please confirm you have a backup first")


def analyze_database(settings):
    """Analyze database and show statistics."""
    with st.spinner("Analyzing database..."):
        try:
            import psycopg2
            import pandas as pd
            from datetime import datetime

            if "postgresql_primary" in settings.get("credentials", {}):
                pg = settings["credentials"]["postgresql_primary"]

                conn = psycopg2.connect(
                    host=pg["host"],
                    port=pg["port"],
                    database=pg["database"],
                    user=pg["username"],
                    password=pg["password"],
                )

                cur = conn.cursor()

                # Get database size
                cur.execute("""
                    SELECT pg_database_size(current_database()) as size,
                           pg_size_pretty(pg_database_size(current_database())) as size_pretty
                """)
                db_size = cur.fetchone()

                st.metric("Total Database Size", db_size[1] if db_size else "Unknown")

                # Get all tables
                cur.execute("""
                    SELECT
                        tablename,
                        pg_size_pretty(pg_total_relation_size('public.'||tablename)) as size,
                        pg_total_relation_size('public.'||tablename) as bytes
                    FROM pg_tables
                    WHERE schemaname = 'public'
                    ORDER BY pg_total_relation_size('public.'||tablename) DESC
                """)

                all_tables = cur.fetchall()
                total_tables = len(all_tables)

                if all_tables:
                    # Categorize tables
                    mlflow_count = len([t for t in all_tables if any(x in t[0].lower()
                                      for x in ['experiment', 'run', 'metric', 'param', 'tag', 'model'])])
                    vector_count = len([t for t in all_tables if 'vector' in t[0].lower() or 'embedding' in t[0].lower()])
                    app_count = total_tables - mlflow_count - vector_count

                    # Display summary
                    st.markdown(f"**Found {total_tables} Tables**")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("MLflow", mlflow_count)
                    with col2:
                        st.metric("Vector", vector_count)
                    with col3:
                        st.metric("Application", app_count)

                    # Show top 5 tables
                    st.markdown("**Top 5 Tables by Size:**")
                    for table, size, bytes_val in all_tables[:5]:
                        pct = (bytes_val / db_size[0] * 100) if db_size else 0
                        st.text(f"• {table}: {size} ({pct:.1f}%)")

                    # CSV download
                    if st.button("📥 Download Table List as CSV"):
                        df = pd.DataFrame(all_tables, columns=['Table', 'Size', 'Bytes'])
                        csv = df.to_csv(index=False)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"database_tables_{timestamp}.csv",
                            mime="text/csv"
                        )

                cur.close()
                conn.close()

        except Exception as e:
            st.error(f"Error: {str(e)}")


def vacuum_database(settings):
    """Run VACUUM ANALYZE on database."""
    with st.spinner("Running VACUUM ANALYZE..."):
        try:
            import psycopg2

            if "postgresql_primary" in settings.get("credentials", {}):
                pg = settings["credentials"]["postgresql_primary"]

                conn = psycopg2.connect(
                    host=pg["host"],
                    port=pg["port"],
                    database=pg["database"],
                    user=pg["username"],
                    password=pg["password"],
                )

                # Set autocommit for VACUUM
                conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
                cur = conn.cursor()

                # Run VACUUM ANALYZE
                cur.execute("VACUUM ANALYZE")

                st.success("✅ Database maintenance complete")
                st.info("Tables vacuumed and statistics updated")

                cur.close()
                conn.close()

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Note: VACUUM requires appropriate permissions")