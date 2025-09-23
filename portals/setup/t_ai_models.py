"""
Tab 4: AI Models - Configure AWS Bedrock
"""
import streamlit as st


def render(setup_service):
    """Step 4: Set up AI chat with Bedrock configuration."""
    st.header("Step 4️⃣: AI Models")
    st.markdown("**Configure your AI models and test the chat setup.**")

    # Bedrock Configuration Section
    st.markdown("### 🤖 AWS Bedrock Configuration")
    st.markdown("Configure your AI model settings for chat functionality.")

    # Load current settings
    try:
        from infrastructure.yaml_loader import get_settings_loader
        settings_loader = get_settings_loader()
        raw_settings = settings_loader._load_settings()

        # Get Bedrock configuration
        bedrock_config = raw_settings.get('llm_models', {}).get('bedrock', {})
        current_model_id = bedrock_config.get('model_id', '')
        current_region = bedrock_config.get('region', 'us-east-1')
        current_max_tokens = bedrock_config.get('max_tokens', 4096)
        current_temperature = bedrock_config.get('temperature', 0.7)

        # Get AWS credentials
        aws_creds = raw_settings.get('credentials', {}).get('aws_basic', {})
        has_aws_creds = bool(aws_creds.get('access_key_id') and aws_creds.get('secret_access_key'))

        if has_aws_creds:
            st.success("✅ AWS credentials configured (using credentials from Prerequisites)")
        else:
            st.warning("⚠️ AWS credentials not configured - set them in System Check tab first")

        st.info(f"💡 **Current Model**: {current_model_id or 'Not configured'}")

    except Exception as e:
        st.warning(f"⚠️ Could not load current Bedrock settings: {str(e)}")
        current_model_id = ''
        current_region = 'us-east-1'
        current_max_tokens = 4096
        current_temperature = 0.7
        has_aws_creds = False

    # Configuration form
    with st.form("bedrock_config_form"):
        st.markdown("**Model Selection**")

        col1, col2 = st.columns(2)

        with col1:
            # Available Bedrock models (updated to current versions)
            bedrock_models = [
                "anthropic.claude-3-haiku-20240307-v1:0",
                "anthropic.claude-3-sonnet-20240229-v1:0",
                "anthropic.claude-3-5-sonnet-20240620-v1:0",
                "anthropic.claude-3-5-sonnet-20241022-v2:0",  # Latest Claude 3.5
                "anthropic.claude-3-opus-20240229-v1:0",
                "anthropic.claude-instant-v1",
                "amazon.titan-text-premier-v1:0",
                "amazon.titan-text-express-v1",
                "amazon.titan-text-lite-v1",
                "meta.llama3-8b-instruct-v1:0",
                "meta.llama3-70b-instruct-v1:0",
                "meta.llama3-1-8b-instruct-v1:0",
                "meta.llama3-1-70b-instruct-v1:0",
                "meta.llama3-1-405b-instruct-v1:0"
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
                help="Select the AI model to use"
            )

            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=float(current_temperature),
                step=0.1,
                help="Controls randomness in responses (0=deterministic, 1=creative)"
            )

        with col2:
            region = st.selectbox(
                "AWS Region",
                ["us-east-1", "us-west-2", "eu-west-1", "eu-central-1", "ap-southeast-1"],
                index=0 if current_region == "us-east-1" else None,
                help="AWS region where Bedrock is available"
            )

            max_tokens = st.number_input(
                "Max Tokens",
                min_value=100,
                max_value=100000,
                value=int(current_max_tokens),
                step=100,
                help="Maximum response length"
            )

        st.markdown("**Additional Settings**")
        enable_streaming = st.checkbox("Enable Response Streaming", value=True, help="Stream responses in real-time")
        enable_fallback = st.checkbox("Enable Model Fallback", value=True, help="Fallback to alternative model if primary fails")

        # Form buttons
        col_test, col_save = st.columns(2)

        with col_test:
            test_clicked = st.form_submit_button("🧪 Test Bedrock Access", use_container_width=True)

        with col_save:
            save_clicked = st.form_submit_button("💾 Save Configuration", use_container_width=True, type="primary")

        if test_clicked:
            if not has_aws_creds:
                st.error("❌ Please configure AWS credentials in System Check tab first")
            else:
                with st.spinner("Testing Bedrock access..."):
                    try:
                        import boto3

                        # Create Bedrock client
                        bedrock = boto3.client(
                            'bedrock-runtime',
                            region_name=region,
                            aws_access_key_id=aws_creds.get('access_key_id'),
                            aws_secret_access_key=aws_creds.get('secret_access_key')
                        )

                        # Simple test prompt
                        test_prompt = "Hello, please respond with 'OK' if you can hear me."

                        # Test based on model type
                        if model_id.startswith("anthropic"):
                            body = {
                                "prompt": f"\n\nHuman: {test_prompt}\n\nAssistant:",
                                "max_tokens_to_sample": 50,
                                "temperature": temperature
                            }
                        elif model_id.startswith("amazon.titan"):
                            body = {
                                "inputText": test_prompt,
                                "textGenerationConfig": {
                                    "maxTokenCount": 50,
                                    "temperature": temperature
                                }
                            }
                        else:
                            body = {"prompt": test_prompt}

                        import json
                        response = bedrock.invoke_model(
                            modelId=model_id,
                            body=json.dumps(body)
                        )

                        st.success(f"✅ Successfully connected to {model_id}!")
                        st.info("Model is responding correctly")

                    except Exception as e:
                        st.error(f"❌ Could not connect to Bedrock: {str(e)}")

        if save_clicked:
            with st.spinner("Saving Bedrock configuration..."):
                try:
                    # Update configuration
                    raw_settings['llm_models'] = raw_settings.get('llm_models', {})
                    raw_settings['llm_models']['bedrock'] = {
                        'model_id': model_id,
                        'region': region,
                        'max_tokens': max_tokens,
                        'temperature': temperature,
                        'stream': enable_streaming,
                        'enable_fallback': enable_fallback
                    }

                    # Save to file
                    import yaml
                    with open(settings_loader.settings_path, 'w') as f:
                        yaml.safe_dump(raw_settings, f, default_flow_style=False, indent=2)

                    st.success("✅ Bedrock configuration saved!")
                    st.info(f"Using model: {model_id}")
                    st.balloons()

                except Exception as e:
                    st.error(f"❌ Failed to save configuration: {str(e)}")

    # Quick Test Section
    st.markdown("---")
    st.markdown("### 🧪 Quick Model Test")

    test_prompt = st.text_area(
        "Test Prompt",
        value="Tell me a short joke about programming.",
        help="Enter a test prompt to send to the model"
    )

    if st.button("🚀 Send Test Prompt", type="primary"):
        if not has_aws_creds:
            st.error("❌ Please configure AWS credentials first")
        else:
            with st.spinner("Sending prompt to model..."):
                try:
                    import boto3
                    import json

                    bedrock = boto3.client(
                        'bedrock-runtime',
                        region_name=current_region,
                        aws_access_key_id=aws_creds.get('access_key_id'),
                        aws_secret_access_key=aws_creds.get('secret_access_key')
                    )

                    # Format request based on model
                    # Check if it's Claude 3 (needs Messages API)
                    if 'claude-3' in current_model_id.lower():
                        # Claude 3 Messages API format
                        body = {
                            "anthropic_version": "bedrock-2023-05-31",
                            "max_tokens": 500,
                            "temperature": current_temperature,
                            "messages": [
                                {"role": "user", "content": test_prompt}
                            ]
                        }
                    elif current_model_id.startswith("anthropic"):
                        # Legacy Claude format (for Claude v1/v2)
                        body = {
                            "prompt": f"\n\nHuman: {test_prompt}\n\nAssistant:",
                            "max_tokens_to_sample": 500,
                            "temperature": current_temperature
                        }
                    elif current_model_id.startswith("amazon.titan"):
                        body = {
                            "inputText": test_prompt,
                            "textGenerationConfig": {
                                "maxTokenCount": 500,
                                "temperature": current_temperature
                            }
                        }
                    elif current_model_id.startswith("meta.llama"):
                        # Llama models format
                        body = {
                            "prompt": test_prompt,
                            "max_gen_len": 500,
                            "temperature": current_temperature
                        }
                    else:
                        body = {"prompt": test_prompt, "max_tokens": 500}

                    response = bedrock.invoke_model(
                        modelId=current_model_id,
                        body=json.dumps(body)
                    )

                    # Parse response
                    response_body = json.loads(response['body'].read())

                    if 'claude-3' in current_model_id.lower():
                        # Claude 3 Messages API response format
                        content = response_body.get('content', [])
                        answer = content[0].get('text', '') if content else ''
                    elif current_model_id.startswith("anthropic"):
                        answer = response_body.get('completion', '')
                    elif current_model_id.startswith("amazon.titan"):
                        answer = response_body.get('results', [{}])[0].get('outputText', '')
                    elif current_model_id.startswith("meta.llama"):
                        answer = response_body.get('generation', '')
                    else:
                        answer = response_body.get('generation', response_body.get('completion', ''))

                    st.success("✅ Response received!")
                    st.markdown("**Model Response:**")
                    st.info(answer)

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    # Status summary
    st.markdown("---")
    st.markdown("### 📊 Configuration Status")

    col1, col2, col3 = st.columns(3)
    with col1:
        if has_aws_creds:
            st.success("✅ AWS Credentials")
        else:
            st.error("❌ AWS Credentials")

    with col2:
        if current_model_id:
            st.success("✅ Model Selected")
        else:
            st.error("❌ Model Selected")

    with col3:
        if current_region:
            st.success("✅ Region Set")
        else:
            st.error("❌ Region Set")

    if has_aws_creds and current_model_id and current_region:
        st.success("🎉 **AI Models are configured!** You can now use AI chat features.")
    else:
        st.warning("⚠️ **Complete the configuration above** to enable AI features.")