"""
Tab 1: System Check - First step of setup process
"""
import streamlit as st


def render(setup_service):
    """Step 1: Check if everything is ready."""
    st.header("Step 1️⃣: System & AWS Setup")
    st.markdown("**Check your system status and configure AWS credentials.**")

    # Current System Status Section
    st.markdown("### 📊 Current System Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 🖥️ System Check")
        with st.spinner("Checking..."):
            try:
                # Quick system check
                import sys
                import os
                if sys.version_info >= (3, 8):
                    st.success("✅ Python OK")
                else:
                    st.error("❌ Python version")

                if os.path.exists("infrastructure/settings.yaml"):
                    st.success("✅ Settings found")
                else:
                    st.warning("⚠️ Settings missing")
            except:
                st.error("❌ Check failed")

    with col2:
        st.markdown("#### 🔌 Services")
        with st.spinner("Checking..."):
            try:
                # Check database connection
                from infrastructure.yaml_loader import get_settings_loader
                loader = get_settings_loader()
                settings = loader._load_settings()

                if 'postgresql_primary' in settings.get('credentials', {}):
                    st.success("✅ Database configured")
                else:
                    st.warning("⚠️ Database not configured")

                if 'mlflow' in settings.get('integrations', {}):
                    st.success("✅ MLflow configured")
                else:
                    st.warning("⚠️ MLflow not configured")
            except:
                st.error("❌ Services check failed")

    with col3:
        st.markdown("#### 🤖 AI Models")
        with st.spinner("Checking..."):
            try:
                # Check AI model configuration using SettingsLoader (cached)
                from infrastructure.yaml_loader import get_settings_loader

                # Cache the loader in session state
                if 'settings_loader' not in st.session_state:
                    st.session_state.settings_loader = get_settings_loader()

                loader = st.session_state.settings_loader
                bedrock_config = loader.get_bedrock_config()

                if bedrock_config:
                    model_id = bedrock_config.get('default_model')
                    if model_id:
                        st.success(f"✅ {model_id.split('.')[0].title()}")
                    else:
                        st.warning("⚠️ No model selected")
                else:
                    st.warning("⚠️ Bedrock not configured")

                if 'aws_basic' in settings.get('credentials', {}):
                    if settings['credentials']['aws_basic'].get('access_key_id'):
                        st.success("✅ AWS credentials set")
                    else:
                        st.error("❌ AWS credentials missing")
                else:
                    st.error("❌ AWS not configured")
            except:
                st.warning("⚠️ AI models not configured")

    st.info("💡 **Ready to start?** Complete each section below to set up your AI portal!")

    # Divider
    st.markdown("---")

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
            from infrastructure.yaml_loader import get_settings_loader

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

    # Test Features Section
    st.markdown("---")
    st.markdown("### 🧪 Test Features")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🗄️ Test Database", use_container_width=True):
            with st.spinner("Testing database connection..."):
                try:
                    import psycopg2
                    from infrastructure.yaml_loader import get_settings_loader
                    loader = get_settings_loader()
                    settings = loader._load_settings()
                    pg = settings['credentials']['postgresql_primary']

                    conn = psycopg2.connect(
                        host=pg['host'],
                        port=pg['port'],
                        database=pg['database'],
                        user=pg['username'],
                        password=pg['password']
                    )
                    conn.close()
                    st.success("✅ Database connection successful!")
                except Exception as e:
                    st.error(f"❌ Database error: {str(e)}")

    with col2:
        if st.button("☁️ Test S3 Access", use_container_width=True):
            with st.spinner("Testing S3 access..."):
                try:
                    import boto3
                    from infrastructure.yaml_loader import get_settings_loader
                    loader = get_settings_loader()
                    settings = loader._load_settings()
                    aws = settings['credentials']['aws_basic']

                    s3 = boto3.client(
                        's3',
                        aws_access_key_id=aws['access_key_id'],
                        aws_secret_access_key=aws['secret_access_key'],
                        region_name=aws.get('default_region', 'us-east-1')
                    )
                    buckets = s3.list_buckets()
                    st.success(f"✅ S3 access OK! {len(buckets['Buckets'])} bucket(s)")
                except Exception as e:
                    st.error(f"❌ S3 error: {str(e)}")

    with col3:
        if st.button("🤖 Test AI Model", use_container_width=True):
            with st.spinner("Testing AI model..."):
                try:
                    import boto3
                    import json
                    from infrastructure.yaml_loader import get_settings_loader

                    # Use cached loader from session state
                    if 'settings_loader' not in st.session_state:
                        st.session_state.settings_loader = get_settings_loader()

                    loader = st.session_state.settings_loader
                    settings = loader._load_settings()

                    aws = settings['credentials']['aws_basic']
                    # Use SettingsLoader for consistent bedrock config access
                    bedrock_config = loader.get_bedrock_config()
                    model_id = bedrock_config.get('default_model') if bedrock_config else None

                    if not model_id or model_id == "":
                        st.warning("⚠️ No model configured. Set up in AI Models tab.")
                        st.info("Default model should be: anthropic.claude-3-sonnet-20240229-v1:0")
                    elif len(str(model_id)) < 1:
                        st.error("❌ Model ID is invalid (empty string)")
                    else:
                        # Get region from bedrock_config or fall back to aws default region
                        region = bedrock_config.get('region') if bedrock_config else None
                        if not region:
                            region = aws.get('default_region', 'us-east-1')

                        bedrock = boto3.client(
                            'bedrock-runtime',
                            region_name=region,
                            aws_access_key_id=aws['access_key_id'],
                            aws_secret_access_key=aws['secret_access_key']
                        )

                        # Use Messages API for Claude 3 models
                        if 'claude-3' in model_id.lower() or 'claude-3' in model_id:
                            # Claude 3 uses Messages API
                            test_body = {
                                "anthropic_version": "bedrock-2023-05-31",
                                "max_tokens": 10,
                                "temperature": 0,
                                "messages": [
                                    {
                                        "role": "user",
                                        "content": "Say 'OK'"
                                    }
                                ]
                            }
                        else:
                            # Legacy format for Claude 2 and older
                            test_body = {
                                "prompt": "\n\nHuman: Say 'OK'\n\nAssistant:",
                                "max_tokens_to_sample": 10,
                                "temperature": 0
                            }

                        # Debug: Show what model we're testing
                        st.info(f"Testing model: {model_id}")

                        response = bedrock.invoke_model(
                            modelId=model_id,
                            body=json.dumps(test_body)
                        )
                        st.success(f"✅ {model_id.split('.')[0]} responding!")
                except Exception as e:
                    st.error(f"❌ Model error: {str(e)[:100]}")

    # End of Tab
    st.markdown("---")
    st.markdown(
        """
    ### 🎯 **How to use this page:**
    - **Status Overview** shows your current configuration at a glance
    - **System Check** performs detailed analysis of requirements
    - **AWS Configuration** sets up S3 credentials for storage
    - **Test Features** verifies each component is working
    - **Green ✅** means everything is working
    - **Red ❌** means something needs to be fixed
    - **Yellow ⚠️** means there might be a small issue
    """
    )