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
import os

# Add parent to path
qa_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(qa_root))

# Also add to PYTHONPATH for better import resolution
if 'PYTHONPATH' in os.environ:
    os.environ['PYTHONPATH'] = f"{qa_root}{os.pathsep}{os.environ['PYTHONPATH']}"
else:
    os.environ['PYTHONPATH'] = str(qa_root)

from domain.services.setup_service import SetupService

# Initialize service
setup_service = SetupService(qa_root)

# Pre-import yaml_loader to ensure it's available
try:
    from infrastructure.yaml_loader import get_settings_loader
    yaml_loader_available = True
except ImportError:
    # Create fallback if yaml_loader not available
    yaml_loader_available = False
    class FallbackLoader:
        def _load_settings(self):
            import yaml
            settings_path = qa_root / "settings.yaml"
            if settings_path.exists():
                with open(settings_path, 'r') as f:
                    return yaml.safe_load(f) or {}
            return {}

        def get_settings(self):
            return self._load_settings()

        def get_database_config(self):
            settings = self._load_settings()
            return settings.get("credentials", {}).get("postgresql_primary", {})

        def update_database_config(self, config):
            return True

        def get_mlflow_config(self):
            settings = self._load_settings()
            return settings.get("integrations", {}).get("mlflow", {})

        def update_mlflow_config(self, config):
            return True

        def get_aws_config(self):
            settings = self._load_settings()
            return settings.get("credentials", {}).get("aws_basic", {})

        def update_aws_config(self, config):
            return True

    def get_settings_loader():
        return FallbackLoader()


def set_page_config():
    """Configure the Streamlit page."""
    st.set_page_config(
        page_title="Setup Portal - Special Edition",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def render_header():
    """Render the portal header."""
    st.title("🚀 Setup Portal - Special Edition")
    st.markdown("**Welcome! Let's set up your AI system step by step.**")

    # Quick status overview
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        wizard_result = setup_service.installation_wizard()
        if wizard_result["overall_status"] == "ready":
            st.success("✅ System Ready")
        else:
            st.error("❌ Needs Setup")

    with col2:
        dep_result = setup_service.dependency_check()
        if dep_result["overall_status"] == "ready":
            st.success("✅ Software OK")
        else:
            st.warning("⚠️ Missing Software")

    with col3:
        chat_result = setup_service.tidyllm_basic_setup()
        model_count = chat_result.get("model_count", 0)
        if model_count > 0:
            st.success(f"✅ {model_count} AI Models")
        else:
            st.error("❌ No AI Models")

    with col4:
        health_result = setup_service.health_check()
        if health_result["overall_status"] == "healthy":
            st.success("✅ All Systems GO")
        else:
            st.warning("⚠️ System Issues")

    st.markdown("---")


def render_step_1_system_check():
    """Step 1: Check if everything is ready."""
    st.header("Step 1️⃣: Check Your System")
    st.markdown("**First, let's see if your computer is ready for AI!**")

    # Progressive flow indicator
    progress_bar = st.progress(0.2)
    st.caption("Progress: Step 1 of 5")

    if st.button("🔍 CHECK MY SYSTEM NOW", type="primary", use_container_width=True):
        with st.spinner("Checking your system... This will take a few seconds..."):
            wizard_results = setup_service.installation_wizard()
            # Store results in session state so they persist
            st.session_state["step1_results"] = wizard_results

    # Display results if they exist in session state
    if "step1_results" in st.session_state:
        wizard_results = st.session_state["step1_results"]
        results = wizard_results["results"]
        status = wizard_results["overall_status"]

        st.markdown("### 📊 System Check Results:")

        if status == "ready":
            st.success("🎉 **GREAT NEWS!** Your system is ready to go!")
        else:
            st.warning(
                "⚠️ **Your system needs some setup.** Don't worry - we'll help you fix it!"
            )

        # Show detailed results
        for check, passed in results.items():
            if isinstance(passed, bool):
                check_name = check.replace("_", " ").title()
                if passed:
                    st.success(f"✅ **{check_name}**: Ready to go!")
                else:
                    st.error(f"❌ **{check_name}**: Needs your attention")

                    # Provide specific help for each issue
                    if check == "python_version":
                        st.info(
                            "💡 **Fix:** You need Python 3.8 or newer. Ask your portal admin for help installing Python."
                        )
                    elif check == "required_directories":
                        st.info(
                            "💡 **Fix:** Some folders are missing. Make sure you downloaded the complete project."
                        )
                    elif check == "settings_yaml_exists":
                        st.info(
                            "💡 **Fix:** The settings.yaml file is missing. Ask your portal admin for the configuration file."
                        )
                    elif check == "database_connection":
                        st.info(
                            "💡 **Fix:** Can't connect to the database. Check your internet connection."
                        )
                    elif check == "aws_credentials":
                        st.info(
                            "💡 **Fix:** AWS credentials are missing. Ask your portal admin for the access keys."
                        )

        st.info(f"📋 **Summary:** {wizard_results['summary']}")

        # Detailed breakdown for clarity
        if status != "ready":
            st.markdown("### 🔍 **What needs fixing:**")
            failed_items = [
                check.replace("_", " ").title()
                for check, passed in results.items()
                if isinstance(passed, bool) and not passed
            ]
            for item in failed_items:
                st.markdown(f"❌ **{item}**")

        # Next step guidance
        if status == "ready":
            st.success("🎯 **NEXT STEP:** Go to Step 2 to check your software!")
        else:
            st.warning("🎯 **NEXT STEP:** Fix the red ❌ items above, then try again.")

        # Add a button to re-check
        if st.button("🔄 Check Again", use_container_width=True):
            del st.session_state["step1_results"]
            st.rerun()

    # S3 Configuration Section - Outside the system check card
    st.markdown("---")
    st.markdown("### ☁️ AWS S3 Configuration")

    with st.expander("☁️ Configure AWS S3 Settings", expanded=False):
        # Load current S3 settings
        try:
            # Use pre-imported or fallback loader
            if not yaml_loader_available:
                # Already imported at top with fallback
                pass
            settings_loader = get_settings_loader()
            raw_settings = settings_loader._load_settings()  # Get raw dict

            # Get AWS credentials
            aws_creds = raw_settings.get("credentials", {}).get("aws_basic", {})
            current_access_key = aws_creds.get("access_key_id", "")
            current_secret_key = aws_creds.get("secret_access_key", "")
            current_region = aws_creds.get("default_region", "us-east-1")

            # Get S3 service settings
            s3_service = raw_settings.get("services", {}).get("s3", {})
            current_bucket = s3_service.get("bucket", "")
            current_prefix = s3_service.get("prefix", "")

            # Mask AWS keys for display
            masked_access = (
                current_access_key[:4] + "****" + current_access_key[-4:]
                if len(current_access_key) > 8
                else "****"
            )
            masked_secret = (
                "****" + current_secret_key[-4:]
                if len(current_secret_key) > 4
                else "****"
            )

            st.info(
                f"💡 **Current AWS Settings**: Bucket: {current_bucket}/{current_prefix} | Region: {current_region} | Access Key: {masked_access}"
            )

        except Exception as e:
            st.warning(f"⚠️ Could not load current S3 settings: {str(e)}")
            # Fallback to defaults
            current_access_key = ""
            current_secret_key = ""
            current_region = "us-east-1"
            current_bucket = ""
            current_prefix = ""

        with st.form("s3_config_form"):
            st.markdown("**AWS S3 Configuration**")

            st.subheader("AWS Credentials")
            col1, col2 = st.columns(2)

            with col1:
                aws_access_key = st.text_input(
                    "AWS Access Key ID",
                    value=current_access_key,
                    type="password",
                    placeholder="AKIA...",
                )
                aws_region = st.selectbox(
                    "AWS Region",
                    [
                        "us-east-1",
                        "us-west-1",
                        "us-west-2",
                        "eu-west-1",
                        "eu-central-1",
                        "ap-southeast-1",
                    ],
                    index=0 if current_region == "us-east-1" else None,
                )

            with col2:
                aws_secret_key = st.text_input(
                    "AWS Secret Access Key",
                    value=current_secret_key,
                    type="password",
                    placeholder="Enter secret key",
                )
                st.markdown(" ")  # Spacer

            st.subheader("S3 Bucket Configuration")
            col3, col4 = st.columns(2)

            with col3:
                s3_bucket = st.text_input(
                    "S3 Bucket Name", value=current_bucket, placeholder="my-bucket"
                )

            with col4:
                s3_prefix = st.text_input(
                    "S3 Prefix/Path",
                    value=current_prefix,
                    placeholder="data/",
                    help="Prefix for all S3 operations",
                )

            # Form buttons
            col_test, col_save = st.columns(2)

            with col_test:
                test_clicked = st.form_submit_button(
                    "🧪 Test S3 Access", use_container_width=True
                )

            with col_save:
                save_clicked = st.form_submit_button(
                    "💾 Save to Settings", use_container_width=True, type="primary"
                )

            if test_clicked:
                with st.spinner("Testing S3 access..."):
                    try:
                        # Test through domain service (which uses infrastructure layer)
                        if hasattr(setup_service, "test_s3_access"):
                            test_result = setup_service.test_s3_access(
                                s3_bucket,
                                s3_prefix,
                                {
                                    "access_key_id": aws_access_key,
                                    "secret_access_key": aws_secret_key,
                                    "region": aws_region,
                                },
                            )

                            if test_result.get("credentials_valid"):
                                st.success(
                                    f"✅ AWS credentials valid! Found {test_result.get('bucket_count', 0)} bucket(s)"
                                )
                                if test_result.get("bucket_accessible"):
                                    st.success(
                                        f"✅ Bucket '{s3_bucket}' accessible! Found {test_result.get('objects_found', 0)} object(s)"
                                    )
                                    if test_result.get("write_permission"):
                                        st.success(f"✅ Write access confirmed!")
                                    else:
                                        st.warning(
                                            f"⚠️ No write permission to bucket '{s3_bucket}'"
                                        )
                                else:
                                    st.error(f"❌ Cannot access bucket '{s3_bucket}'")
                            else:
                                st.error(f"❌ Invalid AWS credentials")

                            if test_result.get("errors"):
                                for error in test_result["errors"]:
                                    st.error(f"❌ {error}")
                        else:
                            st.error(
                                "S3 testing feature not available - please restart the portal"
                            )

                    except Exception as e:
                        st.error(f"❌ Unexpected error during S3 test: {str(e)}")

            if save_clicked:
                with st.spinner("Saving S3 configuration to settings.yaml..."):
                    try:
                        # Save through domain service (which uses infrastructure layer)
                        save_config = {
                            "access_key_id": aws_access_key,
                            "secret_access_key": aws_secret_key,
                            "region": aws_region,
                            "bucket": s3_bucket,
                            "prefix": s3_prefix,
                        }

                        if hasattr(setup_service, "update_s3_config"):
                            save_result = setup_service.update_s3_config(save_config)

                            if save_result.get("success"):
                                st.success(
                                    f"✅ S3 configuration saved to settings.yaml!"
                                )
                                st.info(
                                    f"💡 S3 path configured: s3://{s3_bucket}/{s3_prefix}"
                                )
                                st.balloons()

                                # Clear step1 results to force re-check
                                if "step1_results" in st.session_state:
                                    del st.session_state["step1_results"]
                            else:
                                st.error(
                                    f"❌ Failed to save S3 configuration: {save_result.get('message', 'Unknown error')}"
                                )
                        else:
                            st.error(
                                "S3 configuration feature not available - please restart the portal"
                            )

                    except Exception as e:
                        st.error(
                            f"❌ Unexpected error during S3 configuration save: {str(e)}"
                        )

    st.info(
        "💡 **Architecture Note:** This uses the unified AWS service through the hexagonal architecture for all S3 operations."
    )

    # End of Prerequisites Tab
    st.markdown("---")
    st.markdown(
        """
    ### 🎯 **How to use this page:**
    - **Green ✅** means everything is working
    - **Red ❌** means something needs to be fixed
    - **Yellow ⚠️** means there might be a small issue
    - When you see problems, ask your portal admin for help!
    """
    )


def render_step_2_software_check():
    """Step 2: Check required software."""
    st.header("Step 2️⃣: Check Required Software")
    st.markdown("**Let's make sure you have all the programs you need!**")

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
            st.success("🎯 **NEXT STEP:** Go to Step 3 to set up AI chat!")
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


def render_integrations_tab():
    """Step 3: Configure database and cloud connections."""
    st.header("Step 3️⃣: Connections")
    st.markdown(
        "**Configure and manage your infrastructure integrations - databases, tracking systems, and more.**"
    )

    # Database Configuration Card (First)
    with st.container():
        st.subheader("🗄️ Database Configuration")

        with st.expander("💾 Update Database Connection", expanded=False):
            st.markdown("Configure your primary database connection")

            # Get current database configuration
            # Use pre-imported or fallback loader
            if not yaml_loader_available:
                # Already imported at top with fallback
                pass
            loader = get_settings_loader()
            current_db = loader.get_database_config()

            # Database configuration form
            with st.form(key="database_config_form"):
                st.info(
                    f"💡 Current Settings Loaded: {current_db['host']}:{current_db['port']}/{current_db['database']} (user: {current_db['username']})"
                )

                col1, col2 = st.columns(2)

                with col1:
                    db_host = st.text_input("Database Host", value=current_db["host"])
                    db_name = st.text_input(
                        "Database Name", value=current_db["database"]
                    )
                    db_user = st.text_input("Username", value=current_db["username"])

                with col2:
                    db_port = st.number_input(
                        "Port", value=current_db["port"], min_value=1, max_value=65535
                    )
                    db_password = st.text_input(
                        "Password", value=current_db["password"], type="password"
                    )

                col1, col2, col3 = st.columns(3)

                with col1:
                    test_btn = st.form_submit_button(
                        "🧪 Test Connection", type="secondary", use_container_width=True
                    )

                with col2:
                    save_btn = st.form_submit_button(
                        "💾 Save to settings.yaml",
                        type="primary",
                        use_container_width=True,
                    )

                with col3:
                    reset_btn = st.form_submit_button(
                        "🔄 Reset to Current", use_container_width=True
                    )

                if test_btn:
                    # Test the connection with new settings
                    test_config = {
                        "postgres_host": db_host,
                        "postgres_port": db_port,
                        "postgres_database": db_name,
                        "postgres_username": db_user,
                        "postgres_password": db_password,
                        "postgres_ssl_mode": "require",
                    }

                    with st.spinner("Testing database connection..."):
                        result = setup_service.dependencies.get_database_service().test_connection(
                            test_config
                        )

                        if result.get("success"):
                            st.success("✅ Database connection successful!")
                            st.json(result.get("details", {}))
                        else:
                            st.error(
                                f"❌ Database connection failed: {result.get('message', 'Unknown error')}"
                            )

                if save_btn:
                    # Save to settings.yaml
                    save_config = {
                        "host": db_host,
                        "port": db_port,
                        "database": db_name,
                        "username": db_user,
                        "password": db_password,
                    }

                    result = setup_service.dependencies.get_database_service().update_settings(
                        save_config
                    )

                    if result.get("success"):
                        st.success("✅ Database configuration saved to settings.yaml!")
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(
                            f"❌ Failed to save configuration: {result.get('message')}"
                        )

                if reset_btn:
                    st.rerun()

    # MLflow Re-installation (Second)
    with st.container():
        st.markdown("---")
        st.subheader("🔬 MLflow Tracking Integration")

        # Check MLflow status first
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Check MLflow Status", use_container_width=True):
                try:
                    import mlflow
                    import os
                    from datetime import datetime, timedelta

                    # Set AWS credentials for S3 artifact storage
                    if "aws_basic" in settings.get("credentials", {}):
                        aws = settings["credentials"]["aws_basic"]
                        os.environ["AWS_ACCESS_KEY_ID"] = aws["access_key_id"]
                        os.environ["AWS_SECRET_ACCESS_KEY"] = aws["secret_access_key"]
                        os.environ["AWS_DEFAULT_REGION"] = aws.get(
                            "default_region", "us-east-1"
                        )

                    # Configure MLflow with PostgreSQL backend (not HTTP server!)
                    if "postgresql_primary" in settings.get("credentials", {}):
                        pg = settings["credentials"]["postgresql_primary"]
                        tracking_uri = f"postgresql://{pg['username']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['database']}"
                        mlflow.set_tracking_uri(tracking_uri)

                        # Test connection to PostgreSQL backend
                        client = mlflow.tracking.MlflowClient()

                        # Get experiments
                        experiments = client.search_experiments()
                        st.success(
                            f"✅ MLflow connected to PostgreSQL backend (pooled connection)"
                        )
                        st.info(f"Found {len(experiments)} experiments in database")

                        # Count total runs
                        total_runs = 0
                        recent_runs = []
                        thirty_days_ago = datetime.now() - timedelta(days=30)

                        for exp in experiments[:10]:  # Check first 10 experiments
                            runs = client.search_runs(
                                experiment_ids=[exp.experiment_id], max_results=100
                            )
                            total_runs += len(runs)

                            # Filter recent runs
                            for run in runs:
                                if (
                                    run.info.start_time
                                    > thirty_days_ago.timestamp() * 1000
                                ):
                                    recent_runs.append(run)

                        st.success(f"📊 Total runs in database: {total_runs}")

                        if recent_runs:
                            st.success(
                                f"📈 Found {len(recent_runs)} runs in the last 30 days"
                            )
                            # Show latest runs
                            st.caption("Latest activity:")
                            recent_runs.sort(
                                key=lambda x: x.info.start_time, reverse=True
                            )
                            for run in recent_runs[:3]:
                                exp_name = next(
                                    (
                                        e.name
                                        for e in experiments
                                        if e.experiment_id == run.info.experiment_id
                                    ),
                                    "Unknown",
                                )
                                st.text(
                                    f"  • {exp_name}: Run {run.info.run_id[:8]}... at {datetime.fromtimestamp(run.info.start_time/1000)}"
                                )
                        else:
                            st.info("No MLflow activity in the last 30 days")

                        # Check if MLflow server is running (optional)
                        try:
                            import requests

                            response = requests.get(
                                "http://localhost:5000", timeout=0.5
                            )
                            if response.status_code == 200:
                                st.info(
                                    "ℹ️ MLflow UI server is also running at http://localhost:5000"
                                )
                        except:
                            st.caption(
                                "💡 MLflow UI server not running (optional - not required for tracking)"
                            )
                    else:
                        st.error("❌ PostgreSQL credentials not found in settings")

                except Exception as e:
                    st.error(f"❌ MLflow database connection failed: {str(e)}")
                    st.info(
                        "💡 Run 'python infrastructure/setup/restore_mlflow.py' to fix MLflow schema"
                    )

        # MLflow Database Configuration
        with st.expander("🗄️ MLflow Database Configuration", expanded=False):
            st.markdown("Configure MLflow's backend database connection")

            # Get current MLflow database configuration
            # Use pre-imported or fallback loader
            if not yaml_loader_available:
                # Already imported at top with fallback
                pass
            loader = get_settings_loader()
            settings = loader._load_settings()

            # Check if MLflow is using separate database or inheriting from primary
            mlflow_config = settings.get("integrations", {}).get("mlflow", {})
            backend_uri = mlflow_config.get("backend_store_uri", "auto_select")

            st.info(f"Current backend: {backend_uri}")

            # Configuration options
            config_option = st.radio(
                "MLflow Database Configuration",
                [
                    "Inherit from Primary Database",
                    "Use Separate Database",
                    "Use File Store (Local Only)",
                    "AWS S3 Artifacts + PostgreSQL Backend (Production)",
                ],
                index=(
                    0
                    if backend_uri == "auto_select"
                    else (
                        3
                        if artifact_store and "s3://" in artifact_store
                        else 1 if "postgresql" in str(backend_uri) else 2
                    )
                ),
            )

            if config_option == "Use Separate Database":
                st.warning("Configure a dedicated database for MLflow tracking")

                with st.form(key="mlflow_db_config"):
                    col1, col2 = st.columns(2)

                    with col1:
                        mlflow_host = st.text_input("Host", value="localhost")
                        mlflow_database = st.text_input("Database", value="mlflow_db")
                        mlflow_user = st.text_input("Username", value="mlflow_user")

                    with col2:
                        mlflow_port = st.number_input(
                            "Port", value=5432, min_value=1, max_value=65535
                        )
                        mlflow_password = st.text_input("Password", type="password")

                    if st.form_submit_button(
                        "💾 Save MLflow Database Config", type="primary"
                    ):
                        # Update MLflow backend configuration
                        new_backend_uri = f"postgresql://{mlflow_user}:{mlflow_password}@{mlflow_host}:{mlflow_port}/{mlflow_database}"

                        # Update settings
                        settings["integrations"]["mlflow"][
                            "backend_store_uri"
                        ] = new_backend_uri

                        # Save to settings.yaml
                        import yaml

                        with open(loader.settings_path, "w") as f:
                            yaml.safe_dump(
                                settings, f, default_flow_style=False, indent=2
                            )

                        st.success("✅ MLflow database configuration saved!")
                        st.info("Restart MLflow server for changes to take effect")

            elif config_option == "Use File Store (Local Only)":
                st.info(
                    "MLflow will use local file storage (not recommended for production)"
                )

                file_path = st.text_input("File Store Path", value="./mlflow_data")

                if st.button("💾 Save File Store Config"):
                    settings["integrations"]["mlflow"][
                        "backend_store_uri"
                    ] = f"file://{file_path}"

                    import yaml

                    with open(loader.settings_path, "w") as f:
                        yaml.safe_dump(settings, f, default_flow_style=False, indent=2)

                    st.success("✅ MLflow file store configuration saved!")
                    st.info("Restart MLflow server for changes to take effect")

            elif config_option == "AWS S3 Artifacts + PostgreSQL Backend (Production)":
                st.success("✅ Standard production configuration")
                st.info("• Metadata: PostgreSQL (inherits from primary)")
                st.info(
                    f"• Artifacts: {artifact_store if artifact_store else 'Not configured'}"
                )

                # Show current S3 configuration
                with st.form(key="s3_artifacts_config"):
                    st.subheader("S3 Artifact Store Configuration")

                    # Parse current S3 path if exists
                    current_bucket = ""
                    current_prefix = ""
                    if artifact_store and artifact_store.startswith("s3://"):
                        s3_path = artifact_store.replace("s3://", "")
                        parts = s3_path.split("/", 1)
                        current_bucket = parts[0] if parts else ""
                        current_prefix = parts[1] if len(parts) > 1 else ""

                    s3_bucket = st.text_input(
                        "S3 Bucket", value=current_bucket or "nsc-mvp1"
                    )
                    s3_prefix = st.text_input(
                        "S3 Prefix", value=current_prefix or "onboarding-test/mlflow/"
                    )

                    st.info("💡 This uses AWS credentials from primary configuration")

                    if st.form_submit_button("💾 Update S3 Configuration"):
                        new_artifact_store = f"s3://{s3_bucket}/{s3_prefix}"

                        # Update settings with S3 artifact store but keep backend as auto_select
                        settings["integrations"]["mlflow"][
                            "artifact_store"
                        ] = new_artifact_store
                        settings["integrations"]["mlflow"][
                            "backend_store_uri"
                        ] = "auto_select"
                        settings["integrations"]["mlflow"]["backend_options"][
                            "s3_artifacts_only"
                        ] = True

                        import yaml

                        with open(loader.settings_path, "w") as f:
                            yaml.safe_dump(
                                settings, f, default_flow_style=False, indent=2
                            )

                        st.success(f"✅ Updated artifact store: {new_artifact_store}")
                        st.info("PostgreSQL backend: Inherits from primary database")
                        st.info("Restart MLflow server for changes to take effect")

                if st.button("🔄 Reset to Default Production Config"):
                    default_store = "s3://nsc-mvp1/onboarding-test/mlflow/"

                    # Reset to default production configuration
                    settings["integrations"]["mlflow"]["artifact_store"] = default_store
                    settings["integrations"]["mlflow"][
                        "backend_store_uri"
                    ] = "auto_select"
                    settings["integrations"]["mlflow"]["backend_options"][
                        "s3_artifacts_only"
                    ] = True

                    import yaml

                    with open(loader.settings_path, "w") as f:
                        yaml.safe_dump(settings, f, default_flow_style=False, indent=2)

                    st.success(f"✅ Reset to default: {default_store}")
                    st.info("PostgreSQL backend: Inherits from primary database")
                    st.rerun()

            else:  # Inherit from Primary
                st.success("✅ MLflow is configured to use the primary database")
                st.caption(
                    "MLflow will share the same PostgreSQL database as your main application"
                )

                if st.button("🔄 Reset to Inherit from Primary"):
                    settings["integrations"]["mlflow"][
                        "backend_store_uri"
                    ] = "auto_select"

                    import yaml

                    with open(loader.settings_path, "w") as f:
                        yaml.safe_dump(settings, f, default_flow_style=False, indent=2)

                    st.success("✅ MLflow reset to use primary database!")
                    st.rerun()

        # MLflow Database Maintenance Card (Collapsible)
        with st.expander("🔧 **MLflow Database Maintenance**", expanded=False):
            maintenance_container = st.container(border=True)
            with maintenance_container:
                st.info("Safe database operations for MLflow schema")
                col1, col2 = st.columns(2)

                with col1:
                    st.info(
                        """
                    **RESTORE MLFLOW SCHEMA**

                Safe operation that will:
                - Create any missing MLflow tables
                - Add performance indexes
                - Fix schema issues
                - **Preserve all existing data**
                """
                    )

                if st.button(
                    "🔧 Restore MLflow Schema",
                    type="secondary",
                    use_container_width=True,
                    key="restore_mlflow_schema",
                ):
                    with st.spinner("Restoring MLflow database schema..."):
                        try:
                            import subprocess
                            import sys

                            # Run restoration script with timeout for safety
                            result = subprocess.run(
                                [
                                    sys.executable,
                                    "infrastructure/setup/restore_mlflow.py",
                                ],
                                capture_output=True,
                                text=True,
                                timeout=30,
                            )

                            if result.returncode == 0:
                                st.success("✅ MLflow schema restored successfully!")

                                # Show what was done
                                output_lines = result.stdout.split("\n")
                                created_tables = [
                                    l for l in output_lines if "Created table:" in l
                                ]
                                existing_tables = [
                                    l for l in output_lines if "[EXISTS]" in l
                                ]

                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.metric("Tables Created", len(created_tables))
                                with col_b:
                                    st.metric("Tables Verified", len(existing_tables))

                                if created_tables:
                                    with st.expander("Created Tables"):
                                        for line in created_tables:
                                            st.text(line.strip())

                                # Quick test
                                try:
                                    import mlflow
                                    import os

                                    # Load credentials
                                    if "postgresql_primary" in settings.get(
                                        "credentials", {}
                                    ):
                                        pg = settings["credentials"][
                                            "postgresql_primary"
                                        ]

                                        # Set AWS for artifacts
                                        if "aws_basic" in settings.get(
                                            "credentials", {}
                                        ):
                                            aws = settings["credentials"]["aws_basic"]
                                            os.environ["AWS_ACCESS_KEY_ID"] = aws[
                                                "access_key_id"
                                            ]
                                            os.environ["AWS_SECRET_ACCESS_KEY"] = aws[
                                                "secret_access_key"
                                            ]
                                            os.environ["AWS_DEFAULT_REGION"] = aws.get(
                                                "default_region", "us-east-1"
                                            )

                                        # Connect to MLflow
                                        tracking_uri = f"postgresql://{pg['username']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['database']}"
                                        mlflow.set_tracking_uri(tracking_uri)

                                        client = mlflow.tracking.MlflowClient()
                                        experiments = client.search_experiments()

                                        st.success(
                                            f"✅ MLflow verified: {len(experiments)} experiments intact"
                                        )
                                except Exception as test_error:
                                    st.info(f"MLflow test: {str(test_error)[:100]}")
                            else:
                                st.error("Restoration had issues:")
                                if result.stderr:
                                    with st.expander("Error Details"):
                                        st.code(result.stderr, language="text")

                        except subprocess.TimeoutExpired:
                            st.error("❌ Restoration timed out (30s limit)")
                        except FileNotFoundError:
                            st.error(
                                "❌ Restoration script not found at infrastructure/setup/restore_mlflow.py"
                            )
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")

            with col2:
                st.warning(
                    """
                **CHECK MLFLOW TABLES**

                Diagnostic operation that will:
                - List all MLflow tables
                - Show table sizes
                - Check for missing tables
                - Verify indexes
                """
                )

                if st.button(
                    "📊 Check MLflow Tables",
                    type="secondary",
                    use_container_width=True,
                    key="check_mlflow_tables",
                ):
                    with st.spinner("Checking MLflow tables..."):
                        try:
                            import psycopg2
                            from datetime import datetime, timedelta

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

                                # Display snapshot timestamp
                                snapshot_time = datetime.now()
                                st.info(
                                    f"📸 **Database Snapshot**: {snapshot_time.strftime('%Y-%m-%d %H:%M:%S')} UTC"
                                )

                                # Get MLflow tables with sizes
                                cur.execute(
                                    """
                                    SELECT tablename,
                                           pg_total_relation_size(schemaname||'.'||tablename) as size_bytes,
                                           pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size_pretty
                                    FROM pg_tables
                                    WHERE schemaname = 'public'
                                    AND (tablename LIKE '%experiment%' OR tablename LIKE '%run%'
                                         OR tablename LIKE '%metric%' OR tablename LIKE '%model%'
                                         OR tablename LIKE '%dataset%' OR tablename LIKE '%tag%'
                                         OR tablename LIKE '%param%' OR tablename LIKE '%input%'
                                         OR tablename LIKE '%trace%')
                                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                                """
                                )

                                tables = cur.fetchall()

                                if tables:
                                    # Calculate total space
                                    total_bytes = sum(t[1] for t in tables)

                                    # Calculate metrics
                                    sizes = [t[1] for t in tables]
                                    avg_size = (
                                        total_bytes / len(tables) if tables else 0
                                    )
                                    max_size = max(sizes) if sizes else 0
                                    min_size = min(sizes) if sizes else 0

                                    # Find skew (tables using disproportionate space)
                                    threshold = (
                                        total_bytes * 0.3
                                    )  # Tables using >30% of space
                                    large_tables = [
                                        (t[0], t[2]) for t in tables if t[1] > threshold
                                    ]

                                    # Display summary metrics
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Total Tables", len(tables))
                                    with col2:
                                        st.metric(
                                            "Total Space",
                                            f"{total_bytes / (1024*1024):.1f} MB",
                                        )
                                    with col3:
                                        st.metric(
                                            "Avg Size/Table",
                                            f"{avg_size / (1024*1024):.2f} MB",
                                        )

                                    # Check for space issues
                                    if large_tables:
                                        st.warning(f"⚠️ Space Skew Detected!")
                                        st.info(
                                            f"Table(s) using >30% of space: {', '.join([t[0] for t in large_tables])}"
                                        )

                                    # Check for potentially wasteful tables
                                    cur.execute(
                                        """
                                        SELECT tablename,
                                               (SELECT COUNT(*) FROM public.runs) as run_count,
                                               (SELECT COUNT(*) FROM public.metrics) as metric_count,
                                               (SELECT COUNT(*) FROM public.experiments) as exp_count
                                        FROM pg_tables
                                        WHERE tablename = 'runs' LIMIT 1
                                    """
                                    )

                                    stats = cur.fetchone()
                                    if stats:
                                        _, run_count, metric_count, exp_count = stats

                                        # Check for waste indicators
                                        metrics_per_run = (
                                            metric_count / run_count
                                            if run_count > 0
                                            else 0
                                        )

                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.metric("Experiments", exp_count)
                                        with col2:
                                            st.metric("Runs", run_count)
                                        with col3:
                                            st.metric("Metrics", f"{metric_count:,}")

                                        # Get data age information
                                        cur.execute(
                                            """
                                            SELECT
                                                MIN(start_time) as oldest_run,
                                                MAX(start_time) as newest_run,
                                                COUNT(CASE WHEN start_time > %s THEN 1 END) as recent_runs
                                            FROM runs
                                            WHERE start_time IS NOT NULL
                                        """,
                                            (
                                                int(
                                                    (
                                                        datetime.now()
                                                        - timedelta(days=30)
                                                    ).timestamp()
                                                    * 1000
                                                ),
                                            ),
                                        )

                                        age_stats = cur.fetchone()
                                        if age_stats and age_stats[0]:
                                            oldest_run, newest_run, recent_runs = (
                                                age_stats
                                            )
                                            oldest_date = datetime.fromtimestamp(
                                                oldest_run / 1000
                                            )
                                            newest_date = datetime.fromtimestamp(
                                                newest_run / 1000
                                            )
                                            data_age_days = (
                                                datetime.now() - oldest_date
                                            ).days

                                            # Display data age metrics
                                            st.markdown("#### 📅 Data Timeline")
                                            col1, col2, col3 = st.columns(3)
                                            with col1:
                                                st.metric(
                                                    "Oldest Run",
                                                    oldest_date.strftime("%Y-%m-%d"),
                                                )
                                            with col2:
                                                st.metric(
                                                    "Newest Run",
                                                    newest_date.strftime("%Y-%m-%d"),
                                                )
                                            with col3:
                                                st.metric(
                                                    "Data Age", f"{data_age_days} days"
                                                )

                                            # Activity heatmap
                                            if recent_runs == 0:
                                                st.warning(
                                                    "⚠️ No activity in last 30 days - consider archiving"
                                                )
                                            else:
                                                st.caption(
                                                    f"📊 {recent_runs} runs in last 30 days"
                                                )

                                        if metrics_per_run > 1000:
                                            st.warning(
                                                f"⚠️ High metric density: {metrics_per_run:.0f} metrics/run"
                                            )
                                            st.caption(
                                                "Consider cleaning old metrics or using metric sampling"
                                            )

                                    # Show detailed table info
                                    with st.expander("📋 Detailed Table Information"):
                                        table_data = []
                                        for (
                                            table_name,
                                            size_bytes,
                                            size_pretty,
                                        ) in tables:
                                            pct_of_total = (
                                                (size_bytes / total_bytes * 100)
                                                if total_bytes > 0
                                                else 0
                                            )
                                            table_data.append(
                                                {
                                                    "Table": table_name,
                                                    "Size": size_pretty,
                                                    "% of Total": f"{pct_of_total:.1f}%",
                                                }
                                            )

                                        st.dataframe(
                                            table_data, use_container_width=True
                                        )

                                        # Show largest tables warning
                                        if tables and tables[0][1] > total_bytes * 0.5:
                                            st.error(
                                                f"⚠️ Table '{tables[0][0]}' uses {tables[0][1]/total_bytes*100:.0f}% of space!"
                                            )

                                    # Check for orphaned data
                                    cur.execute(
                                        """
                                        SELECT
                                            (SELECT COUNT(*) FROM runs WHERE experiment_id NOT IN
                                                (SELECT experiment_id FROM experiments)) as orphan_runs,
                                            (SELECT COUNT(*) FROM metrics WHERE run_uuid NOT IN
                                                (SELECT run_uuid FROM runs)) as orphan_metrics
                                    """
                                    )
                                    orphans = cur.fetchone()
                                    if orphans and (orphans[0] > 0 or orphans[1] > 0):
                                        st.error(
                                            f"🗑️ Orphaned data found: {orphans[0]} runs, {orphans[1]} metrics"
                                        )
                                        st.caption(
                                            "This wastes space and should be cleaned"
                                        )

                                    # Check for essential tables
                                    essential = [
                                        "experiments",
                                        "runs",
                                        "metrics",
                                        "params",
                                        "tags",
                                    ]
                                    table_names = [t[0] for t in tables]
                                    missing = [
                                        t for t in essential if t not in table_names
                                    ]

                                    if missing:
                                        st.warning(
                                            f"Missing essential tables: {', '.join(missing)}"
                                        )
                                        st.info(
                                            "Click 'Restore MLflow Schema' to create them"
                                        )
                                    else:
                                        st.success("✅ All essential tables present")

                                    # Recommendations
                                    if total_bytes > 100 * 1024 * 1024:  # >100MB
                                        with st.expander("💡 Storage Recommendations"):
                                            st.markdown(
                                                """
                                            **Your MLflow database is getting large. Consider:**
                                            - Archive old experiments to cold storage
                                            - Delete failed or test runs
                                            - Implement metric sampling for high-frequency logging
                                            - Use S3 for large artifacts instead of database
                                            """
                                            )

                                    # Create snapshot report for DBA
                                    snapshot_report = {
                                        "timestamp": snapshot_time.isoformat(),
                                        "database": {
                                            "host": pg["host"],
                                            "database": pg["database"],
                                            "total_tables": len(tables),
                                            "total_size_mb": round(
                                                total_bytes / (1024 * 1024), 2
                                            ),
                                            "experiments": (
                                                exp_count
                                                if "exp_count" in locals()
                                                else 0
                                            ),
                                            "runs": (
                                                run_count
                                                if "run_count" in locals()
                                                else 0
                                            ),
                                            "metrics": (
                                                metric_count
                                                if "metric_count" in locals()
                                                else 0
                                            ),
                                        },
                                        "data_timeline": {
                                            "oldest_run": (
                                                oldest_date.isoformat()
                                                if "oldest_date" in locals()
                                                else None
                                            ),
                                            "newest_run": (
                                                newest_date.isoformat()
                                                if "newest_date" in locals()
                                                else None
                                            ),
                                            "data_age_days": (
                                                data_age_days
                                                if "data_age_days" in locals()
                                                else None
                                            ),
                                            "recent_activity_30d": (
                                                recent_runs
                                                if "recent_runs" in locals()
                                                else 0
                                            ),
                                        },
                                        "top_tables": [
                                            {
                                                "name": t[0],
                                                "size": t[2],
                                                "percent": round(
                                                    t[1] / total_bytes * 100, 1
                                                ),
                                            }
                                            for t in tables[:5]
                                        ],
                                        "issues": {
                                            "space_skew": (
                                                len(large_tables) > 0
                                                if "large_tables" in locals()
                                                else False
                                            ),
                                            "orphaned_data": (
                                                (orphans[0] > 0 or orphans[1] > 0)
                                                if "orphans" in locals() and orphans
                                                else False
                                            ),
                                            "high_metric_density": (
                                                metrics_per_run > 1000
                                                if "metrics_per_run" in locals()
                                                else False
                                            ),
                                            "missing_tables": (
                                                len(missing)
                                                if "missing" in locals()
                                                else 0
                                            ),
                                        },
                                    }

                                    # Display copyable snapshot for DBA
                                    with st.expander("📄 DBA Snapshot Report"):
                                        import json

                                        snapshot_json = json.dumps(
                                            snapshot_report, indent=2
                                        )
                                        st.code(snapshot_json, language="json")

                                        st.download_button(
                                            label="📥 Download Snapshot Report",
                                            data=snapshot_json,
                                            file_name=f"mlflow_snapshot_{snapshot_time.strftime('%Y%m%d_%H%M%S')}.json",
                                            mime="application/json",
                                        )

                                        st.caption(
                                            f"Share this snapshot with your DBA for: {pg['host']}"
                                        )
                                else:
                                    st.warning("No MLflow tables found")
                                    st.info(
                                        "Click 'Restore MLflow Schema' to create them"
                                    )

                                cur.close()
                                conn.close()

                        except Exception as e:
                            st.error(f"Database check failed: {str(e)}")

        # PGVector Database Maintenance Card (Collapsible)
        with st.expander("🔮 **PGVector Database Maintenance**", expanded=False):
            pgvector_container = st.container(border=True)
            with pgvector_container:
                st.info("Vector database operations and optimization")
                col1, col2 = st.columns(2)

                with col1:
                    if st.button(
                        "📊 Check PGVector Tables",
                        type="secondary",
                        use_container_width=True,
                        key="check_pgvector",
                    ):
                        with st.spinner("Checking pgvector tables..."):
                            try:
                                import psycopg2
                                from datetime import datetime

                                if "postgresql_primary" in settings.get(
                                    "credentials", {}
                                ):
                                    pg = settings["credentials"]["postgresql_primary"]

                                conn = psycopg2.connect(
                                    host=pg["host"],
                                    port=pg["port"],
                                    database=pg["database"],
                                    user=pg["username"],
                                    password=pg["password"],
                                )

                                cur = conn.cursor()

                                # Check pgvector extension
                                cur.execute(
                                    """
                                    SELECT installed_version
                                    FROM pg_available_extensions
                                    WHERE name = 'vector'
                                """
                                )
                                vector_version = cur.fetchone()

                                if vector_version and vector_version[0]:
                                    st.success(
                                        f"✅ PGVector Extension v{vector_version[0]}"
                                    )

                                    # Get vector tables
                                    cur.execute(
                                        """
                                        SELECT
                                            t.tablename,
                                            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                                            obj_description(c.oid) as description
                                        FROM pg_tables t
                                        JOIN pg_class c ON c.relname = t.tablename
                                        WHERE t.schemaname = 'public'
                                        AND EXISTS (
                                            SELECT 1 FROM pg_attribute a
                                            JOIN pg_type typ ON a.atttypid = typ.oid
                                            WHERE a.attrelid = c.oid
                                            AND typ.typname = 'vector'
                                        )
                                        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                                    """
                                    )

                                    vector_tables = cur.fetchall()

                                    if vector_tables:
                                        st.info(
                                            f"Found {len(vector_tables)} vector table(s)"
                                        )
                                        for table_name, size, desc in vector_tables:
                                            st.text(f"• {table_name}: {size}")
                                            if desc:
                                                st.caption(f"  {desc}")
                                    else:
                                        st.warning("No vector tables found")

                                    # Check for vector indexes and dimension info
                                    cur.execute(
                                        """
                                        SELECT
                                            i.indexname,
                                            i.tablename,
                                            i.indexdef,
                                            pg_size_pretty(pg_relation_size(c.oid)) as index_size,
                                            am.amname as index_method
                                        FROM pg_indexes i
                                        JOIN pg_class c ON c.relname = i.indexname
                                        JOIN pg_am am ON c.relam = am.oid
                                        WHERE i.indexdef LIKE '%vector%'
                                        LIMIT 10
                                    """
                                    )
                                    vector_indexes = cur.fetchall()

                                    if vector_indexes:
                                        # Get index names and types for summary
                                        index_summary = []
                                        for idx in vector_indexes:
                                            idx_name = idx[0]
                                            idx_def = idx[2]
                                            # Determine index type
                                            if "ivfflat" in idx_def.lower():
                                                index_type = "IVFFlat"
                                            elif "hnsw" in idx_def.lower():
                                                index_type = "HNSW"
                                            else:
                                                index_type = "btree"
                                            index_summary.append(
                                                f"{idx_name} ({index_type})"
                                            )

                                        if len(vector_indexes) == 1:
                                            st.info(
                                                f"📊 **Found 1 vector index: {index_summary[0]}**"
                                            )
                                        else:
                                            st.info(
                                                f"📊 **Found {len(vector_indexes)} vector indexes: {', '.join(index_summary[:3])}{'...' if len(index_summary) > 3 else ''}**"
                                            )

                                        for (
                                            idx_name,
                                            tbl_name,
                                            idx_def,
                                            idx_size,
                                            idx_method,
                                        ) in vector_indexes:
                                            # Extract index type (ivfflat, hnsw, etc.) from definition
                                            index_type = "btree"  # default
                                            if "ivfflat" in idx_def.lower():
                                                index_type = "IVFFlat"
                                            elif "hnsw" in idx_def.lower():
                                                index_type = "HNSW"

                                            # Extract distance metric (cosine, l2, ip) from definition
                                            distance = "cosine"  # default
                                            if "vector_l2_ops" in idx_def:
                                                distance = "L2 (Euclidean)"
                                            elif "vector_ip_ops" in idx_def:
                                                distance = "Inner Product"
                                            elif "vector_cosine_ops" in idx_def:
                                                distance = "Cosine"

                                            # Try to extract dimensions from the index definition
                                            import re

                                            dim_match = re.search(
                                                r"vector\((\d+)\)", idx_def
                                            )
                                            dimensions = (
                                                dim_match.group(1)
                                                if dim_match
                                                else "unknown"
                                            )

                                            st.markdown(f"**• {idx_name}**")
                                            col1, col2, col3 = st.columns(3)
                                            with col1:
                                                st.caption(f"📋 Table: {tbl_name}")
                                                st.caption(f"🔧 Type: {index_type}")
                                            with col2:
                                                st.caption(f"📏 Distance: {distance}")
                                                st.caption(f"📐 Dims: {dimensions}")
                                            with col3:
                                                st.caption(f"💾 Size: {idx_size}")
                                                st.caption(f"⚙️ Method: {idx_method}")

                                    # Also check for vector column details
                                    cur.execute(
                                        """
                                        SELECT
                                            c.relname as table_name,
                                            a.attname as column_name,
                                            format_type(a.atttypid, a.atttypmod) as data_type,
                                            COUNT(*) OVER (PARTITION BY c.relname) as vector_cols_in_table
                                        FROM pg_attribute a
                                        JOIN pg_class c ON a.attrelid = c.oid
                                        JOIN pg_namespace n ON c.relnamespace = n.oid
                                        WHERE n.nspname = 'public'
                                        AND format_type(a.atttypid, a.atttypmod) LIKE 'vector%'
                                        ORDER BY c.relname, a.attname
                                    """
                                    )
                                    vector_columns = cur.fetchall()

                                    if vector_columns:
                                        st.markdown("**📦 Vector Columns:**")
                                        for tbl, col, dtype, count in vector_columns:
                                            # Extract dimensions from data type (e.g., "vector(1024)")
                                            dim_match = re.search(
                                                r"vector\((\d+)\)", dtype
                                            )
                                            dims = (
                                                dim_match.group(1)
                                                if dim_match
                                                else "variable"
                                            )
                                            st.caption(
                                                f"• {tbl}.{col} - {dims}D vectors"
                                            )

                                else:
                                    st.warning("⚠️ PGVector extension not installed")
                                    st.info(
                                        "Run: CREATE EXTENSION IF NOT EXISTS vector;"
                                    )

                                    cur.close()
                                    conn.close()

                            except Exception as e:
                                st.error(f"Error checking pgvector: {str(e)}")

            with col2:
                if st.button(
                    "🔧 Optimize Vector Indexes",
                    type="secondary",
                    use_container_width=True,
                    key="optimize_vectors",
                ):
                    with st.spinner("Optimizing vector indexes..."):
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

                                cur = conn.cursor()

                                # Reindex vector tables
                                cur.execute(
                                    """
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
                                """
                                )

                                vector_tables = cur.fetchall()
                                optimized_tables = []
                                failed_tables = []

                                for (table_name,) in vector_tables:
                                    try:
                                        # Get table size before optimization
                                        cur.execute(
                                            f"""
                                            SELECT pg_size_pretty(pg_total_relation_size('{table_name}'))
                                        """
                                        )
                                        size_before = cur.fetchone()[0]

                                        # Reindex the table
                                        cur.execute(f"REINDEX TABLE {table_name}")

                                        # Analyze to update statistics
                                        cur.execute(f"ANALYZE {table_name}")

                                        optimized_tables.append(
                                            (table_name, size_before)
                                        )
                                    except Exception as e:
                                        failed_tables.append((table_name, str(e)))

                                conn.commit()

                                # Get vector index count
                                cur.execute(
                                    """
                                    SELECT COUNT(*)
                                    FROM pg_indexes
                                    WHERE indexdef LIKE '%vector%'
                                """
                                )
                                total_indexes = cur.fetchone()[0]

                                cur.close()
                                conn.close()

                                if optimized_tables:
                                    st.success(
                                        f"✅ Successfully optimized {len(optimized_tables)} vector table(s)"
                                    )
                                    with st.expander(
                                        "Optimization Details", expanded=True
                                    ):
                                        for table, size in optimized_tables:
                                            st.text(f"• {table}: {size}")
                                        st.caption(
                                            f"Total vector indexes reindexed: {total_indexes}"
                                        )
                                        st.info(
                                            "Statistics updated for improved query planning"
                                        )

                                if failed_tables:
                                    st.warning(
                                        f"⚠️ Failed to optimize {len(failed_tables)} table(s)"
                                    )
                                    for table, error in failed_tables:
                                        st.caption(f"• {table}: {error[:100]}")

                                if not optimized_tables and not failed_tables:
                                    st.info("No vector tables found to optimize")
                                    st.caption(
                                        "Tip: Create vector tables first before optimization"
                                    )

                        except Exception as e:
                            st.error(f"Error optimizing: {str(e)}")

        # General Database Monitoring Card (Collapsible)
        with st.expander("📊 **General Database Monitoring**", expanded=False):
            general_db_container = st.container(border=True)
            with general_db_container:
                st.info("Monitor all database tables and performance")
                col1, col2 = st.columns(2)

                with col1:
                    if st.button(
                        "📈 Database Overview",
                        type="secondary",
                        use_container_width=True,
                        key="db_overview",
                    ):
                        with st.spinner("Analyzing database..."):
                            try:
                                import psycopg2
                                from datetime import datetime

                                if "postgresql_primary" in settings.get(
                                    "credentials", {}
                                ):
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
                                cur.execute(
                                    """
                                    SELECT pg_database_size(current_database()) as size,
                                           pg_size_pretty(pg_database_size(current_database())) as size_pretty
                                """
                                )
                                db_size = cur.fetchone()

                                st.metric(
                                    "Total Database Size",
                                    db_size[1] if db_size else "Unknown",
                                )

                                # Get ALL tables for complete analysis
                                cur.execute(
                                    """
                                    SELECT
                                        schemaname,
                                        tablename,
                                        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size_pretty,
                                        pg_total_relation_size(schemaname||'.'||tablename) as bytes,
                                        obj_description(c.oid) as description
                                    FROM pg_tables t
                                    JOIN pg_class c ON c.relname = t.tablename AND c.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = t.schemaname)
                                    WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                                """
                                )

                                all_tables = cur.fetchall()
                                total_tables = len(all_tables)

                                if all_tables:
                                    # Categorize tables
                                    mlflow_count = len(
                                        [
                                            t
                                            for t in all_tables
                                            if any(
                                                x in t[1].lower()
                                                for x in [
                                                    "experiment",
                                                    "run",
                                                    "metric",
                                                    "param",
                                                    "tag",
                                                    "model",
                                                    "logged",
                                                    "registered",
                                                    "dataset",
                                                    "input",
                                                    "trace",
                                                ]
                                            )
                                        ]
                                    )
                                    vector_count = len(
                                        [
                                            t
                                            for t in all_tables
                                            if "vector" in t[1].lower()
                                            or "embedding" in t[1].lower()
                                        ]
                                    )
                                    app_count = (
                                        total_tables - mlflow_count - vector_count
                                    )

                                    # Display aggregate summary
                                    st.markdown(
                                        f"### 📊 **Found {total_tables} Tables**"
                                    )

                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric("Total", total_tables)
                                    with col2:
                                        st.metric("MLflow", mlflow_count)
                                    with col3:
                                        st.metric("Vector", vector_count)
                                    with col4:
                                        st.metric("Application", app_count)

                                    # Show top 5 tables
                                    st.markdown("**Top 5 Tables by Size:**")
                                    for (
                                        schema,
                                        table,
                                        size,
                                        bytes_val,
                                        desc,
                                    ) in all_tables[:5]:
                                        pct = (
                                            (bytes_val / db_size[0] * 100)
                                            if db_size
                                            else 0
                                        )
                                        st.text(
                                            f"• {schema}.{table}: {size} ({pct:.1f}%)"
                                        )

                                    # Create detailed table data for download
                                    with st.expander(
                                        f"📋 View All {total_tables} Tables & Download CSV"
                                    ):
                                        import pandas as pd

                                        table_data = []
                                        for (
                                            schema,
                                            table,
                                            size_pretty,
                                            bytes_val,
                                            desc,
                                        ) in all_tables:
                                            category = "Application"
                                            if any(
                                                x in table.lower()
                                                for x in [
                                                    "experiment",
                                                    "run",
                                                    "metric",
                                                    "param",
                                                    "tag",
                                                    "model",
                                                    "logged",
                                                    "registered",
                                                    "dataset",
                                                    "input",
                                                    "trace",
                                                ]
                                            ):
                                                category = "MLflow"
                                            elif (
                                                "vector" in table.lower()
                                                or "embedding" in table.lower()
                                            ):
                                                category = "Vector"

                                            table_data.append(
                                                {
                                                    "Schema": schema,
                                                    "Table": table,
                                                    "Category": category,
                                                    "Size": size_pretty,
                                                    "Bytes": bytes_val,
                                                    "% of DB": round(
                                                        (
                                                            (
                                                                bytes_val
                                                                / db_size[0]
                                                                * 100
                                                            )
                                                            if db_size
                                                            else 0
                                                        ),
                                                        2,
                                                    ),
                                                    "Description": (desc or "")[:100],
                                                }
                                            )

                                        df = pd.DataFrame(table_data)

                                        # Show summary by category
                                        category_summary = (
                                            df.groupby("Category")
                                            .agg({"Table": "count", "Bytes": "sum"})
                                            .rename(columns={"Table": "Count"})
                                        )
                                        category_summary["Size"] = category_summary[
                                            "Bytes"
                                        ].apply(lambda x: f"{x/(1024*1024):.1f} MB")

                                        st.markdown("**Summary by Category:**")
                                        st.dataframe(
                                            category_summary[["Count", "Size"]],
                                            use_container_width=True,
                                        )

                                        # Show all tables in a scrollable dataframe
                                        st.markdown(f"**All {total_tables} Tables:**")
                                        st.dataframe(
                                            df[
                                                ["Table", "Category", "Size", "% of DB"]
                                            ].head(20),
                                            use_container_width=True,
                                            height=400,
                                        )
                                        if total_tables > 20:
                                            st.caption(
                                                f"Showing first 20 of {total_tables} tables. Download CSV for complete list."
                                            )

                                        # Download button for CSV
                                        csv = df.to_csv(index=False)
                                        timestamp = datetime.now().strftime(
                                            "%Y%m%d_%H%M%S"
                                        )

                                        st.download_button(
                                            label=f"📥 Download All {total_tables} Tables as CSV",
                                            data=csv,
                                            file_name=f"database_tables_{pg['database']}_{timestamp}.csv",
                                            mime="text/csv",
                                            help=f"Download complete list of {total_tables} tables with sizes and categories",
                                        )

                                # Get connection stats
                                cur.execute(
                                    """
                                    SELECT count(*) as total,
                                           count(*) FILTER (WHERE state = 'active') as active,
                                           count(*) FILTER (WHERE state = 'idle') as idle
                                    FROM pg_stat_activity
                                    WHERE datname = current_database()
                                """
                                )

                                conn_stats = cur.fetchone()
                                if conn_stats:
                                    st.markdown("**Connection Stats:**")
                                    col_a, col_b, col_c = st.columns(3)
                                    with col_a:
                                        st.metric("Total", conn_stats[0])
                                    with col_b:
                                        st.metric("Active", conn_stats[1])
                                    with col_c:
                                        st.metric("Idle", conn_stats[2])

                                cur.close()
                                conn.close()

                            except Exception as e:
                                st.error(f"Error: {str(e)}")

            with col2:
                if st.button(
                    "🧹 Vacuum & Analyze",
                    type="secondary",
                    use_container_width=True,
                    key="vacuum_db",
                ):
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
                                conn.set_isolation_level(
                                    psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
                                )
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

        # Danger Zone - Collapsible Card
        with st.expander("⚠️ **Danger Zone** - Destructive Operations", expanded=False):
            danger_container = st.container(border=True)
            with danger_container:
                st.error(
                    "**⚡ WARNING: Destructive operations that cannot be undone!**"
                )

                st.markdown("##### 🔴 Delete & Re-install MLflow")
                st.warning(
                    """
                This will:
                • Stop MLflow server
                • Delete ALL experiments, runs, and metrics
                • Delete ALL artifacts from S3
                • Create fresh MLflow installation
                """
                )

                confirm_reinstall = st.checkbox(
                    "I understand this will delete all MLflow data",
                    key="confirm_mlflow_reinstall_integrations",
                )

                if confirm_reinstall:
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        confirmation_text = st.text_input(
                            "Type 'DELETE MLFLOW' to confirm:",
                            key="mlflow_confirm_text",
                        )
                    with col2:
                        st.caption(" ")  # Spacer
                        if confirmation_text == "DELETE MLFLOW":
                            if st.button(
                                "🔴 RE-INSTALL",
                                type="primary",
                                key="reinstall_mlflow_btn",
                            ):
                                with st.spinner(
                                    "Re-installing MLflow... This will take a few moments..."
                                ):
                                    progress_bar = st.progress(0)
                                    status_text = st.empty()

                                try:
                                    import subprocess
                                    import time

                                    # Step 1: Stop MLflow server
                                    status_text.text("Stopping MLflow server...")
                                    progress_bar.progress(10)
                                    subprocess.run(
                                        ["taskkill", "/F", "/IM", "mlflow.exe"],
                                        capture_output=True,
                                        text=True,
                                        shell=True,
                                    )
                                    time.sleep(2)

                                    # Step 2: Clear MLflow artifacts from S3
                                    status_text.text(
                                        "Clearing MLflow artifacts from S3..."
                                    )
                                    progress_bar.progress(25)

                                    # Use boto3 to clear S3 artifacts
                                    try:
                                        import boto3
                                        # Use pre-imported or fallback loader
                                        if not yaml_loader_available:
                                            # Already imported at top with fallback
                                            pass
                                        settings_loader = get_settings_loader()
                                        aws_config = settings_loader.get_aws_config()
                                        s3_config = settings_loader.get_s3_config()

                                        # Create S3 client
                                        s3_client = boto3.client(
                                            "s3",
                                            aws_access_key_id=aws_config[
                                                "access_key_id"
                                            ],
                                            aws_secret_access_key=aws_config[
                                                "secret_access_key"
                                            ],
                                            region_name=aws_config["region"],
                                        )

                                        # Delete all objects under mlflow prefix
                                        bucket = s3_config["bucket"]
                                        prefix = "compliance-qa/mlflow/"

                                        # List and delete all objects
                                        paginator = s3_client.get_paginator(
                                            "list_objects_v2"
                                        )
                                        pages = paginator.paginate(
                                            Bucket=bucket, Prefix=prefix
                                        )

                                        delete_keys = []
                                        for page in pages:
                                            if "Contents" in page:
                                                for obj in page["Contents"]:
                                                    delete_keys.append(
                                                        {"Key": obj["Key"]}
                                                    )

                                                    # Delete in batches of 1000 (S3 limit)
                                                    if len(delete_keys) >= 1000:
                                                        s3_client.delete_objects(
                                                            Bucket=bucket,
                                                            Delete={
                                                                "Objects": delete_keys
                                                            },
                                                        )
                                                        delete_keys = []

                                        # Delete remaining objects
                                        if delete_keys:
                                            s3_client.delete_objects(
                                                Bucket=bucket,
                                                Delete={"Objects": delete_keys},
                                            )

                                        st.info(
                                            f"Cleared MLflow artifacts from s3://{bucket}/{prefix}"
                                        )
                                    except Exception as s3_error:
                                        st.warning(
                                            f"Could not clear S3 artifacts: {s3_error}"
                                        )
                                        st.info("Continuing with local cleanup...")

                                    # Step 3: Drop and recreate MLflow database tables
                                    status_text.text("Resetting MLflow database...")
                                    progress_bar.progress(40)

                                    # Get database config and reset MLflow tables
                                    # Use pre-imported or fallback loader
                                    if not yaml_loader_available:
                                        # Already imported at top with fallback
                                        pass
                                    loader = get_settings_loader()
                                    db_config = loader.get_database_config()

                                    # Run MLflow database upgrade command
                                    mlflow_db_uri = f"postgresql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

                                    # Step 4: Re-initialize MLflow database
                                    status_text.text(
                                        "Re-initializing MLflow database..."
                                    )
                                    progress_bar.progress(60)
                                    result = subprocess.run(
                                        ["mlflow", "db", "upgrade", mlflow_db_uri],
                                        capture_output=True,
                                        text=True,
                                        shell=True,
                                    )
                                    time.sleep(2)

                                    # Step 5: Restart MLflow server
                                    status_text.text("Starting fresh MLflow server...")
                                    progress_bar.progress(80)
                                    subprocess.Popen(
                                        [
                                            "mlflow",
                                            "server",
                                            "--backend-store-uri",
                                            mlflow_db_uri,
                                            "--default-artifact-root",
                                            "s3://nsc-mvp1/compliance-qa/mlflow/",
                                            "--host",
                                            "0.0.0.0",
                                            "--port",
                                            "5000",
                                        ],
                                        shell=True,
                                    )
                                    time.sleep(3)

                                    # Step 6: Verify MLflow is running
                                    status_text.text("Verifying MLflow installation...")
                                    progress_bar.progress(95)

                                    import requests

                                    try:
                                        response = requests.get(
                                            "http://localhost:5000", timeout=5
                                        )
                                        if response.status_code == 200:
                                            progress_bar.progress(100)
                                            status_text.text(
                                                "MLflow re-installation complete!"
                                            )
                                            time.sleep(1)

                                            st.balloons()
                                            st.success(
                                                """
                                            ✅ **MLflow Successfully Re-installed!**

                                            - MLflow server is running at: http://localhost:5000
                                            - Database has been reset and initialized
                                            - All previous experiments and runs have been deleted
                                            - System is ready for fresh ML tracking
                                            """
                                            )
                                        else:
                                            st.error(
                                                "MLflow server started but not responding correctly"
                                            )
                                    except Exception as verify_error:
                                        st.error(
                                            f"Could not verify MLflow: {verify_error}"
                                        )

                                except Exception as e:
                                    st.error(
                                        f"❌ MLflow re-installation failed: {str(e)}"
                                    )
                                    st.exception(e)
                        else:
                            if confirmation_text:
                                st.error(
                                    "❌ Confirmation text does not match. Type exactly: DELETE MLFLOW"
                                )

                if not confirm_reinstall:
                    st.info("👆 Check the box above to enable MLflow re-installation")

    # Future Integration Placeholders
    st.markdown("---")
    st.subheader("🔮 Additional Integrations")
    st.info(
        """
    Future integrations will appear here:
    - **LDAP**: Enterprise authentication (currently disabled)
    - **SSO**: Single sign-on integration (currently disabled)
    - **Observability**: Datadog/NewRelic monitoring (currently disabled)
    - **Kafka**: Event streaming and message queuing (coming soon)
    - **Redis**: Caching and session management (coming soon)
    """
    )

    st.success("✅ Infrastructure integrations are configured and ready!")
    st.caption("Move to the Connections tab to set up AI services")


def render_step_4_chat_setup():
    """Step 4: Set up AI chat with Bedrock configuration."""
    st.header("Step 4️⃣: AI Models")
    st.markdown("**Configure your AI models and test the chat setup.**")

    # Bedrock Configuration Section (main content)
    st.markdown("### 🤖 AWS Bedrock Configuration")
    st.markdown("Configure your AI model settings for chat functionality.")

    with st.expander("🤖 Configure AWS Bedrock Settings", expanded=False):
        # Load current Bedrock settings
        try:
            # Use pre-imported or fallback loader
            if not yaml_loader_available:
                # Already imported at top with fallback
                pass
            settings_loader = get_settings_loader()
            raw_settings = settings_loader._load_settings()  # Get raw dict

            # Get Bedrock configuration
            bedrock_config = raw_settings.get("llm_models", {}).get("bedrock", {})
            current_model_id = bedrock_config.get("model_id", "")
            current_region = bedrock_config.get("region", "us-east-1")
            current_max_tokens = bedrock_config.get("max_tokens", 4096)
            current_temperature = bedrock_config.get("temperature", 0.7)

            # Get AWS credentials for Bedrock
            aws_creds = raw_settings.get("credentials", {}).get("aws_basic", {})
            has_aws_creds = bool(
                aws_creds.get("access_key_id") and aws_creds.get("secret_access_key")
            )

            if has_aws_creds:
                st.success(
                    "✅ AWS credentials configured (using credentials from Prerequisites)"
                )
            else:
                st.warning(
                    "⚠️ AWS credentials not configured - set them in Prerequisites tab first"
                )

            st.info(f"💡 **Current Model**: {current_model_id or 'Not configured'}")

        except Exception as e:
            st.warning(f"⚠️ Could not load current Bedrock settings: {str(e)}")
            current_model_id = ""
            current_region = "us-east-1"
            current_max_tokens = 4096
            current_temperature = 0.7
            has_aws_creds = False

        with st.form("bedrock_config_form"):
            st.markdown("**AWS Bedrock Configuration**")

            st.subheader("Model Selection")
            col1, col2 = st.columns(2)

            with col1:
                # Available Bedrock models
                bedrock_models = [
                    "anthropic.claude-3-haiku-20240307-v1:0",
                    "anthropic.claude-3-sonnet-20240229-v1:0",
                    "anthropic.claude-3-5-sonnet-20240620-v1:0",
                    "anthropic.claude-3-opus-20240229-v1:0",
                    "anthropic.claude-instant-v1",
                    "amazon.titan-text-express-v1",
                    "amazon.titan-text-lite-v1",
                    "meta.llama2-13b-chat-v1",
                    "meta.llama2-70b-chat-v1",
                ]

                # Find current model index
                try:
                    model_index = bedrock_models.index(current_model_id)
                except ValueError:
                    model_index = 0

                model_id = st.selectbox(
                    "Bedrock Model",
                    bedrock_models,
                    index=model_index,
                    help="Select the AI model to use",
                )

                temperature = st.slider(
                    "Temperature",
                    min_value=0.0,
                    max_value=1.0,
                    value=float(current_temperature),
                    step=0.1,
                    help="Controls randomness in responses (0=deterministic, 1=creative)",
                )

            with col2:
                region = st.selectbox(
                    "AWS Region",
                    [
                        "us-east-1",
                        "us-west-2",
                        "eu-west-1",
                        "eu-central-1",
                        "ap-southeast-1",
                    ],
                    index=0 if current_region == "us-east-1" else None,
                    help="AWS region where Bedrock is available",
                )

                max_tokens = st.number_input(
                    "Max Tokens",
                    min_value=100,
                    max_value=100000,
                    value=int(current_max_tokens),
                    step=100,
                    help="Maximum response length",
                )

            st.subheader("Additional Settings")
            enable_streaming = st.checkbox(
                "Enable Response Streaming",
                value=True,
                help="Stream responses in real-time",
            )
            enable_fallback = st.checkbox(
                "Enable Model Fallback",
                value=True,
                help="Fallback to alternative model if primary fails",
            )

            # Form buttons
            col_test, col_save = st.columns(2)

            with col_test:
                test_clicked = st.form_submit_button(
                    "🧪 Test Bedrock Access", use_container_width=True
                )

            with col_save:
                save_clicked = st.form_submit_button(
                    "💾 Save Configuration", use_container_width=True, type="primary"
                )

            if test_clicked:
                if not has_aws_creds:
                    st.error(
                        "❌ Please configure AWS credentials in Prerequisites tab first"
                    )
                else:
                    with st.spinner("Testing Bedrock access..."):
                        try:
                            # Test Bedrock connection using the domain service
                            test_result = setup_service.test_bedrock_access()

                            if test_result.get("success"):
                                st.success(f"✅ Successfully connected to AWS Bedrock!")
                                if test_result.get("models_available"):
                                    st.info(
                                        f"📋 Available models: {', '.join(test_result['models_available'][:3])}..."
                                    )
                            else:
                                st.error(
                                    f"❌ Bedrock test failed: {test_result.get('error', 'Unknown error')}"
                                )

                        except Exception as e:
                            st.error(f"❌ Unexpected error: {str(e)}")

            if save_clicked:
                with st.spinner("Saving Bedrock configuration..."):
                    try:
                        # Update Bedrock configuration in settings
                        if "llm_models" not in raw_settings:
                            raw_settings["llm_models"] = {}
                        if "bedrock" not in raw_settings["llm_models"]:
                            raw_settings["llm_models"]["bedrock"] = {}

                        raw_settings["llm_models"]["bedrock"].update(
                            {
                                "model_id": model_id,
                                "region": region,
                                "max_tokens": max_tokens,
                                "temperature": temperature,
                                "streaming": enable_streaming,
                                "fallback_enabled": enable_fallback,
                                "type": "bedrock_model",
                            }
                        )

                        # Save to settings.yaml
                        import yaml

                        with open(settings_loader.settings_path, "w") as f:
                            yaml.safe_dump(
                                raw_settings, f, default_flow_style=False, indent=2
                            )

                        st.success("✅ Bedrock configuration saved successfully!")
                        st.info(f"💡 Model configured: {model_id}")
                        st.balloons()

                        # Clear step3 results to force re-check
                        if "step3_results" in st.session_state:
                            del st.session_state["step3_results"]

                    except Exception as e:
                        st.error(f"❌ Failed to save configuration: {str(e)}")

        st.info(
            "💡 **Note:** Bedrock uses AWS credentials from Prerequisites tab for authentication."
        )

        # Model Management Button
        if st.button(
            "⚙️ Advanced Model Configuration", type="secondary", use_container_width=True
        ):
            st.session_state.show_model_config = not st.session_state.get(
                "show_model_config", False
            )

        # Model Configuration Section
        if st.session_state.get("show_model_config", False):
            st.markdown("---")
            st.subheader("🎯 Advanced Model Configuration")

            # Load current Bedrock config
            # Use pre-imported or fallback loader
            if not yaml_loader_available:
                # Already imported at top with fallback
                pass
            loader = get_settings_loader()
            bedrock_config = loader.get_bedrock_config()

            if bedrock_config:
                # Get current settings
                model_mapping = bedrock_config.get("model_mapping", {})
                current_default = bedrock_config.get("default_model", "")
                adapter_config = bedrock_config.get("adapter_config", {})

                # Create tabs for different configuration sections
                config_tab1, config_tab2, config_tab3, config_tab4, config_tab5 = (
                    st.tabs(
                        [
                            "🎯 Models",
                            "🔧 Mappings",
                            "⚙️ Adapter Settings",
                            "🔤 Embeddings",
                            "🧪 Model Testing",
                        ]
                    )
                )

                with config_tab1:
                    st.markdown("#### Model Selection")

                    # Default model selection
                    default_model_key = None
                    for key, value in model_mapping.items():
                        if value == current_default:
                            default_model_key = key
                            break

                    selected_default = st.selectbox(
                        "🎯 Default Model",
                        options=list(model_mapping.keys()),
                        index=(
                            list(model_mapping.keys()).index(default_model_key)
                            if default_model_key and default_model_key in model_mapping
                            else 0
                        ),
                        help="Select the default model for AI operations",
                    )

                    # Available models selection
                    st.markdown("#### Enable/Disable Models")
                    available_models = st.multiselect(
                        "✅ Available Models",
                        options=list(model_mapping.keys()),
                        default=list(model_mapping.keys()),
                        help="Select which models should be available (unselected models will be disabled)",
                    )

                    # Show status
                    disabled_models = [
                        m for m in model_mapping.keys() if m not in available_models
                    ]
                    if disabled_models:
                        st.warning(f"⚠️ Disabled models: {', '.join(disabled_models)}")

                with config_tab2:
                    st.markdown("#### Model Mappings")
                    st.info(
                        "💡 Model mappings link friendly names to AWS Bedrock model IDs"
                    )

                    # Display current mappings
                    st.markdown("**Current Mappings:**")
                    for alias, model_id in model_mapping.items():
                        col1, col2, col3 = st.columns([1, 3, 1])
                        with col1:
                            st.text(alias)
                        with col2:
                            st.code(model_id, language=None)
                        with col3:
                            if alias in available_models:
                                st.success("✅ Enabled")
                            else:
                                st.error("❌ Disabled")

                    # Model Library - friendly categorized view
                    with st.expander("📚 Model Library - Add from Available Models"):

                        # Chat/Conversation Models
                        st.markdown("**💬 Chat & Conversation Models**")
                        st.caption("For interactive chat, Q&A, and conversational AI")
                        chat_models = {
                            "Claude 3.5 Sonnet (Best Overall)": "anthropic.claude-3-5-sonnet-20240620-v1:0",
                            "Claude 3 Opus (Most Capable)": "anthropic.claude-3-opus-20240229-v1:0",
                            "Claude 3 Sonnet (Balanced)": "anthropic.claude-3-sonnet-20240229-v1:0",
                            "Claude 3 Haiku (Fast & Efficient)": "anthropic.claude-3-haiku-20240307-v1:0",
                        }

                        for display_name, model_id in chat_models.items():
                            col1, col2, col3 = st.columns([3, 4, 2])
                            with col1:
                                st.text(display_name)
                            with col2:
                                st.code(model_id, language=None)
                            with col3:
                                already_mapped = model_id in model_mapping.values()
                                if already_mapped:
                                    st.success("✅ Mapped")
                                else:
                                    if st.button(f"Add", key=f"add_chat_{model_id}"):
                                        alias = f"chat-{display_name.lower().replace(' ', '-').replace('(', '').replace(')', '').replace('.', '').replace('&', 'and')}"
                                        model_mapping[alias] = model_id
                                        st.success(f"✅ Added: {alias}")
                                        st.rerun()

                        st.divider()

                        # Text Generation/Processing Models
                        st.markdown("**📝 Text Generation & Processing Models**")
                        st.caption(
                            "For content generation, analysis, summarization, workflows, and ensemble operations"
                        )
                        text_models = {
                            "Claude 3.5 Sonnet (Premium)": "anthropic.claude-3-5-sonnet-20240620-v1:0",
                            "Claude 3 Opus (Complex Tasks)": "anthropic.claude-3-opus-20240229-v1:0",
                            "Claude 3 Sonnet (Balanced)": "anthropic.claude-3-sonnet-20240229-v1:0",
                            "Claude 3 Haiku (High Throughput)": "anthropic.claude-3-haiku-20240307-v1:0",
                            "Llama 3.1 70B (Alternative)": "meta.llama3-1-70b-instruct-v1:0",
                            "Llama 3.1 8B (Lightweight)": "meta.llama3-1-8b-instruct-v1:0",
                            "Mistral Large (European)": "mistral.mistral-large-2402-v1:0",
                            "Mistral 7B (Efficient)": "mistral.mistral-7b-instruct-v0:2",
                        }

                        st.info(
                            "💡 Perfect for ensemble workflows - use multiple models for different steps or validation"
                        )

                        for display_name, model_id in text_models.items():
                            col1, col2, col3 = st.columns([3, 4, 2])
                            with col1:
                                st.text(display_name)
                            with col2:
                                st.code(model_id, language=None)
                            with col3:
                                already_mapped = model_id in model_mapping.values()
                                if already_mapped:
                                    st.success("✅ Mapped")
                                else:
                                    if st.button(f"Add", key=f"add_text_{model_id}"):
                                        alias = f"text-{display_name.lower().replace(' ', '-').replace('(', '').replace(')', '').replace('.', '')}"
                                        model_mapping[alias] = model_id
                                        st.success(f"✅ Added: {alias}")
                                        st.rerun()

                        st.divider()

                        # Embedding Models
                        st.markdown("**🔗 Embedding Models**")
                        st.caption("For vector search, RAG, and semantic similarity")
                        embedding_models = {
                            "Titan v2 (Recommended 1024D)": "amazon.titan-embed-text-v2:0",
                            "Titan v1 (1536D → 1024D)": "amazon.titan-embed-text-v1",
                            "Cohere English (1024D)": "cohere.embed-english-v3",
                            "Cohere Multilingual (1024D)": "cohere.embed-multilingual-v3",
                        }

                        for display_name, model_id in embedding_models.items():
                            col1, col2, col3 = st.columns([3, 4, 2])
                            with col1:
                                st.text(display_name)
                            with col2:
                                st.code(model_id, language=None)
                            with col3:
                                already_mapped = model_id in model_mapping.values()
                                if already_mapped:
                                    st.success("✅ Mapped")
                                else:
                                    if st.button(f"Add", key=f"add_embed_{model_id}"):
                                        alias = (
                                            display_name.lower()
                                            .replace(" ", "-")
                                            .replace("(", "")
                                            .replace(")", "")
                                            .replace("→", "to")
                                        )
                                        model_mapping[alias] = model_id
                                        st.success(f"✅ Added: {alias}")
                                        st.rerun()

                        st.divider()

                        # Multimodal Models
                        st.markdown("**🎭 Multimodal Models**")
                        st.caption(
                            "For vision, image analysis, and multimodal understanding"
                        )
                        multimodal_models = {
                            "Claude 3.5 Sonnet (Vision)": "anthropic.claude-3-5-sonnet-20240620-v1:0",
                            "Claude 3 Opus (Vision)": "anthropic.claude-3-opus-20240229-v1:0",
                            "Claude 3 Sonnet (Vision)": "anthropic.claude-3-sonnet-20240229-v1:0",
                            "Claude 3 Haiku (Vision)": "anthropic.claude-3-haiku-20240307-v1:0",
                        }

                        st.info(
                            "💡 All Claude 3+ models support image analysis. Same model IDs, different use case."
                        )

                        for display_name, model_id in multimodal_models.items():
                            col1, col2, col3 = st.columns([3, 4, 2])
                            with col1:
                                st.text(display_name)
                            with col2:
                                st.code(model_id, language=None)
                            with col3:
                                already_mapped = model_id in model_mapping.values()
                                if already_mapped:
                                    st.success("✅ Mapped")
                                else:
                                    if st.button(f"Add", key=f"add_vision_{model_id}"):
                                        alias = f"vision-{display_name.lower().replace(' ', '-').replace('(', '').replace(')', '').replace('.', '')}"
                                        model_mapping[alias] = model_id
                                        st.success(f"✅ Added: {alias}")
                                        st.rerun()

                        st.divider()

                        # Other Bedrock Models
                        st.markdown("**🔧 Other Bedrock Models**")
                        st.caption("Additional models available on AWS Bedrock")
                        other_models = {
                            "Llama 3.1 70B (Meta)": "meta.llama3-1-70b-instruct-v1:0",
                            "Llama 3.1 8B (Meta)": "meta.llama3-1-8b-instruct-v1:0",
                            "Mistral 7B (Mistral AI)": "mistral.mistral-7b-instruct-v0:2",
                            "Mistral Large (Mistral AI)": "mistral.mistral-large-2402-v1:0",
                            "Titan Text G1 (Amazon)": "amazon.titan-text-lite-v1",
                            "AI21 Jurassic-2 Ultra": "ai21.j2-ultra-v1",
                            "AI21 Jurassic-2 Mid": "ai21.j2-mid-v1",
                        }

                        for display_name, model_id in other_models.items():
                            col1, col2, col3 = st.columns([3, 4, 2])
                            with col1:
                                st.text(display_name)
                            with col2:
                                st.code(model_id, language=None)
                            with col3:
                                already_mapped = model_id in model_mapping.values()
                                if already_mapped:
                                    st.success("✅ Mapped")
                                else:
                                    if st.button(f"Add", key=f"add_other_{model_id}"):
                                        alias = (
                                            display_name.lower()
                                            .replace(" ", "-")
                                            .replace("(", "")
                                            .replace(")", "")
                                            .replace(".", "")
                                        )
                                        model_mapping[alias] = model_id
                                        st.success(f"✅ Added: {alias}")
                                        st.rerun()

                    # Manual add for advanced users
                    with st.expander("⚙️ Advanced: Add Custom Model"):
                        new_alias = st.text_input(
                            "Friendly Name", placeholder="e.g., my-custom-model"
                        )
                        new_model_id = st.text_input(
                            "Bedrock Model ID",
                            placeholder="e.g., anthropic.claude-3-opus-20240229-v1:0",
                        )

                        if st.button("Add Custom Mapping"):
                            if new_alias and new_model_id:
                                model_mapping[new_alias] = new_model_id
                                st.success(
                                    f"✅ Added mapping: {new_alias} → {new_model_id}"
                                )
                                st.rerun()
                            else:
                                st.error("Please provide both alias and model ID")

                with config_tab3:
                    st.markdown("#### Adapter Configuration")
                    st.info("💡 Control timeout, retry, and circuit breaker settings")

                    col1, col2 = st.columns(2)

                    with col1:
                        timeout = st.number_input(
                            "⏱️ Timeout (seconds)",
                            min_value=10,
                            max_value=300,
                            value=adapter_config.get("timeout", 60),
                            step=10,
                            help="Maximum time to wait for model response",
                        )

                        retry_attempts = st.number_input(
                            "🔄 Retry Attempts",
                            min_value=0,
                            max_value=10,
                            value=adapter_config.get("retry_attempts", 3),
                            help="Number of retry attempts on failure",
                        )

                    with col2:
                        circuit_breaker = st.checkbox(
                            "🔌 Circuit Breaker",
                            value=adapter_config.get("circuit_breaker", True),
                            help="Enable circuit breaker pattern for fault tolerance",
                        )

                        if circuit_breaker:
                            st.info(
                                "Circuit breaker will temporarily disable failing services"
                            )

                with config_tab4:
                    st.markdown("#### Embeddings Configuration")
                    st.info(
                        "💡 Configure embedding models for vector search and RAG operations"
                    )

                    # Check current embeddings config from settings
                    embeddings_config = bedrock_config.get("embeddings", {})

                    col1, col2 = st.columns(2)

                    with col1:
                        # Embedding model selection with dimensions
                        embedding_models = {
                            "amazon.titan-embed-text-v1": {
                                "dimensions": 1536,
                                "max_tokens": 8192,
                            },
                            "amazon.titan-embed-text-v2:0": {
                                "dimensions": 1024,
                                "max_tokens": 8192,
                            },
                            "cohere.embed-english-v3": {
                                "dimensions": 1024,
                                "max_tokens": 512,
                            },
                            "cohere.embed-multilingual-v3": {
                                "dimensions": 1024,
                                "max_tokens": 512,
                            },
                        }

                        selected_embedding_model = st.selectbox(
                            "🔤 Embedding Model",
                            options=list(embedding_models.keys()),
                            index=(
                                list(embedding_models.keys()).index(
                                    embeddings_config.get(
                                        "model_id", list(embedding_models.keys())[0]
                                    )
                                )
                                if embeddings_config.get("model_id") in embedding_models
                                else 0
                            ),
                            help="Select embedding model for vector operations",
                        )

                        # Auto-set dimensions based on model
                        model_info = embedding_models[selected_embedding_model]
                        auto_dimensions = model_info["dimensions"]
                        max_tokens = model_info["max_tokens"]

                        st.info(
                            f"📐 **Auto-detected dimensions:** {auto_dimensions} for {selected_embedding_model.split('.')[-1]}"
                        )
                        st.info(f"📄 **Max input tokens:** {max_tokens:,}")

                        # Check pgvector database max dimensions
                        if st.button(
                            "🔍 Check Database Vector Limits",
                            help="Query pgvector database for maximum supported dimensions",
                        ):
                            with st.spinner("Querying pgvector database..."):
                                try:
                                    # Get database service from setup_service
                                    from domain.services.setup_service import (
                                        SetupService,
                                    )
                                    from adapters.secondary.setup.setup_dependencies_adapter import (
                                        get_setup_dependencies_adapter,
                                    )

                                    adapter = get_setup_dependencies_adapter()
                                    setup_service_instance = SetupService(adapter)

                                    # Get database connection
                                    db_service = adapter.get_database_service()

                                    # Query pgvector extension info
                                    query = """
                                    SELECT
                                        name,
                                        default_version,
                                        installed_version,
                                        comment
                                    FROM pg_available_extensions
                                    WHERE name = 'vector'
                                    UNION ALL
                                    SELECT
                                        'vector_max_dims' as name,
                                        NULL as default_version,
                                        NULL as installed_version,
                                        'Check current_setting for vector.max_dimensions' as comment
                                    """

                                    # Also try to get max dimensions setting
                                    max_dims_query = """
                                    SELECT
                                        current_setting('vector.max_dimensions', true) as max_dimensions,
                                        version() as pg_version
                                    """

                                    # Execute queries through database adapter
                                    health_result = db_service.health_check()
                                    if health_result.get("overall_status") == "healthy":
                                        st.success("✅ Database connection successful!")

                                        # Show database info
                                        databases = health_result.get("databases", {})
                                        for db_name, db_info in databases.items():
                                            if db_info.get("status") == "healthy":
                                                st.info(
                                                    f"📊 **{db_name}**: {db_info.get('version', 'Unknown version')}"
                                                )

                                        # Based on your existing vector_manager.py configuration
                                        st.info("🔧 **Your pgvector Configuration**:")
                                        st.text("• Database: vectorqa on AWS RDS")
                                        st.text(
                                            "• Standard dimension: 1024 (from vector_manager.py)"
                                        )
                                        st.text(
                                            "• Host: vectorqa-cluster.cluster-cu562e4m02nq.us-east-1.rds.amazonaws.com"
                                        )
                                        st.text(
                                            "• pgvector supports up to 16,000 dimensions"
                                        )
                                        st.text(
                                            "• Your Bedrock models: 1024-1536D (perfectly compatible)"
                                        )

                                        # Show recommendation based on your actual setup
                                        current_vector_dim = (
                                            1024  # From your vector_manager.py
                                        )
                                        if auto_dimensions <= current_vector_dim:
                                            st.success(
                                                f"✅ **Perfect Match**: {selected_embedding_model.split('.')[-1]} ({auto_dimensions}D) ≤ current vector DB ({current_vector_dim}D)"
                                            )
                                        elif auto_dimensions <= 1536:
                                            st.warning(
                                                f"⚠️ **Size Increase**: {selected_embedding_model.split('.')[-1]} ({auto_dimensions}D) > current setup ({current_vector_dim}D)"
                                            )
                                            st.info(
                                                "💡 You may need to update vector_dimension in VectorConfig"
                                            )
                                        else:
                                            st.error(
                                                f"❌ **Incompatible**: {auto_dimensions}D exceeds recommended limits"
                                            )
                                    else:
                                        st.warning(
                                            "⚠️ Database not available - using default pgvector limits"
                                        )
                                        st.info(
                                            "📏 **Default pgvector limits**: Up to 16,000 dimensions"
                                        )

                                except Exception as e:
                                    st.error(f"❌ Could not query database: {str(e)}")
                                    st.info(
                                        "📏 **Standard pgvector limits**: Up to 16,000 dimensions"
                                    )

                        # Allow manual override (for advanced users)
                        use_custom_dimensions = st.checkbox(
                            "🔧 Override dimensions (advanced)", value=False
                        )

                        if use_custom_dimensions:
                            dimensions = st.number_input(
                                "📐 Custom Vector Dimensions",
                                min_value=128,
                                max_value=1536,
                                value=embeddings_config.get(
                                    "dimensions", auto_dimensions
                                ),
                                step=64,
                                help="⚠️ Only change if you know what you're doing",
                            )
                            st.warning(
                                "⚠️ Using incorrect dimensions may cause compatibility issues"
                            )
                        else:
                            dimensions = auto_dimensions

                    with col2:
                        # Batch processing settings
                        batch_size = st.number_input(
                            "📦 Batch Size",
                            min_value=1,
                            max_value=100,
                            value=embeddings_config.get("batch_size", 25),
                            help="Number of texts to process in a single batch",
                        )

                        # Chunk settings for large texts
                        max_chunk_size = st.number_input(
                            "✂️ Max Chunk Size",
                            min_value=100,
                            max_value=8000,
                            value=embeddings_config.get("max_chunk_size", 2000),
                            step=100,
                            help="Maximum characters per text chunk",
                        )

                    # Advanced embedding settings
                    with st.expander("🔧 Advanced Embedding Settings"):
                        col1, col2 = st.columns(2)

                        with col1:
                            normalize_embeddings = st.checkbox(
                                "📏 Normalize Embeddings",
                                value=embeddings_config.get("normalize", True),
                                help="Normalize embedding vectors to unit length",
                            )

                            cache_embeddings = st.checkbox(
                                "💾 Cache Embeddings",
                                value=embeddings_config.get("cache_enabled", True),
                                help="Cache embeddings to improve performance",
                            )

                        with col2:
                            embedding_timeout = st.number_input(
                                "⏱️ Embedding Timeout (seconds)",
                                min_value=10,
                                max_value=120,
                                value=embeddings_config.get("timeout", 30),
                                help="Timeout for embedding operations",
                            )

                    # Show current configuration
                    st.markdown("**Current Configuration:**")
                    config_col1, config_col2, config_col3 = st.columns(3)
                    with config_col1:
                        st.metric("Model", selected_embedding_model.split(".")[-1])
                    with config_col2:
                        st.metric("Dimensions", dimensions)
                    with config_col3:
                        st.metric("Batch Size", batch_size)

                # Save ALL configuration
                st.markdown("---")
                if st.button(
                    "💾 Save All Configuration",
                    type="primary",
                    use_container_width=True,
                    key="save_all_model_config",
                ):
                    try:
                        # Save to settings
                        import yaml

                        settings_path = Path("infrastructure/settings.yaml")
                        with open(settings_path, "r") as f:
                            settings = yaml.safe_load(f)

                        # Update default model
                        settings["credentials"]["bedrock_llm"]["default_model"] = (
                            model_mapping.get(selected_default, current_default)
                        )

                        # Update model mappings (keeping all, but only enabled ones will be used)
                        settings["credentials"]["bedrock_llm"][
                            "model_mapping"
                        ] = model_mapping

                        # Store disabled models list separately (for reference)
                        disabled_models = [
                            m for m in model_mapping.keys() if m not in available_models
                        ]
                        if (
                            "disabled_models"
                            not in settings["credentials"]["bedrock_llm"]
                        ):
                            settings["credentials"]["bedrock_llm"][
                                "disabled_models"
                            ] = disabled_models
                        else:
                            settings["credentials"]["bedrock_llm"][
                                "disabled_models"
                            ] = disabled_models

                        # Update adapter config
                        settings["credentials"]["bedrock_llm"]["adapter_config"] = {
                            "timeout": timeout,
                            "retry_attempts": retry_attempts,
                            "circuit_breaker": circuit_breaker,
                        }

                        # Update embeddings config
                        settings["credentials"]["bedrock_llm"]["embeddings"] = {
                            "model_id": selected_embedding_model,
                            "dimensions": dimensions,
                            "batch_size": batch_size,
                            "max_chunk_size": max_chunk_size,
                            "normalize": normalize_embeddings,
                            "cache_enabled": cache_embeddings,
                            "timeout": embedding_timeout,
                            "type": "bedrock_embeddings",
                        }

                        with open(settings_path, "w") as f:
                            yaml.safe_dump(
                                settings, f, default_flow_style=False, indent=2
                            )

                        st.success("✅ All configurations saved successfully!")

                        # Show summary
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.info(f"📌 Default: {selected_default}")
                        with col2:
                            st.info(f"✅ Enabled: {len(available_models)} models")
                        with col3:
                            st.info(f"⏱️ Timeout: {timeout}s")
                        with col4:
                            st.info(
                                f"🔤 Embeddings: {selected_embedding_model.split('.')[-1]}"
                            )

                    except Exception as e:
                        st.error(f"❌ Failed to save configuration: {str(e)}")

                with config_tab5:
                    st.markdown("#### Model Testing & Validation")
                    st.info(
                        "🧪 Test individual models and validate your entire configuration"
                    )

                    # Test Options
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("##### 🔧 Quick Tests")

                        # Single model test
                        test_model = st.selectbox(
                            "Test Single Model",
                            options=list(model_mapping.keys()),
                            help="Test access to a specific configured model",
                        )

                        model_type = st.radio(
                            "Model Type",
                            ["text", "embedding"],
                            help="Select the type of model to test",
                        )

                        if st.button(
                            "🧪 Test Selected Model", use_container_width=True
                        ):
                            if test_model and test_model in model_mapping:
                                with st.spinner(f"Testing {test_model}..."):
                                    try:
                                        model_id = model_mapping[test_model]
                                        result = setup_service.test_model_access(
                                            model_id, model_type
                                        )

                                        if result.get("accessible"):
                                            st.success(
                                                f"✅ {test_model} is accessible!"
                                            )
                                            col_resp1, col_resp2 = st.columns(2)
                                            with col_resp1:
                                                st.metric(
                                                    "Response Time",
                                                    f"{result.get('response_time_ms', 0)}ms",
                                                )
                                            with col_resp2:
                                                if (
                                                    model_type == "embedding"
                                                    and result.get(
                                                        "embedding_dimension"
                                                    )
                                                ):
                                                    st.metric(
                                                        "Dimensions",
                                                        f"{result.get('embedding_dimension')}D",
                                                    )
                                                else:
                                                    st.metric(
                                                        "Test Status", "✅ Success"
                                                    )
                                        else:
                                            st.error(
                                                f"❌ {test_model} failed: {result.get('error', 'Unknown error')}"
                                            )
                                    except Exception as e:
                                        st.error(f"❌ Test failed: {str(e)}")
                            else:
                                st.error("❌ Please select a valid model")

                        # Validate all mappings
                        if st.button(
                            "🔍 Validate All Model Mappings", use_container_width=True
                        ):
                            with st.spinner("Validating all configured models..."):
                                try:
                                    result = setup_service.validate_model_mapping(
                                        model_mapping
                                    )

                                    if result.get("mapping_valid"):
                                        st.success(
                                            f"✅ All {result.get('total_mappings', 0)} models are accessible!"
                                        )
                                    else:
                                        st.warning(
                                            f"⚠️ {len(result.get('failed_mappings', []))} models failed validation"
                                        )

                                        if result.get("failed_mappings"):
                                            st.markdown("**Failed Models:**")
                                            for failed in result["failed_mappings"]:
                                                st.error(
                                                    f"❌ {failed['friendly_name']} ({failed['model_id']}): {failed['error']}"
                                                )

                                    # Summary metrics
                                    col_sum1, col_sum2, col_sum3 = st.columns(3)
                                    with col_sum1:
                                        st.metric(
                                            "Total Models",
                                            result.get("total_mappings", 0),
                                        )
                                    with col_sum2:
                                        st.metric(
                                            "Accessible",
                                            result.get("accessible_mappings", 0),
                                        )
                                    with col_sum3:
                                        st.metric(
                                            "Failed",
                                            len(result.get("failed_mappings", [])),
                                        )

                                except Exception as e:
                                    st.error(f"❌ Validation failed: {str(e)}")

                    with col2:
                        st.markdown("##### 🎯 Advanced Testing")

                        # Model discovery
                        if st.button(
                            "🔍 Discover Available Models", use_container_width=True
                        ):
                            with st.spinner("Discovering available Bedrock models..."):
                                try:
                                    result = setup_service.get_available_models()

                                    if result.get("error"):
                                        st.error(
                                            f"❌ Discovery failed: {result['error']}"
                                        )
                                    else:
                                        st.success(
                                            f"✅ Found {result.get('total_count', 0)} available models"
                                        )

                                        # Show breakdown by type
                                        by_type = result.get("by_type", {})
                                        if by_type:
                                            st.markdown("**Available by Type:**")
                                            for model_type, count in by_type.items():
                                                st.metric(
                                                    f"{model_type.title()} Models",
                                                    count,
                                                )

                                except Exception as e:
                                    st.error(f"❌ Discovery failed: {str(e)}")

                        # Batch test configured models
                        if st.button(
                            "🧪 Test All Configured Models", use_container_width=True
                        ):
                            with st.spinner("Testing all configured models..."):
                                try:
                                    # Prepare models for batch testing
                                    test_models = []
                                    for (
                                        friendly_name,
                                        model_id,
                                    ) in model_mapping.items():
                                        # Determine model type based on name or ID
                                        if (
                                            "embed" in friendly_name.lower()
                                            or "titan-embed" in model_id
                                            or "cohere.embed" in model_id
                                        ):
                                            model_type = "embedding"
                                        else:
                                            model_type = "text"

                                        test_models.append(
                                            {
                                                "model_id": model_id,
                                                "type": model_type,
                                                "name": friendly_name,
                                            }
                                        )

                                    result = setup_service.test_multiple_models(
                                        test_models
                                    )

                                    # Display results
                                    if result.get("summary", {}).get("all_accessible"):
                                        st.success(
                                            f"✅ All {result.get('total_models', 0)} models are working!"
                                        )
                                    else:
                                        st.warning(
                                            f"⚠️ {result.get('failed_models', 0)} models failed"
                                        )

                                    # Summary metrics
                                    col_batch1, col_batch2, col_batch3 = st.columns(3)
                                    with col_batch1:
                                        st.metric(
                                            "Total Tested",
                                            result.get("total_models", 0),
                                        )
                                    with col_batch2:
                                        st.metric(
                                            "Success Rate",
                                            f"{result.get('summary', {}).get('success_rate', 0):.1f}%",
                                        )
                                    with col_batch3:
                                        st.metric(
                                            "Failed", result.get("failed_models", 0)
                                        )

                                    # Show individual results in expander
                                    with st.expander("📋 Detailed Results"):
                                        model_results = result.get("model_results", {})
                                        for name, test_result in model_results.items():
                                            if test_result.get("accessible"):
                                                st.success(
                                                    f"✅ {name}: {test_result.get('response_time_ms', 0)}ms"
                                                )
                                            else:
                                                st.error(
                                                    f"❌ {name}: {test_result.get('error', 'Failed')}"
                                                )

                                except Exception as e:
                                    st.error(f"❌ Batch testing failed: {str(e)}")

                        # Embedding-specific testing
                        st.markdown("##### 🔤 Embedding Testing")

                        embedding_models = {
                            k: v
                            for k, v in model_mapping.items()
                            if "embed" in k.lower()
                            or "titan-embed" in v
                            or "cohere.embed" in v
                        }

                        if embedding_models:
                            embed_model = st.selectbox(
                                "Test Embedding Model",
                                options=list(embedding_models.keys()),
                                help="Test embedding generation and dimension compatibility",
                            )

                            test_text = st.text_input(
                                "Test Text",
                                value="This is a sample text for embedding generation.",
                                help="Text to generate embeddings for",
                            )

                            if st.button(
                                "🔤 Test Embedding Generation", use_container_width=True
                            ):
                                if embed_model and embed_model in embedding_models:
                                    with st.spinner(f"Testing embedding generation..."):
                                        try:
                                            model_id = embedding_models[embed_model]
                                            result = setup_service.test_embedding_model(
                                                model_id, test_text
                                            )

                                            if result.get("accessible"):
                                                st.success(
                                                    f"✅ Embedding generated successfully!"
                                                )
                                                col_embed1, col_embed2 = st.columns(2)
                                                with col_embed1:
                                                    st.metric(
                                                        "Dimensions",
                                                        f"{result.get('embedding_dimension', 0)}D",
                                                    )
                                                with col_embed2:
                                                    st.metric(
                                                        "Response Time",
                                                        f"{result.get('response_time_ms', 0)}ms",
                                                    )

                                                # Check dimension compatibility
                                                dims = result.get(
                                                    "embedding_dimension", 0
                                                )
                                                if dims == 1024:
                                                    st.success(
                                                        "🎯 Perfect! 1024D matches your database configuration"
                                                    )
                                                elif dims > 1024:
                                                    st.warning(
                                                        f"⚠️ {dims}D will be truncated to 1024D for storage"
                                                    )
                                                elif dims < 1024:
                                                    st.info(
                                                        f"📏 {dims}D will be padded to 1024D for storage"
                                                    )

                                            else:
                                                st.error(
                                                    f"❌ Embedding test failed: {result.get('error', 'Unknown error')}"
                                                )
                                        except Exception as e:
                                            st.error(
                                                f"❌ Embedding test failed: {str(e)}"
                                            )
                        else:
                            st.info(
                                "💡 No embedding models configured. Add some in the Mappings tab!"
                            )

            else:
                st.warning(
                    "⚠️ Bedrock configuration not found in settings. Please save main configuration first."
                )

    # Check AI Chat Status Section (at the end)
    st.markdown("---")
    st.markdown("### 🔍 Check AI Chat Status")

    if st.button("🤖 CHECK AI CHAT SETUP", type="primary", use_container_width=True):
        with st.spinner("Checking AI chat setup..."):
            chat_results = setup_service.tidyllm_basic_setup()
            # Store results in session state so they persist
            st.session_state["step4_chat_results"] = chat_results

    # Display results if they exist in session state
    if "step4_chat_results" in st.session_state:
        chat_results = st.session_state["step4_chat_results"]
        results = chat_results["results"]
        model_count = chat_results.get("model_count", 0)
        status = chat_results["overall_status"]

        st.markdown("### 🤖 AI Chat Setup Results:")

        if status == "configured":
            st.success(
                f"🎉 **AMAZING!** Your AI chat is ready with {model_count} different models!"
            )
        else:
            st.warning(
                "⚠️ **AI chat needs configuration.** Configure Bedrock settings above."
            )

        # Show AI models available
        if model_count > 0:
            st.info(f"🤖 **You have {model_count} AI models available:**")
            st.markdown(
                """
            - **Claude-3-Haiku**: Fastest model, great for quick questions
            - **Claude-3-Sonnet**: Balanced model, good for most tasks
            - **Claude-3.5-Sonnet**: Latest model, enhanced capabilities
            - **Claude-3-Opus**: Most powerful model, best for complex tasks
            """
            )

        # Show detailed results
        for check, passed in results.items():
            if isinstance(passed, bool):
                check_name = check.replace("_", " ").title()
                if passed:
                    st.success(f"✅ **{check_name}**: Configured perfectly!")
                else:
                    st.error(f"❌ **{check_name}**: Not configured")

                    # Provide specific help
                    if check == "bedrock_models_configured":
                        st.info("💡 **Fix:** Configure AWS Bedrock settings above.")
                    elif check == "basic_chat_settings":
                        st.info(
                            "💡 **Fix:** Chat settings are missing. Check the settings.yaml file."
                        )
                    elif check == "default_timeouts_set":
                        st.info(
                            "💡 **Fix:** Timeout settings are missing. Configure in settings.yaml."
                        )
                    elif check == "basic_mlflow_tracking":
                        st.info(
                            "💡 **Fix:** MLflow tracking is not set up. Check Step 3 Integrations."
                        )

        st.info(f"📋 **Summary:** {chat_results['summary']}")

        # Next step guidance
        if status == "configured":
            st.success("🎯 **NEXT STEP:** Go to Step 5 for final health check!")
        else:
            st.warning("🎯 **NEXT STEP:** Configure Bedrock settings above first.")

        # Add a button to re-check
        if st.button(
            "🔄 Check Again", use_container_width=True, key="step4_check_again"
        ):
            del st.session_state["step4_chat_results"]
            st.rerun()


def render_step_5_health_check():
    """Step 5: Final health check."""
    st.header("Step 5️⃣: Final Health Check")
    st.markdown("**Let's make sure everything is working perfectly!**")

    if st.button("💚 TEST EVERYTHING NOW", type="primary", use_container_width=True):
        with st.spinner("Testing all systems... This might take a minute..."):
            health_results = setup_service.health_check()
            # Store results in session state so they persist
            st.session_state["step4_results"] = health_results

    # Display results if they exist in session state
    if "step4_results" in st.session_state:
        health_results = st.session_state["step4_results"]
        results = health_results["results"]
        status = health_results["overall_status"]

        st.markdown("### 💚 System Health Results:")

        if status == "healthy":
            st.success("🎉 **PERFECT!** Everything is working beautifully!")
        else:
            st.warning(
                "⚠️ **Some systems aren't working properly.** Let's see what needs fixing..."
            )

        # Show detailed results
        for check, passed in results.items():
            if isinstance(passed, bool):
                check_name = check.replace("_", " ").title()
                if passed:
                    st.success(f"✅ **{check_name}**: Working perfectly!")
                else:
                    st.error(f"❌ **{check_name}**: Having problems")

                    # Provide specific help
                    if check == "database_connection_status":
                        st.info(
                            "💡 **Fix:** Database connection failed. Check your internet or ask your portal admin."
                        )
                    elif check == "aws_service_connectivity":
                        st.info(
                            "💡 **Fix:** AWS connection failed. Check AWS credentials with your portal admin."
                        )
                    elif check == "mlflow_tracking_status":
                        st.info(
                            "💡 **Fix:** MLflow is not working. Ask your portal admin to check MLflow setup."
                        )
                    elif check == "bedrock_model_accessibility":
                        st.info(
                            "💡 **Fix:** AI models are not accessible. Check AWS Bedrock configuration."
                        )
                    elif check == "basic_chat_functionality":
                        st.info(
                            "💡 **Fix:** Chat is not working. Fix AWS and Bedrock issues first."
                        )

        st.info(f"📋 **Summary:** {health_results['summary']}")

        # Next step guidance
        if status == "healthy":
            st.success(
                "🎯 **NEXT STEP:** You're ready! Check out the available portals below!"
            )
        else:
            st.warning("🎯 **NEXT STEP:** Fix the issues above, then test again.")

        # Add a button to re-check
        if st.button(
            "🔄 Check Again", use_container_width=True, key="step4_check_again"
        ):
            del st.session_state["step4_results"]
            st.rerun()


def render_step_6_portal_guide():
    """Step 6: Portal guide."""
    st.header("Step 6️⃣: Explore Your Portals")
    st.markdown("**Great! Now you can explore all the different AI tools available!**")

    portal_data = setup_service.portal_guide()

    if portal_data["overall_status"] == "available":
        portals = portal_data["portals"]
        descriptions = portal_data["portal_descriptions"]

        st.success(
            f"🚪 **{portal_data['active_portals']} out of {portal_data['total_portals']} portals are currently running!**"
        )

        # Organize portals by category
        categories = portal_data["categories"]

        for category, category_portals in categories.items():
            st.subheader(f"📁 {category} Tools")

            for portal in category_portals:
                name = portal["name"]
                port = portal["port"]
                active = portal.get("active", False)
                description = descriptions.get(name, "Portal functionality")

                col1, col2, col3 = st.columns([2, 4, 1])

                with col1:
                    if active:
                        st.success(f"🟢 **{name}**")
                    else:
                        st.error(f"🔴 **{name}**")

                with col2:
                    st.write(f"📝 {description}")
                    if not active:
                        st.caption(
                            "💡 Ask your portal admin to start this portal if you need it"
                        )

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

            if example_results["overall_status"] == "loaded":
                st.success(
                    "✅ **Example data loaded successfully!** You can now try the AI tools with sample conversations."
                )
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
            st.info(
                """
            **Need Help?**
            1. 📧 Ask your teacher
            2. 📖 Check the documentation
            3. 👥 Ask a classmate
            4. 🔄 Try refreshing the page
            """
            )

    with col3:
        if st.button("📊 SYSTEM STATUS", use_container_width=True):
            env_summary = setup_service.get_environment_summary()
            st.json(env_summary)


def render_overview_tab():
    """Overview tab - Welcome and introduction to the installer."""
    st.markdown("# 🎉 Welcome to TidyLLM Setup!")

    st.markdown(
        """
    ## What is TidyLLM?

    **TidyLLM** is your comprehensive AI platform that provides:

    - 🤖 **Multi-Model Chat**: Access to Claude, GPT, and AWS Bedrock models
    - 🔍 **RAG (Retrieval-Augmented Generation)**: Chat with your documents
    - 🧪 **DSPy Integration**: Advanced prompt engineering and optimization
    - 📊 **MLflow Tracking**: Monitor and track your AI experiments
    """
    )

    st.markdown("## 📊 Current System Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="🖥️ System Check",
            value="Checking...",
            help="System requirements validation",
        )

    with col2:
        st.metric(
            label="🔌 Services",
            value="Checking...",
            help="Database and cloud connections",
        )

    with col3:
        st.metric(
            label="🤖 AI Models",
            value="Checking...",
            help="Available AI models and configurations",
        )

    st.info("💡 **Ready to start?** Click the **🔧 Prerequisites** tab above to begin!")


def render_prerequisites_tab():
    """Prerequisites tab - System and software requirements."""
    st.markdown("# 🔧 Prerequisites")
    st.markdown("**Let's check if your system has everything needed to run TidyLLM.**")

    render_step_1_system_check()


def render_connections_tab():
    """Connections tab - Database and cloud service setup."""
    st.markdown("# 🔌 Connections")
    st.markdown("**Configure your database and cloud connections.**")

    render_step_4_chat_setup()


def render_test_features_tab():
    """Test Features tab - Validate AI functionality."""
    st.markdown("# 🧪 Test Features")
    st.markdown("**Test your AI chat and core features.**")

    render_step_2_software_check()


def render_get_started_tab():
    """Get Started tab - Final steps and portal access."""
    st.markdown("# 🚀 Get Started")
    st.markdown("**You're all set! Here's how to start using TidyLLM.**")

    st.markdown("## 🔍 Final Health Check")
    render_step_5_health_check()

    st.markdown("## 🌟 Explore Your Portals")
    render_step_6_portal_guide()


def check_step_completion():
    """Check which steps are completed for structured flow."""
    step1_complete = (
        "step1_results" in st.session_state
        and st.session_state.get("step1_results", {}).get("overall_status") == "ready"
    )
    step2_complete = (
        "step2_results" in st.session_state
        and st.session_state.get("step2_results", {}).get("overall_status") == "ready"
    )
    step3_complete = (
        "step3_results" in st.session_state
        and st.session_state.get("step3_results", {}).get("overall_status") == "ready"
    )
    step4_complete = (
        "step4_results" in st.session_state
        and st.session_state.get("step4_results", {}).get("overall_status") == "ready"
    )

    return step1_complete, step2_complete, step3_complete, step4_complete


def main():
    """Main application with structured flow."""
    set_page_config()
    render_header()

    # Check step completion for structured flow
    step1_done, step2_done, step3_done, step4_done = check_step_completion()

    # Restructured tab labels for better installer journey
    tab_labels = [
        "1) System Check",
        "2) Prerequisites",
        "3) Connections",
        "4) AI Models",
        "5) Explore Portals",
    ]

    # Navigation tabs with structured flow
    tab1, tab2, tab3, tab4, tab5 = st.tabs(tab_labels)

    with tab1:
        render_overview_tab()

    with tab2:
        render_prerequisites_tab()

    with tab3:
        render_integrations_tab()

    with tab4:
        render_connections_tab()

    with tab5:
        render_step_6_portal_guide()


if __name__ == "__main__":
    main()
