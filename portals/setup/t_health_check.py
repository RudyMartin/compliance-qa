"""
Tab 5: Health Check - Final system health verification
"""
import streamlit as st


def render(setup_service):
    """Step 5: Final health check."""
    st.header("Step 5️⃣: Final Health Check")
    st.markdown("**Let's make sure everything is working perfectly!**")

    if st.button("🏥 RUN COMPLETE HEALTH CHECK", type="primary", use_container_width=True):
        with st.spinner("Running comprehensive health check... This may take a minute..."):
            health_results = setup_service.final_health_check()
            # Store results in session state
            st.session_state["step5_results"] = health_results

    # Display results if they exist
    if "step5_results" in st.session_state:
        health_results = st.session_state["step5_results"]
        results = health_results["results"]
        status = health_results["overall_status"]

        st.markdown("### 💚 System Health Results:")

        # Overall status
        if status == "healthy":
            st.success("🎉 **EXCELLENT!** Your system is 100% healthy and ready!")
            st.balloons()
        elif status == "mostly_healthy":
            st.warning("⚠️ **Good!** Your system is mostly healthy with minor issues.")
        else:
            st.error("❌ **Issues found!** Some components need attention.")

        # Detailed results by category
        categories = {
            "System": ["python_version", "required_directories", "file_permissions"],
            "Database": ["database_connection", "postgresql_available"],
            "AWS": ["aws_credentials", "s3_access"],
            "MLflow": ["mlflow_configured", "mlflow_tracking"],
            "AI Models": ["bedrock_configured", "model_accessible"]
        }

        for category, checks in categories.items():
            with st.expander(f"**{category} Health**", expanded=True):
                category_results = {k: v for k, v in results.items() if k in checks}
                all_passed = all(category_results.values()) if category_results else False

                if all_passed:
                    st.success(f"✅ All {category} checks passed!")
                else:
                    for check, passed in category_results.items():
                        check_name = check.replace("_", " ").title()
                        if passed:
                            st.success(f"✅ {check_name}")
                        else:
                            st.error(f"❌ {check_name}")

        # Summary and recommendations
        st.info(f"📋 **Summary:** {health_results.get('summary', 'System health check complete')}")

        # Count issues
        total_checks = len(results)
        passed_checks = sum(1 for v in results.values() if v)
        failed_checks = total_checks - passed_checks

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Checks", total_checks)
        with col2:
            st.metric("✅ Passed", passed_checks)
        with col3:
            st.metric("❌ Failed", failed_checks)

        # Next steps
        if status == "healthy":
            st.success("🎯 **NEXT STEP:** Perfect! Go to the 'Explore Portals' tab to discover and launch AI tools!")
        else:
            st.warning("🎯 **NEXT STEP:** Review the failed checks above and fix any issues before exploring portals.")

        # Re-check button
        if st.button("🔄 Run Health Check Again", use_container_width=True):
            del st.session_state["step5_results"]
            st.rerun()


    # System info
    st.markdown("---")
    st.markdown("### 📊 System Information")

    with st.expander("View System Details"):
        import platform
        import sys
        import os

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Python Environment**")
            st.text(f"Version: {sys.version}")
            st.text(f"Platform: {platform.platform()}")
            st.text(f"Machine: {platform.machine()}")

        with col2:
            st.markdown("**System Paths**")
            st.text(f"Working Dir: {os.getcwd()}")
            st.text(f"Python Path: {sys.executable}")
            st.text(f"User: {os.getenv('USER', os.getenv('USERNAME', 'Unknown'))}")

    st.markdown("---")
    st.info("""
    ### 💡 **What This Health Check Does:**
    - Verifies all components from Steps 1-4 are properly configured
    - Ensures database, AWS, MLflow, and AI models are accessible
    - Provides a final confirmation before exploring portals
    - Run this after any configuration changes to verify everything still works

    **Tip:** Once everything is green ✅, proceed to the 'Explore Portals' tab to start using AI tools!
    """)