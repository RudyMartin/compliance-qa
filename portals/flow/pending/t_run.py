"""
Render Run Tab - Simple workflow execution with feedback
"""
import streamlit as st
import time
import uuid
from pathlib import Path


def extract_criteria_factors(criteria: dict) -> dict:
    """Extract optimizable factors from criteria configuration."""

    template_fields = criteria.get('template_fields', {})

    # Extract key factors for optimization tracking
    factors = {
        'confidence_threshold': template_fields.get('confidence_threshold', {}).get('value', 0.85),
        'model_type': template_fields.get('model_type', {}).get('value', 'unknown'),
        'validation_scope': template_fields.get('validation_scope', {}).get('value', 'unknown'),
        'regulatory_framework': template_fields.get('regulatory_framework', {}).get('value', 'unknown'),
        'query_length': len(criteria.get('query', '').split()),
        'context_length': len(criteria.get('context', '').split()),
        'required_sections_count': len(criteria.get('assessment_criteria', {}).get('documentation_completeness', {}).get('required_sections', [])),
        'scoring_weights_count': len(criteria.get('assessment_criteria', {}).get('documentation_completeness', {}).get('scoring_weights', {}))
    }

    return factors


def render_factor_analysis_dashboard(recent_runs):
    """Render factor analysis dashboard using MLflow data."""

    st.divider()
    st.subheader("🔍 Factor Performance Analysis")

    # Extract factor data from recent runs
    factor_data = []
    for run in recent_runs:
        if run.data.metrics.get('feedback_user_rating'):
            factor_record = {
                'workflow': run.data.params.get('workflow', 'unknown'),
                'criteria_confidence': float(run.data.params.get('criteria_confidence', 0.85)),
                'criteria_model_type': run.data.params.get('criteria_model_type', 'unknown'),
                'criteria_query_length': float(run.data.params.get('criteria_query_length', 0)),
                'process_time_ms': float(run.data.metrics.get('process_time_ms', 0)),
                'process_exploration_rate': float(run.data.metrics.get('process_exploration_rate', 0.1)),
                'response_length_chars': float(run.data.metrics.get('response_length_chars', 0)),
                'response_word_count': float(run.data.metrics.get('response_word_count', 0)),
                'response_signature': run.data.params.get('response_signature_used', 'unknown'),
                'feedback_rating': float(run.data.metrics.get('feedback_user_rating', 2)),
                'feedback_notes_length': float(run.data.metrics.get('feedback_improvement_notes_length', 0))
            }
            factor_data.append(factor_record)

    if len(factor_data) >= 2:
        import pandas as pd
        import numpy as np

        df = pd.DataFrame(factor_data)

        st.success(f"📊 Analyzing {len(factor_data)} runs with factor data")

        # Factor Performance Metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # Speed vs Quality
            fast_runs = df[df['process_time_ms'] < df['process_time_ms'].median()]
            slow_runs = df[df['process_time_ms'] >= df['process_time_ms'].median()]

            if len(fast_runs) > 0 and len(slow_runs) > 0:
                fast_avg = fast_runs['feedback_rating'].mean()
                slow_avg = slow_runs['feedback_rating'].mean()
                st.metric("Speed vs Quality",
                         f"Fast: {fast_avg:.1f} | Slow: {slow_avg:.1f}",
                         delta=f"{fast_avg - slow_avg:+.1f}")
            else:
                st.metric("Speed Analysis", "Need more data")

        with col2:
            # Confidence vs Quality
            high_conf = df[df['criteria_confidence'] > df['criteria_confidence'].median()]
            low_conf = df[df['criteria_confidence'] <= df['criteria_confidence'].median()]

            if len(high_conf) > 0 and len(low_conf) > 0:
                high_avg = high_conf['feedback_rating'].mean()
                low_avg = low_conf['feedback_rating'].mean()
                st.metric("Confidence vs Quality",
                         f"High: {high_avg:.1f} | Low: {low_avg:.1f}",
                         delta=f"{high_avg - low_avg:+.1f}")
            else:
                st.metric("Confidence Analysis", "Need more data")

        with col3:
            # Response Length vs Quality
            if df['response_length_chars'].std() > 0:
                length_quality_corr = df['response_length_chars'].corr(df['feedback_rating'])
                st.metric("Length-Quality Correlation",
                         f"{length_quality_corr:.2f}",
                         delta="Strong" if abs(length_quality_corr) > 0.5 else "Weak")
            else:
                st.metric("Length Correlation", "Need more variance")

        with col4:
            # Best Performing Workflow
            if 'workflow' in df.columns:
                workflow_performance = df.groupby('workflow')['feedback_rating'].mean()
                if len(workflow_performance) > 1:
                    best_workflow = workflow_performance.idxmax()
                    best_score = workflow_performance.max()
                    st.metric("Best Workflow",
                             best_workflow,
                             delta=f"{best_score:.1f} avg rating")
                else:
                    st.metric("Workflow Analysis", "Single workflow")

        # Detailed Factor Insights
        with st.expander("📈 Detailed Factor Insights", expanded=False):

            # Factor correlation matrix
            numeric_factors = df.select_dtypes(include=[np.number])
            if len(numeric_factors.columns) > 2:
                correlation_matrix = numeric_factors.corr()['feedback_rating'].sort_values(ascending=False)

                st.write("**Factor-Quality Correlations:**")
                for factor, correlation in correlation_matrix.items():
                    if factor != 'feedback_rating' and not np.isnan(correlation):
                        strength = "🔥 Strong" if abs(correlation) > 0.5 else "📊 Moderate" if abs(correlation) > 0.3 else "📉 Weak"
                        direction = "📈 Positive" if correlation > 0 else "📉 Negative"
                        st.write(f"- **{factor}**: {correlation:.2f} ({strength}, {direction})")

            # Recent trends
            if len(df) >= 5:
                recent_trend = df.tail(5)['feedback_rating'].mean() - df.head(5)['feedback_rating'].mean()
                trend_icon = "📈" if recent_trend > 0 else "📉" if recent_trend < 0 else "📊"
                st.write(f"**Recent Performance Trend**: {trend_icon} {recent_trend:+.2f} rating points")

            # Factor recommendations
            st.write("**Quick Factor Insights:**")

            # Speed recommendations
            if df['process_time_ms'].std() > 0:
                speed_quality_corr = df['process_time_ms'].corr(df['feedback_rating'])
                if speed_quality_corr < -0.3:
                    st.info("💡 **Speed matters**: Faster processing correlates with higher ratings")
                elif speed_quality_corr > 0.3:
                    st.info("💡 **Quality over speed**: Users prefer thorough analysis even if slower")

            # Confidence recommendations
            if df['criteria_confidence'].std() > 0:
                conf_quality_corr = df['criteria_confidence'].corr(df['feedback_rating'])
                if conf_quality_corr > 0.3:
                    st.info("💡 **Confidence boost**: Higher confidence thresholds improve satisfaction")
                elif conf_quality_corr < -0.3:
                    st.info("💡 **Confidence balance**: Lower confidence might allow more flexible responses")

    elif len(factor_data) == 1:
        st.info("📊 Found 1 run with factor data. Need at least 2 runs for comparative analysis.")

        # Show single run factors
        single_run = factor_data[0]
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Criteria Confidence", f"{single_run['criteria_confidence']:.2f}")
            st.metric("Process Time", f"{single_run['process_time_ms']:.0f}ms")

        with col2:
            st.metric("Response Length", f"{single_run['response_length_chars']} chars")
            st.metric("Response Words", f"{single_run['response_word_count']} words")

        with col3:
            st.metric("User Rating", f"{single_run['feedback_rating']:.1f}/3")
            st.metric("Feedback Notes", f"{single_run['feedback_notes_length']} chars")

    else:
        st.warning("📊 No factor data available yet. Complete a workflow and provide feedback to enable factor analysis!")
        st.info("💡 Factor analysis will show correlations between workflow parameters and user satisfaction.")


def render_run_tab(path_manager):
    """Render the simplified Run page with workflow selector, run button, output, feedback, and MLflow stats."""
    st.header("🚀 Run Workflow")
    st.markdown("**Simple workflow execution with feedback collection and performance tracking**")

    # Workflow selector
    st.subheader("Select Workflow")

    # Get available workflows from the projects directory
    workflows_dir = Path(path_manager.root_folder) / "domain" / "workflows" / "projects"
    available_workflows = []

    if workflows_dir.exists():
        for project_dir in workflows_dir.iterdir():
            if project_dir.is_dir():
                # Check if it has criteria or workflow definition
                criteria_path = project_dir / "criteria" / "criteria.json"
                if criteria_path.exists():
                    available_workflows.append(project_dir.name)

    if not available_workflows:
        st.warning("No workflows found. Create a workflow first in the 'Create' tab.")
        return

    selected_workflow = st.selectbox(
        "Choose workflow to run:",
        available_workflows,
        help="Select from your created workflows"
    )

    # Run button and execution
    col1, col2 = st.columns([1, 3])

    with col1:
        run_clicked = st.button("▶️ Run Workflow", type="primary")

    with col2:
        if st.button("📊 Show MLflow Stats"):
            st.session_state['show_mlflow_stats'] = True

    # MLflow Statistics Display
    if st.session_state.get('show_mlflow_stats', False):
        render_mlflow_stats()

    # Workflow execution
    if run_clicked and selected_workflow:
        execute_workflow(selected_workflow, workflows_dir)

    # Feedback Section
    if st.session_state.get('last_run'):
        render_feedback_section()

    # Show recent feedback summary
    if st.session_state.get('feedback_history'):
        render_feedback_summary()


def render_mlflow_stats():
    """Render MLflow statistics section using existing infrastructure."""
    st.subheader("📈 MLflow Statistics")
    with st.expander("Recent MLflow Runs", expanded=True):
        try:
            # Use proper hexagonal architecture pattern - access through infrastructure layer
            from infrastructure.services.enhanced_mlflow_service import get_enhanced_mlflow_service

            mlflow_service = get_enhanced_mlflow_service()

            if not mlflow_service.is_available():
                st.warning(f"MLflow not available: {mlflow_service.get_status()}")
                return

            st.success(f"✅ {mlflow_service.get_status()}")

            # Get real MLflow client and data through service layer
            client = mlflow_service.client
            if not client:
                st.error("Could not get MLflow client")
                return

            # Load MLflow data using service methods
            with st.spinner("Loading MLflow data..."):
                all_experiments = client.search_experiments()
                all_runs = []

                for exp in all_experiments:
                    runs = client.search_runs(
                        experiment_ids=[exp.experiment_id],
                        order_by=["start_time DESC"],
                        max_results=10
                    )
                    all_runs.extend(runs)

                # Sort by start time and get last 5
                all_runs.sort(key=lambda x: x.info.start_time, reverse=True)
                recent_runs = all_runs[:5]

            # Summary metrics from real data
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Experiments", len(all_experiments))
            with col2:
                st.metric("Total Runs", len(all_runs))
            with col3:
                success_count = sum(1 for run in recent_runs if run.info.status == "FINISHED")
                success_rate = f"{(success_count/len(recent_runs)*100):.0f}%" if recent_runs else "0%"
                st.metric("Recent Success Rate", success_rate)

            st.divider()

            # Recent runs table with real data
            if recent_runs:
                st.subheader("Recent Runs")
                import pandas as pd
                from datetime import datetime

                runs_data = []
                for run in recent_runs:
                    # Get experiment name
                    exp = client.get_experiment(run.info.experiment_id)

                    # Calculate duration
                    duration = "N/A"
                    if run.info.end_time and run.info.start_time:
                        duration_sec = (run.info.end_time - run.info.start_time) / 1000
                        duration = f"{duration_sec:.1f}s"

                    runs_data.append({
                        'Run ID': run.info.run_id[:8] + "...",
                        'Experiment': exp.name,
                        'Status': run.info.status,
                        'Duration': duration,
                        'Model': run.data.params.get('model', 'Unknown'),
                        'Start Time': datetime.fromtimestamp(run.info.start_time/1000).strftime("%Y-%m-%d %H:%M")
                    })

                df = pd.DataFrame(runs_data)
                st.dataframe(df, use_container_width=True)

                # Show additional metrics if available
                if recent_runs[0].data.metrics:
                    st.subheader("Latest Run Metrics")
                    latest_metrics = recent_runs[0].data.metrics

                    metric_cols = st.columns(min(4, len(latest_metrics)))
                    for i, (key, value) in enumerate(list(latest_metrics.items())[:4]):
                        with metric_cols[i]:
                            if 'token' in key.lower():
                                st.metric(key.replace('_', ' ').title(), f"{int(value)}")
                            elif 'time' in key.lower():
                                st.metric(key.replace('_', ' ').title(), f"{value:.1f}ms")
                            else:
                                st.metric(key.replace('_', ' ').title(), f"{value:.2f}")
            else:
                st.info("No recent runs found")

            # FACTOR ANALYSIS DASHBOARD
            render_factor_analysis_dashboard(recent_runs)

        except Exception as e:
            st.error(f"Error loading MLflow stats: {e}")
            st.info("MLflow integration requires proper configuration and credentials")


def execute_workflow(selected_workflow, workflows_dir):
    """Execute the selected workflow using real DSPy system."""
    st.subheader("🔄 Executing Workflow...")

    with st.spinner(f"Running workflow: {selected_workflow}"):
        try:
            # Load the actual workflow configuration
            workflow_path = workflows_dir / selected_workflow
            criteria_path = workflow_path / "criteria" / "criteria.json"

            if not criteria_path.exists():
                st.error(f"Workflow criteria not found: {criteria_path}")
                return

            # Load criteria configuration
            import json
            with open(criteria_path, 'r') as f:
                criteria = json.load(f)

            # Generate a run ID for tracking
            run_id = str(uuid.uuid4())

            # Execute using real DSPy/RL system
            from packages.tidyllm.knowledge_systems.adapters.dspy_rag.rl_dspy_adapter import get_rl_dspy_adapter

            rl_adapter = get_rl_dspy_adapter()

            # FACTOR TRACKING: Extract criteria factors
            criteria_factors = extract_criteria_factors(criteria)

            # Create request from criteria
            request = {
                'query': criteria.get('query', 'Process the workflow'),
                'context': criteria.get('context', ''),
                'workflow_id': selected_workflow,
                'run_id': run_id
            }

            # FACTOR TRACKING: Start MLflow run with factor logging
            try:
                from infrastructure.services.enhanced_mlflow_service import get_enhanced_mlflow_service
                mlflow_service = get_enhanced_mlflow_service()

                if mlflow_service.is_available():
                    import mlflow
                    with mlflow.start_run(run_name=f"workflow_{selected_workflow}_{run_id}"):
                        # 1. Log CRITERIA factors
                        mlflow.log_params({
                            "workflow": selected_workflow,
                            "criteria_confidence": criteria_factors.get('confidence_threshold', 0.85),
                            "criteria_model_type": criteria_factors.get('model_type', 'unknown'),
                            "criteria_validation_scope": criteria_factors.get('validation_scope', 'unknown'),
                            "criteria_query_length": criteria_factors.get('query_length', 0),
                            "criteria_context_length": criteria_factors.get('context_length', 0)
                        })

                        # 2. Execute and track PROCESS factors
                        start_time = time.time()
                        response = rl_adapter.query(request)
                        process_time = time.time() - start_time

                        # Log PROCESS factors
                        mlflow.log_metrics({
                            "process_time_ms": process_time * 1000,
                            "process_exploration_rate": getattr(rl_adapter, 'exploration_rate', 0.1),
                            "process_signature_count": len(getattr(rl_adapter, 'signature_performance', {}))
                        })

                        # 3. Log RESPONSE factors
                        response_text = response.get('response', '')
                        mlflow.log_metrics({
                            "response_length_chars": len(response_text),
                            "response_word_count": len(response_text.split()),
                        })

                        mlflow.log_params({
                            "response_signature_used": response.get('signature_used', 'unknown')
                        })

                        # Store MLflow run ID for feedback tracking
                        st.session_state[f'mlflow_run_id_{run_id}'] = mlflow.active_run().info.run_id

                else:
                    # Fallback: execute without MLflow
                    start_time = time.time()
                    response = rl_adapter.query(request)
                    process_time = time.time() - start_time

            except Exception as e:
                # Fallback: execute without factor tracking
                st.warning(f"Factor tracking unavailable: {e}")
                start_time = time.time()
                response = rl_adapter.query(request)
                process_time = time.time() - start_time

            # Store run info with real results
            st.session_state['last_run'] = {
                'workflow': selected_workflow,
                'run_id': run_id,
                'timestamp': time.time(),
                'query': request['query'],
                'response': response.get('response', ''),
                'signature_used': response.get('signature_used', 'unknown')
            }

            st.success("✅ Workflow execution completed!")

            # Show real output
            st.subheader("📋 Output")

            # Display the actual DSPy response
            with st.expander("DSPy Response", expanded=True):
                st.write("**Query:**", request['query'])
                st.write("**Response:**", response.get('response', 'No response'))
                st.write("**Signature Used:**", response.get('signature_used', 'Unknown'))
                if response.get('rl_mode'):
                    st.write("**RL Mode:**", response.get('rl_mode'))

            # Show technical details
            with st.expander("Technical Details"):
                st.json({
                    "workflow": selected_workflow,
                    "run_id": run_id,
                    "status": "completed",
                    "criteria": criteria,
                    "response_metadata": {
                        k: v for k, v in response.items()
                        if k not in ['response']  # Don't duplicate the response text
                    }
                })

        except ImportError:
            st.error("RL-DSPy system not available. Cannot execute real workflow.")
            return
        except Exception as e:
            st.error(f"Workflow execution failed: {e}")
            st.info("Check that the workflow has valid criteria.json and DSPy system is configured")
            return


def render_feedback_section():
    """Render the feedback collection section."""
    st.subheader("💬 Feedback")
    st.markdown("Help us improve the workflow by providing feedback:")

    last_run = st.session_state['last_run']

    # Feedback form
    with st.form("feedback_form", clear_on_submit=True):
        col1, col2 = st.columns([1, 2])

        with col1:
            rating = st.radio(
                "How would you rate the result?",
                options=[1, 2, 3],
                format_func=lambda x: {1: "👎 Poor", 2: "😐 OK", 3: "👍 Good"}[x],
                horizontal=True
            )

        with col2:
            improvement_notes = st.text_area(
                "What can we improve?",
                placeholder="Describe what could be better...",
                height=80
            )

        submit_feedback = st.form_submit_button("Submit Feedback", type="primary")

        if submit_feedback:
            try:
                # Store feedback using existing RL-DSPy system
                feedback_data = {
                    'run_id': last_run['run_id'],
                    'workflow': last_run['workflow'],
                    'rating': rating,
                    'improvement_notes': improvement_notes,
                    'timestamp': time.time()
                }

                # Store feedback in RL-DSPy system with real query/response data
                feedback_stored = False
                try:
                    from packages.tidyllm.knowledge_systems.adapters.dspy_rag.rl_dspy_adapter import get_rl_dspy_adapter

                    rl_adapter = get_rl_dspy_adapter()

                    # Create feedback record with actual query and response data
                    feedback_record = {
                        'query_id': last_run['run_id'],
                        'query_text': last_run.get('query', ''),
                        'response_text': last_run.get('response', ''),
                        'rating': rating,
                        'improvement_notes': improvement_notes,
                        'signature_used': last_run.get('signature_used', 'unknown'),
                        'workflow': last_run['workflow']
                    }

                    result = rl_adapter.collect_feedback(
                        query_id=last_run['run_id'],
                        rating=rating,
                        improvement_notes=improvement_notes
                    )

                    if result.get('success'):
                        feedback_stored = True
                        st.success(f"✅ Feedback stored in RL system! Rating: {rating}/3")
                        st.info(f"Feedback count: {result.get('feedback_count', 0)}")

                        # FACTOR TRACKING: Log FEEDBACK factors to MLflow
                        mlflow_run_id = st.session_state.get(f'mlflow_run_id_{last_run["run_id"]}')
                        if mlflow_run_id:
                            try:
                                import mlflow
                                with mlflow.start_run(run_id=mlflow_run_id):
                                    # 4. Log FEEDBACK factors
                                    mlflow.log_metrics({
                                        "feedback_user_rating": rating,
                                        "feedback_improvement_notes_length": len(improvement_notes),
                                        "feedback_timestamp": time.time()
                                    })

                                    mlflow.log_params({
                                        "feedback_has_improvement_notes": len(improvement_notes) > 0
                                    })

                                st.info("📊 Feedback factors logged to MLflow for analysis")
                            except Exception as e:
                                st.warning(f"MLflow feedback logging failed: {e}")

                        # Show RL learning status
                        if result.get('optimization_pending'):
                            st.info("🔄 RL optimization will trigger with collected feedback")
                            st.info(f"Signature '{last_run.get('signature_used', 'unknown')}' performance will be updated")

                        # Store feedback in PostgreSQL for long-term RL memory
                        try:
                            rl_adapter._store_feedback_in_postgres(
                                feedback_record,
                                (rating - 2) / 1.0  # Convert to reward scale
                            )
                            st.info("💾 Feedback stored in PostgreSQL for long-term RL learning")
                        except Exception as postgres_error:
                            st.warning(f"PostgreSQL storage failed: {postgres_error}")
                    else:
                        st.warning(f"RL feedback storage failed: {result.get('error', 'Unknown error')}")

                except ImportError as e:
                    st.warning("RL-DSPy adapter not available, using session storage")
                except Exception as e:
                    st.warning(f"RL feedback collection failed: {e}")
                    # Still show the error details for debugging
                    with st.expander("Error Details"):
                        st.error(str(e))

                # Fallback to session state storage
                if not feedback_stored:
                    if 'feedback_history' not in st.session_state:
                        st.session_state['feedback_history'] = []
                    st.session_state['feedback_history'].append(feedback_data)
                    st.success(f"✅ Feedback stored locally! Rating: {rating}/3")

                # Clear the last run to prevent duplicate feedback
                del st.session_state['last_run']
                st.rerun()

            except Exception as e:
                st.error(f"Error storing feedback: {e}")
                st.info("Feedback could not be stored")


def render_feedback_summary():
    """Render the feedback summary statistics."""
    st.subheader("📊 Feedback Summary")
    feedback_list = st.session_state['feedback_history']

    col1, col2, col3 = st.columns(3)
    with col1:
        avg_rating = sum(f['rating'] for f in feedback_list) / len(feedback_list)
        st.metric("Average Rating", f"{avg_rating:.1f}/3")

    with col2:
        st.metric("Total Feedback", len(feedback_list))

    with col3:
        good_feedback = len([f for f in feedback_list if f['rating'] >= 3])
        success_rate = (good_feedback / len(feedback_list)) * 100
        st.metric("Satisfaction Rate", f"{success_rate:.0f}%")