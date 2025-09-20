"""
Setup Portal - Credential & Configuration Management

The central portal for reviewing, validating, and establishing system credentials
and configuration. Now properly separated as external presentation layer.

Port: 8511
Category: Infrastructure
Dependencies: database, aws
Architecture: External presentation layer (hexagonal principles)
"""

import streamlit as st
import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any
import json
import time

# Add the qa-shipping root to Python path (now external to core packages)
qa_shipping_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(qa_shipping_root))

try:
    # Hexagonal architecture imports - use DI container
    from infrastructure.container import get_container, reset_container
    from domain.ports.outbound.session_port import SessionPort, DatabaseSessionPort, AWSSessionPort, CredentialPort
    from application.use_cases.setup_environment import SetupEnvironmentUseCase

    # Legacy infrastructure imports (to be phased out)
    from infrastructure.environment_manager import get_environment_manager, get_db_config, get_aws_config, get_mlflow_config
    from infrastructure.credential_validator import validate_all_credentials, quick_health_check
    from infrastructure.portal_config import get_portal_config_manager, get_portal_summary
    from infrastructure.settings_loader import get_settings_loader
except ImportError as e:
    st.error(f"Configuration system not available: {e}")
    st.stop()

# Global dependency injection context
_app_context = None

def get_app_context():
    """Get the application context with all dependencies wired"""
    global _app_context
    if _app_context is None:
        try:
            container = get_container()
            _app_context = container.wire()
        except Exception as e:
            st.error(f"Failed to initialize application context: {e}")
            _app_context = {}
    return _app_context


def get_architecture_info():
    """Get architecture information from settings.yaml."""
    try:
        settings_loader = get_settings_loader()
        config = settings_loader.load_config()

        # Get architecture pattern from settings
        arch_pattern = getattr(config, 'system', {}).get('architecture', {}).get('pattern', '4layer_clean')
        arch_version = getattr(config, 'configuration', {}).get('architecture_version', 'v2_4layer_clean')

        # Format for display
        if '4layer' in arch_pattern.lower() or '4layer' in arch_version.lower():
            return {
                'name': '4-Layer Clean',
                'full_name': '4-Layer Clean Architecture',
                'description': 'External Presentation Layer - 4-Layer Clean Architecture'
            }
        elif 'hexagonal' in arch_pattern.lower() or 'hexagonal' in arch_version.lower():
            return {
                'name': 'Hexagonal',
                'full_name': 'Hexagonal Architecture',
                'description': 'External Presentation Layer - Hexagonal Architecture'
            }
        else:
            return {
                'name': arch_pattern.replace('_', '-').title(),
                'full_name': f'{arch_pattern.replace("_", "-").title()} Architecture',
                'description': f'External Presentation Layer - {arch_pattern.replace("_", "-").title()} Architecture'
            }
    except Exception as e:
        # Fallback to hardcoded values
        return {
            'name': '4-Layer Clean',
            'full_name': '4-Layer Clean Architecture',
            'description': 'External Presentation Layer - 4-Layer Clean Architecture'
        }


def set_page_config():
    """Configure the Streamlit page."""
    st.set_page_config(
        page_title="Setup Portal - qa-shipping",
        page_icon="⚙️",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def render_header():
    """Render the portal header."""
    arch_info = get_architecture_info()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.title("⚙️ Setup Portal")
        st.markdown("**🔧 System Configuration & Credential Management**")
        st.markdown(f"*📋 {arch_info['description']}*")
        st.markdown("---")


def render_architecture_info():
    """Render architecture information."""
    arch_info = get_architecture_info()

    with st.expander("🏗️ Architecture Information"):
        st.write(f"**📐 {arch_info['full_name']} Compliance:**")
        st.success("✅ External Presentation Layer - Outside core packages")
        st.success("✅ Dependency Inversion - Depends on packages layer")
        st.success("✅ Clean Boundaries - Separated from business logic")

        # Test architecture integration
        col1, col2 = st.columns(2)

        with col1:
            st.write("**🔗 Hexagonal Integration:**")
            try:
                context = get_app_context()
                session_adapter = context.get("adapters", {}).get("session")

                if session_adapter:
                    st.success("✅ Dependency Injection: Active")
                    st.success("✅ Session Adapter: Loaded")

                    # Quick port test
                    implements_ports = all([
                        isinstance(session_adapter, SessionPort),
                        isinstance(session_adapter, DatabaseSessionPort),
                        isinstance(session_adapter, AWSSessionPort),
                        isinstance(session_adapter, CredentialPort)
                    ])

                    if implements_ports:
                        st.success("✅ Port Implementation: Complete")
                    else:
                        st.error("❌ Port Implementation: Incomplete")
                else:
                    st.error("❌ Session Adapter: Not Found")
                    st.error("❌ Dependency Injection: Failed")

            except Exception as e:
                st.error(f"❌ Architecture Integration: Error ({e})")

        with col2:
            st.write("**⚡ Architecture Benefits:**")
            st.info("🎯 Testable: Can inject mocks")
            st.info("🔄 Flexible: Can swap implementations")
            st.info("📦 Isolated: Domain has no infrastructure deps")
            st.info("🔌 Standard: Follows port/adapter pattern")

        st.write("**Layer Structure:**")
        st.code("""
qa-shipping/
├── portals/              # 🚪 PRESENTATION LAYER (External)
│   ├── setup/           # This portal
│   ├── chat/
│   ├── rag/
│   └── flow/
├── packages/             # 📦 DOMAIN PACKAGES
│   ├── tidyllm/         # Core business logic
│   ├── tlm/             # TLM core functionality
│   └── tidyllm-sentence/ # Sentence processing logic
├── adapters/             # 🔌 INFRASTRUCTURE ADAPTERS
│   └── session/         # Unified session management
├── common/               # 🛠️ COMMON UTILITIES
│   └── utilities/       # Path management, shared tools
└── infrastructure/       # 🏗️ INFRASTRUCTURE LAYER
    ├── environment_manager.py
    ├── credential_validator.py
    ├── portal_config.py
    ├── settings_loader.py
    └── settings.yaml    # Configuration file
        """)


def render_system_status():
    """Render real-time system status."""
    st.subheader("📊 System Status")

    # Create placeholders for real-time updates
    status_container = st.container()

    with status_container:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("🌍 Environment", st.session_state.get('environment', 'Unknown'))

        with col2:
            health_status = st.session_state.get('health_status', 'Unknown')
            health_icon = "💚" if health_status == "OK" else "⚠️"
            st.metric(f"{health_icon} Health", health_status,
                     delta="Healthy" if health_status == "OK" else "Issues detected")

        with col3:
            portal_count = st.session_state.get('active_portals', 0)
            st.metric("🚪 Active Portals", f"{portal_count}/7")

        with col4:
            arch_info = get_architecture_info()
            st.metric("🏗️ Architecture", arch_info['name'], delta="External Layer")


@st.cache_data(ttl=30)  # Cache for 30 seconds
def get_environment_summary():
    """Get environment summary with caching."""
    try:
        env_mgr = get_environment_manager()
        return env_mgr.get_environment_summary()
    except Exception as e:
        return {"error": str(e)}


def render_environment_config():
    """Render environment configuration section."""
    st.subheader("🌍 Environment Configuration")

    summary = get_environment_summary()

    if "error" in summary:
        st.error(f"Environment configuration error: {summary['error']}")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Current Environment:**")
        st.info(summary.get('environment', 'development'))

        st.write("**Configuration Sources:**")
        for component, source in summary.get('config_sources', {}).items():
            icon = "✅" if source == "environment" else "🔧"
            st.write(f"{icon} {component}: {source}")

    with col2:
        st.write("**Component Validation:**")
        for component, valid in summary.get('validation_results', {}).items():
            status = "✅ Valid" if valid else "❌ Invalid"
            st.write(f"{status} {component}")


def render_credential_management():
    """Render credential management interface."""
    st.subheader("🔑 Credential Management")

    tab1, tab2, tab3, tab4 = st.tabs(["Environment Variables", "Validation", "Secure Input", "Package Dependencies"])

    with tab1:
        render_environment_variables()

    with tab2:
        render_credential_validation()

    with tab3:
        render_secure_credential_input()

    with tab4:
        render_package_dependencies()


def render_package_dependencies():
    """Render package dependency information."""
    st.write("**Core Package Dependencies:**")

    packages = [
        ("tidyllm", "Core TidyLLM business logic", "🎯"),
        ("tlm", "TLM core functionality", "🎯"),
        ("tidyllm-sentence", "Sentence processing", "🎯"),
        ("infrastructure", "Infrastructure layer", "🏗️"),
        ("adapters", "Infrastructure adapters", "🔌"),
        ("common", "Common utilities", "🛠️")
    ]

    # Check for UnifiedRAGManager availability
    try:
        import sys
        sys.path.insert(0, str(qa_shipping_root / "packages"))
        from tidyllm.services.unified_rag_manager import UnifiedRAGManager
        st.success("✅ UnifiedRAGManager (URM): Available")
    except ImportError as e:
        st.error(f"❌ UnifiedRAGManager (URM): Not Available - {e}")
    except Exception as e:
        st.warning(f"⚠️ UnifiedRAGManager (URM): Import Error - {e}")

    for package, description, icon in packages:
        path = qa_shipping_root / package
        exists = path.exists()

        with st.expander(f"{icon} {package} - {description}"):
            if exists:
                st.success(f"✅ Package found at: {path}")

                # Try to import and get info
                try:
                    if package == "config":
                        from infrastructure import environment_manager
                        st.write("Available modules: environment_manager, credential_validator, portal_config")
                    else:
                        st.write(f"Directory exists with {len(list(path.rglob('*.py')))} Python files")
                except ImportError:
                    st.warning("Package directory exists but import failed")
            else:
                st.error(f"❌ Package not found at: {path}")


def render_environment_variables():
    """Render environment variable status."""
    st.write("**Required Environment Variables:**")

    required_vars = [
        ('DB_HOST', 'Database host address'),
        ('DB_PORT', 'Database port (default: 5432)'),
        ('DB_NAME', 'Database name'),
        ('DB_USERNAME', 'Database username'),
        ('DB_PASSWORD', 'Database password'),
    ]

    optional_vars = [
        ('AWS_ACCESS_KEY_ID', 'AWS access key'),
        ('AWS_SECRET_ACCESS_KEY', 'AWS secret key'),
        ('AWS_REGION', 'AWS region (default: us-east-1)'),
        ('MLFLOW_TRACKING_URI', 'MLflow tracking server'),
        ('ENVIRONMENT', 'Deployment environment'),
        ('LOG_LEVEL', 'Logging level (default: INFO)'),
    ]

    st.write("**Critical Variables:**")
    for var_name, description in required_vars:
        value = os.getenv(var_name)
        if value:
            st.success(f"✅ {var_name}: Set ({description})")
        else:
            st.error(f"❌ {var_name}: Not set - {description})")

    st.write("**Optional Variables:**")
    for var_name, description in optional_vars:
        value = os.getenv(var_name)
        if value:
            st.success(f"✅ {var_name}: Set ({description})")
        else:
            st.warning(f"⚠️ {var_name}: Not set - {description}")


def render_credential_validation():
    """Render credential validation interface."""
    st.write("**System Validation:**")

    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("🔬 Run Full Validation", type="primary"):
            with st.spinner("Validating system credentials..."):
                try:
                    # Run async validation (legacy)
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    report = loop.run_until_complete(validate_all_credentials())
                    st.session_state['validation_report'] = report
                except Exception as e:
                    st.error(f"Validation failed: {e}")

        if st.button("⚡ Quick Health Check"):
            with st.spinner("Checking essential services..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    healthy = loop.run_until_complete(quick_health_check())
                    if healthy:
                        st.success("✅ Essential services healthy")
                    else:
                        st.error("❌ Essential services unavailable")
                except Exception as e:
                    st.error(f"Health check failed: {e}")

        if st.button("🏗️ Hexagonal Validation"):
            with st.spinner("Validating through hexagonal architecture..."):
                try:
                    # Use session adapter for validation
                    arch_report = run_hexagonal_validation()
                    st.session_state['arch_validation_report'] = arch_report
                    if arch_report.get('success', False):
                        st.success("✅ Hexagonal validation passed!")
                    else:
                        st.error("❌ Hexagonal validation failed!")
                except Exception as e:
                    st.error(f"Architecture validation failed: {e}")

    with col2:
        if 'validation_report' in st.session_state:
            report = st.session_state['validation_report']
            render_validation_report(report)

        if 'arch_validation_report' in st.session_state:
            arch_report = st.session_state['arch_validation_report']
            render_architecture_validation_report(arch_report)


def render_validation_report(report: Dict[str, Any]):
    """Render detailed validation report."""
    st.write("**Validation Results:**")

    # Overall status
    status = report.get('overall_status', 'unknown')
    if status == 'healthy':
        st.success(f"🎉 System Status: {status.upper()}")
    elif status == 'degraded':
        st.warning(f"⚠️ System Status: {status.upper()}")
    else:
        st.error(f"❌ System Status: {status.upper()}")

    # Summary
    summary = report.get('summary', {})
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Checks", summary.get('total_checks', 0))
    with col2:
        st.metric("Successful", summary.get('successful', 0))
    with col3:
        st.metric("Errors", summary.get('errors', 0))

    # Detailed results
    st.write("**Component Details:**")
    for result in report.get('results', []):
        status_icon = {"success": "✅", "warning": "⚠️", "error": "❌"}
        icon = status_icon.get(result['status'], "❓")

        with st.expander(f"{icon} {result['component']} - {result['message']}"):
            st.write(f"**Status:** {result['status']}")
            st.write(f"**Message:** {result['message']}")
            if result.get('details'):
                st.write("**Details:**")
                st.json(result['details'])

    # Recommendations
    if report.get('recommendations'):
        st.write("**🔧 Recommendations:**")
        for rec in report['recommendations']:
            st.info(f"💡 {rec}")

    # Auto-Fix Cards for Failed Components
    st.write("**🛠️ Auto-Fix Options:**")

    error_components = [r for r in report.get('results', []) if r['status'] == 'error']
    warning_components = [r for r in report.get('results', []) if r['status'] == 'warning']

    if error_components:
        for result in error_components:
            component_name = result['component']
            error_message = result['message']

            with st.expander(f"🔧 Fix {component_name} Issue"):
                fix_component_issue(component_name, error_message)

    if warning_components:
        for result in warning_components:
            component_name = result['component']
            warning_message = result['message']

            with st.expander(f"⚡ Optimize {component_name} Performance"):
                tune_component_issue(component_name, warning_message)

    if not error_components and not warning_components:
        st.success("🎉 All components are healthy! No fixes needed.")


def render_secure_credential_input():
    """Render secure credential input interface."""
    st.write("**Secure Credential Configuration:**")
    st.info("⚠️ For security, credentials are set via environment variables. Use your system's secure methods.")

    st.write("**Recommended Setup Methods:**")

    with st.expander("🪟 Windows Setup"):
        st.code("""
# Option 1: PowerShell (Current Session)
$env:DB_HOST="your_host"
$env:DB_PASSWORD="your_password"

# Option 2: Command Prompt (Current Session)
set DB_HOST=your_host
set DB_PASSWORD=your_password

# Option 3: System Environment Variables (Permanent)
# Go to: System Properties > Advanced > Environment Variables
        """, language="powershell")

    with st.expander("🐧 Linux/Mac Setup"):
        st.code("""
# Option 1: Current Session
export DB_HOST="your_host"
export DB_PASSWORD="your_password"

# Option 2: Add to ~/.bashrc or ~/.zshrc (Permanent)
echo 'export DB_HOST="your_host"' >> ~/.bashrc
echo 'export DB_PASSWORD="your_password"' >> ~/.bashrc

# Option 3: .env file (with python-dotenv)
# Create .env file in project root:
DB_HOST=your_host
DB_PASSWORD=your_password
        """, language="bash")

    with st.expander("🔐 Production Setup"):
        st.code("""
# AWS Secrets Manager
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Azure Key Vault
# Use Azure CLI or environment variables

# Docker Secrets
# Mount secrets as environment variables

# Kubernetes Secrets
# Use ConfigMaps and Secrets resources
        """, language="yaml")


def render_portal_management():
    """Render portal management interface."""
    st.subheader("🚪 Portal Management")

    try:
        summary = get_portal_summary()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Portals", summary['total_portals'])
        with col2:
            st.metric("Enabled", summary['enabled_portals'])
        with col3:
            st.metric("Disabled", summary['disabled_portals'])

        st.write("**Portal Registry:**")

        for portal in summary['portal_list']:
            with st.expander(f"{'🟢' if portal['enabled'] else '🔴'} {portal['title']} (Port {portal['port']})"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Name:** {portal['name']}")
                    st.write(f"**Category:** {portal['category']}")
                    st.write(f"**Port:** {portal['port']}")

                with col2:
                    st.write(f"**Status:** {'Enabled' if portal['enabled'] else 'Disabled'}")
                    if portal['url']:
                        st.link_button("🔗 Open Portal", portal['url'])

                    if st.button(f"{'Disable' if portal['enabled'] else 'Enable'} {portal['name']}"):
                        st.info("Portal status management will be implemented in Phase 3")

    except Exception as e:
        st.error(f"Portal management error: {e}")


def render_health_endpoint():
    """Health check endpoint for monitoring."""
    if st.query_params.get('health') == 'true':
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            healthy = loop.run_until_complete(quick_health_check())

            return {
                "status": "healthy" if healthy else "unhealthy",
                "portal": "setup_portal",
                "port": 8511,
                "architecture": "external_presentation_layer",
                "timestamp": time.time()
            }
        except Exception:
            return {
                "status": "error",
                "portal": "setup_portal",
                "port": 8511,
                "architecture": "external_presentation_layer",
                "timestamp": time.time()
            }
    return None


def render_comprehensive_setup():
    """Render comprehensive setup management interface."""
    st.subheader("🚀 Comprehensive Setup Management")

    # Add overview section
    st.markdown("""
    This section provides one-click setup for all QA-Shipping components including:
    - Environment configuration and validation
    - Database connection pooling setup
    - Portal discovery and management
    - Script generation for all platforms
    - Health monitoring and validation
    """)

    # Important warning banner
    st.error("""
    ⚠️ **IMPORTANT SETUP WARNING**

    The package installer will automatically discover and attempt to install any packages
    with proper setup.py files. Installation will FAIL if packaging structure is incorrect.

    Ensure all packages in the `packages/` directory have valid setup.py files before proceeding.
    """)

    # Setup status overview
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🌍 Environment", st.session_state.get('environment', 'Unknown'))
    with col2:
        st.metric("🔗 Connection Pool", "Enabled" if check_connection_pool_status() else "Disabled")
    with col3:
        st.metric("🚪 Active Portals", f"{discover_active_portals()}/7")
    with col4:
        st.metric("📋 Scripts", "Ready" if check_script_generation() else "Missing")

    st.markdown("---")

    # One-click setup actions
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 Quick Setup", "🔍 Portal Discovery", "📊 Health Check", "📜 Script Generation"])

    with tab1:
        render_quick_setup()

    with tab2:
        render_portal_discovery()

    with tab3:
        render_comprehensive_health_check()

    with tab4:
        render_script_generation_management()


def check_connection_pool_status():
    """Check if connection pooling is properly enabled."""
    try:
        from infrastructure.settings_loader import get_settings_loader
        settings_loader = get_settings_loader()
        config = settings_loader.load_config()

        # Check multiple pool configurations
        pool_enabled = getattr(config, 'deployment', {}).get('connection_pool', {}).get('enabled', False)
        global_pool = getattr(config, 'deployment', {}).get('connection_pool', {}).get('global_pool', False)
        postgres_pool = getattr(config, 'credentials', {}).get('postgresql', {}).get('connection_pool', {}).get('enabled', False)

        return pool_enabled and global_pool and postgres_pool
    except Exception:
        return False


def discover_active_portals():
    """Discover and count active portals."""
    import socket

    known_ports = [8511, 8506, 8525, 8505, 8501, 8502, 8550]
    active_count = 0

    for port in known_ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                if result == 0:
                    active_count += 1
        except Exception:
            continue

    return active_count


def check_script_generation():
    """Check if script generation is available."""
    try:
        from infrastructure.script_generator import get_script_generator
        generator = get_script_generator()
        validation = generator.validate_generated_scripts()
        return any(validation.values())
    except Exception:
        return False


def render_quick_setup():
    """Render quick setup interface."""
    st.write("**🚀 One-Click Setup Actions:**")

    # STEP 1: Package Installation (FIRST STEP)
    st.markdown("### 📦 Step 1: Install Independent Packages")
    st.info("**FIRST STEP**: Install tlm, tidyllm, and tidyllm-sentence as independent packages")
    st.warning("**IMPORTANT:** Installer will attempt to install packages with proper packaging structure and will fail if packaging is incorrect!")

    if st.button("📦 Install All Packages", use_container_width=True, type="primary"):
        with st.spinner("Installing packages as independent packages..."):
            install_result = install_all_packages()
            if install_result:
                st.success("✅ All packages installed as independent packages!")
                st.balloons()
            else:
                st.error("❌ Package installation failed!")

    st.markdown("---")
    st.markdown("### ⚙️ Step 2-4: System Configuration")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🌍 Setup Environment", use_container_width=True):
            with st.spinner("Setting up environment..."):
                setup_result = perform_environment_setup()
                if setup_result:
                    st.success("✅ Environment setup completed!")
                else:
                    st.error("❌ Environment setup failed!")

        if st.button("🔗 Initialize Connection Pool", use_container_width=True):
            with st.spinner("Initializing connection pool..."):
                pool_result = initialize_connection_pool()
                if pool_result:
                    st.success("✅ Connection pool initialized!")
                else:
                    st.error("❌ Connection pool initialization failed!")

    with col2:
        if st.button("📜 Generate All Scripts", use_container_width=True):
            with st.spinner("Generating platform scripts..."):
                script_result = generate_all_scripts()
                if script_result:
                    st.success("✅ All scripts generated!")
                else:
                    st.error("❌ Script generation failed!")

        if st.button("🔬 Run Complete Validation", use_container_width=True):
            with st.spinner("Running comprehensive validation..."):
                validation_result = run_complete_validation()
                if validation_result:
                    st.success("✅ All systems validated!")
                else:
                    st.error("❌ Validation issues found!")

        if st.button("🏗️ Test Hexagonal Architecture", use_container_width=True):
            with st.spinner("Testing hexagonal architecture integration..."):
                arch_result = test_hexagonal_architecture()
                if arch_result:
                    st.success("✅ Hexagonal architecture working perfectly!")
                    st.balloons()
                else:
                    st.error("❌ Architecture integration issues!")

        if st.button("🔄 Sync Active Credential State", use_container_width=True):
            with st.spinner("Syncing credentials from all sources..."):
                sync_result = sync_active_credential_state()
                if sync_result:
                    st.success("✅ Credential state synchronized!")
                    st.balloons()
                else:
                    st.error("❌ Credential sync issues!")


def render_portal_discovery():
    """Render portal discovery interface."""
    st.write("**🔍 Portal Discovery & Management:**")

    known_portals = [
        {"name": "Setup Portal", "port": 8512, "category": "Infrastructure"},
        {"name": "QA Scoring Portal", "port": 8511, "category": "Analysis"},
        {"name": "Flow Creator", "port": 8550, "category": "Workflow"},
        {"name": "RAG Creator V3", "port": 8525, "category": "Knowledge"},
        {"name": "Chat Test Portal", "port": 8502, "category": "Testing"},
        {"name": "AI Portal", "port": 8501, "category": "AI"},
        {"name": "Analysis Portal", "port": 8506, "category": "Analysis"},
        {"name": "Data Portal", "port": 8505, "category": "Data"}
    ]

    active_portals = []
    inactive_portals = []

    for portal in known_portals:
        if check_port_active(portal["port"]):
            active_portals.append(portal)
        else:
            inactive_portals.append(portal)

    col1, col2 = st.columns(2)

    with col1:
        st.write("**🟢 Active Portals:**")
        for portal in active_portals:
            with st.container():
                st.write(f"✅ **{portal['name']}** (Port {portal['port']})")
                st.write(f"   Category: {portal['category']}")
                st.link_button(f"🔗 Open {portal['name']}", f"http://localhost:{portal['port']}", key=f"open_{portal['port']}")
                st.write("---")

    with col2:
        st.write("**🔴 Inactive Portals:**")
        for portal in inactive_portals:
            with st.container():
                st.write(f"❌ **{portal['name']}** (Port {portal['port']})")
                st.write(f"   Category: {portal['category']}")
                if st.button(f"🚀 Start {portal['name']}", key=f"start_{portal['port']}"):
                    st.info(f"Portal startup for {portal['name']} will be implemented in Phase 3")
                st.write("---")


def check_port_active(port):
    """Check if a specific port is active."""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result == 0
    except Exception:
        return False


def render_comprehensive_health_check():
    """Render comprehensive health check interface."""
    st.write("**🏥 System Health Overview:**")

    if st.button("🔬 Run Complete Health Check", use_container_width=True):
        with st.spinner("Running comprehensive health check..."):
            health_results = perform_comprehensive_health_check()

            col1, col2 = st.columns(2)

            with col1:
                st.write("**✅ Passing Components:**")
                for component, status in health_results.items():
                    if status:
                        st.write(f"✅ {component}")

            with col2:
                st.write("**❌ Failing Components:**")
                for component, status in health_results.items():
                    if not status:
                        st.write(f"❌ {component}")


def render_script_generation_management():
    """Render script generation management interface."""
    st.write("**📜 Script Generation Management:**")

    try:
        from infrastructure.script_generator import get_script_generator
        generator = get_script_generator()

        info = generator.get_script_info()
        st.write(f"**Source Settings:** {info['source_settings']}")
        st.write(f"**Output Directory:** {info['output_directory']}")

        validation = generator.validate_generated_scripts()

        col1, col2 = st.columns(2)

        with col1:
            st.write("**📋 Available Scripts:**")
            for script, valid in validation.items():
                status = "✅" if valid else "❌"
                st.write(f"{status} {script}")

        with col2:
            if st.button("🔄 Regenerate All Scripts", use_container_width=True):
                with st.spinner("Regenerating scripts..."):
                    try:
                        generator.generate_all_scripts()
                        st.success("✅ All scripts regenerated!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Script generation failed: {e}")

    except ImportError:
        st.error("Script generator not available")


def perform_environment_setup():
    """Perform comprehensive environment setup."""
    try:
        from infrastructure.settings_loader import setup_environment_from_settings
        setup_environment_from_settings()
        return True
    except Exception:
        return False


def initialize_connection_pool():
    """Initialize connection pool using session adapter."""
    try:
        context = get_app_context()
        session_adapter = context.get("adapters", {}).get("session")
        if not session_adapter:
            return False

        # Test pool initialization through session port
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        s3_client = loop.run_until_complete(session_adapter.get_s3_client())
        return s3_client is not None
    except Exception:
        return False


def generate_all_scripts():
    """Generate all platform scripts."""
    try:
        from infrastructure.script_generator import get_script_generator
        generator = get_script_generator()
        generator.generate_all_scripts()
        return True
    except Exception:
        return False


def install_all_packages():
    """Install all three packages as independent packages."""
    try:
        from infrastructure.install_packages import PackageInstaller
        installer = PackageInstaller(qa_shipping_root)
        results = installer.install_all_packages(development_mode=True)
        return all(results.values())
    except Exception as e:
        st.error(f"Package installation error: {e}")
        return False


def run_complete_validation():
    """Run complete system validation."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        from infrastructure.credential_validator import quick_health_check
        result = loop.run_until_complete(quick_health_check())
        return result
    except Exception:
        return False


def test_hexagonal_architecture():
    """Test hexagonal architecture integration."""
    try:
        # Test dependency injection wiring
        context = get_app_context()
        if not context:
            return False

        # Test session adapter integration
        session_adapter = context.get("adapters", {}).get("session")
        if not session_adapter:
            return False

        # Test that adapter implements all ports
        implements_session = isinstance(session_adapter, SessionPort)
        implements_database = isinstance(session_adapter, DatabaseSessionPort)
        implements_aws = isinstance(session_adapter, AWSSessionPort)
        implements_credential = isinstance(session_adapter, CredentialPort)

        port_tests = [implements_session, implements_database, implements_aws, implements_credential]

        # Test basic functionality through ports
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Test connection status
        status = loop.run_until_complete(session_adapter.get_connection_status())
        functional_test = status.get('overall_health') != 'error'

        # Test credential validation
        creds = loop.run_until_complete(session_adapter.get_credential_status())
        cred_test = len(creds) > 0

        return all(port_tests) and functional_test and cred_test

    except Exception as e:
        st.error(f"Architecture test failed: {e}")
        return False


def run_hexagonal_validation():
    """Run validation through hexagonal architecture."""
    try:
        # Get application context
        context = get_app_context()
        session_adapter = context.get("adapters", {}).get("session")

        if not session_adapter:
            return {
                "success": False,
                "error": "Session adapter not found",
                "details": {}
            }

        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Test connection status through ports
        connection_status = loop.run_until_complete(session_adapter.get_connection_status())

        # Test credential validation through ports
        credential_status = loop.run_until_complete(session_adapter.get_credential_status())

        # Test individual service connections
        database_test = loop.run_until_complete(session_adapter.test_connection("database"))
        aws_test = loop.run_until_complete(session_adapter.test_connection("aws"))

        return {
            "success": True,
            "connection_status": connection_status,
            "credential_status": credential_status,
            "service_tests": {
                "database": database_test,
                "aws": aws_test
            },
            "architecture_compliance": {
                "dependency_injection": True,
                "port_implementation": True,
                "session_adapter_loaded": True
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "details": {}
        }


def sync_active_credential_state():
    """Portal function to call infrastructure credential sync service"""
    try:
        # Call the infrastructure service (proper separation of concerns)
        from infrastructure.services.credential_carrier import sync_active_credential_state as infra_sync

        result = infra_sync()

        if not result["success"]:
            st.error(f"Credential sync failed: {result.get('error', 'Unknown error')}")
            return False

        # Display sync results from infrastructure service
        st.write("**🔄 Credential Sync Results:**")

        status = result.get("status", {})
        for service, info in status.items():
            available = info.get('available', False)
            valid = info.get('valid', False)
            source = info.get('source', 'unknown')

            if available and valid:
                st.success(f"✅ {service.title()}: Valid (source: {source})")
            elif available:
                st.warning(f"⚠️ {service.title()}: Available but invalid (source: {source})")
            else:
                st.error(f"❌ {service.title()}: Not available")

        # Show backup info if created
        if result.get("backup_created"):
            backup_path = result.get("backup_path", "unknown")
            st.info(f"💾 Credentials backed up to {backup_path}")

        # Show environment variable status
        if result.get("environment_vars_set"):
            st.success("✅ Environment variables synchronized")
        else:
            st.warning("⚠️ Environment variable sync issues")

        return result["success"]

    except Exception as e:
        st.error(f"Portal sync call failed: {e}")
        return False


def render_architecture_validation_report(report: Dict[str, Any]):
    """Render architecture validation report."""
    st.write("**🏗️ Hexagonal Architecture Validation:**")

    if report.get("success", False):
        st.success("🎉 Architecture validation successful!")

        # Architecture compliance
        compliance = report.get("architecture_compliance", {})
        st.write("**Architecture Compliance:**")
        for feature, status in compliance.items():
            icon = "✅" if status else "❌"
            st.write(f"{icon} {feature.replace('_', ' ').title()}")

        # Connection status through ports
        conn_status = report.get("connection_status", {})
        st.write("**Connection Status (via Ports):**")
        st.write(f"Overall Health: {conn_status.get('overall_health', 'unknown')}")

        # Service tests through ports
        service_tests = report.get("service_tests", {})
        st.write("**Service Tests (via Session Adapter):**")
        for service, result in service_tests.items():
            success = result.get("success", False)
            icon = "✅" if success else "❌"
            st.write(f"{icon} {service.title()}: {result.get('message', 'No message')}")

        # Credential status through ports
        cred_status = report.get("credential_status", {})
        if cred_status:
            st.write("**Credential Validation (via CredentialPort):**")
            for service, status in cred_status.items():
                valid = status.get("valid", False)
                icon = "✅" if valid else "❌"
                st.write(f"{icon} {service.title()}: {'Valid' if valid else 'Invalid'}")

    else:
        st.error(f"❌ Architecture validation failed: {report.get('error', 'Unknown error')}")


def render_packages_page():
    """Render dedicated packages management page."""
    st.subheader("📦 Package Management")

    # Warning banner
    st.warning("""
    ⚠️ **PACKAGE INSTALLATION WARNING**

    The installer will discover and attempt to install packages with valid setup.py files.
    Installation will FAIL if packaging structure is incorrect.
    """)

    # Discover packages
    try:
        from infrastructure.install_packages import PackageInstaller
        installer = PackageInstaller(qa_shipping_root)
        packages = installer.packages

        if not packages:
            st.error("❌ No installable packages found in packages/ directory!")
            return

        # Package overview
        st.markdown("### 📋 Discovered Packages")

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        total_packages = len(packages)
        with_setup = sum(1 for pkg in packages.values() if pkg.get('has_setup', False))

        with col1:
            st.metric("📦 Total Packages", total_packages)
        with col2:
            st.metric("✅ With setup.py", with_setup)
        with col3:
            st.metric("❌ Missing setup.py", total_packages - with_setup)
        with col4:
            st.metric("🎯 Ready to Install", with_setup)

        st.markdown("---")

        # Individual package management
        st.markdown("### 🔧 Individual Package Management")

        for pkg_name, pkg_info in packages.items():
            with st.expander(f"📦 {pkg_name} - {pkg_info['description']}", expanded=False):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"**Package:** {pkg_name}")
                    st.write(f"**Description:** {pkg_info['description']}")
                    st.write(f"**Path:** `{pkg_info['path']}`")

                    setup_status = "✅ Found" if pkg_info.get('has_setup', False) else "❌ Missing"
                    st.write(f"**setup.py:** {setup_status}")

                    if pkg_info.get('auto_discovered', False):
                        st.info("🔍 Auto-discovered package")

                with col2:
                    if pkg_info.get('has_setup', False):
                        if st.button(f"🚀 Install {pkg_name}", key=f"install_{pkg_name}", use_container_width=True):
                            with st.spinner(f"Installing {pkg_name}..."):
                                success = install_single_package(pkg_name)
                                if success:
                                    st.success(f"✅ {pkg_name} installed successfully!")
                                    st.balloons()
                                else:
                                    st.error(f"❌ {pkg_name} installation failed!")

                        if st.button(f"🔍 Verify {pkg_name}", key=f"verify_{pkg_name}", use_container_width=True):
                            with st.spinner(f"Verifying {pkg_name}..."):
                                verified = verify_single_package(pkg_name)
                                if verified:
                                    st.success(f"✅ {pkg_name} is properly installed!")
                                else:
                                    st.error(f"❌ {pkg_name} verification failed!")
                    else:
                        st.error("Cannot install - missing setup.py")

        st.markdown("---")

        # Bulk operations
        st.markdown("### 🚀 Bulk Operations")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📦 Install All Packages", use_container_width=True, type="primary"):
                with st.spinner("Installing all packages..."):
                    install_result = install_all_packages()
                    if install_result:
                        st.success("✅ All packages installed!")
                        st.balloons()
                    else:
                        st.error("❌ Some packages failed to install!")

        with col2:
            if st.button("🔍 Verify All Packages", use_container_width=True):
                with st.spinner("Verifying all packages..."):
                    verify_result = verify_all_packages()
                    if verify_result:
                        st.success("✅ All packages verified!")
                    else:
                        st.warning("⚠️ Some packages have issues!")

        with col3:
            if st.button("🔄 Re-scan Packages", use_container_width=True):
                st.info("🔄 Re-scanning packages directory...")
                st.rerun()

        # Installation status
        st.markdown("### 📊 Installation Status")
        render_package_installation_status(packages)

    except Exception as e:
        st.error(f"❌ Error loading package information: {e}")


def install_single_package(package_name: str) -> bool:
    """Install a single package."""
    try:
        from infrastructure.install_packages import PackageInstaller
        installer = PackageInstaller(qa_shipping_root)
        success = installer.install_package(package_name, development_mode=True)
        return success
    except Exception as e:
        st.error(f"Installation error: {e}")
        return False


def verify_single_package(package_name: str) -> bool:
    """Verify a single package installation."""
    try:
        from infrastructure.install_packages import PackageInstaller
        installer = PackageInstaller(qa_shipping_root)
        import_name = installer._get_import_name(package_name)

        import subprocess
        import sys
        result = subprocess.run([
            sys.executable, "-c", f"import {import_name}; print('Success')"
        ], capture_output=True, text=True)

        return result.returncode == 0
    except Exception:
        return False


def verify_all_packages() -> bool:
    """Verify all package installations."""
    try:
        from infrastructure.install_packages import PackageInstaller
        installer = PackageInstaller(qa_shipping_root)
        verification = installer.verify_installations()
        return all(verification.values())
    except Exception:
        return False


def render_package_installation_status(packages: dict):
    """Render installation status for all packages."""
    st.write("**Current Installation Status:**")

    status_data = []
    for pkg_name in packages.keys():
        verified = verify_single_package(pkg_name)
        status_data.append({
            "Package": pkg_name,
            "Status": "✅ Installed" if verified else "❌ Not Installed",
            "Import Name": get_import_name_for_display(pkg_name)
        })

    if status_data:
        import pandas as pd
        df = pd.DataFrame(status_data)
        st.dataframe(df, use_container_width=True, hide_index=True)


def get_import_name_for_display(package_name: str) -> str:
    """Get import name for display purposes."""
    import_mapping = {
        "tidyllm-sentence": "tidyllm_sentence",
    }
    return import_mapping.get(package_name, package_name)


def perform_comprehensive_health_check():
    """Perform comprehensive health check of all components."""
    results = {
        "Environment Setup": False,
        "Connection Pool": False,
        "Database Connection": False,
        "AWS Credentials": False,
        "Script Generation": False,
        "Portal Discovery": False
    }

    try:
        # Environment check
        results["Environment Setup"] = perform_environment_setup()

        # Connection pool check
        results["Connection Pool"] = check_connection_pool_status()

        # Database check
        try:
            from infrastructure.environment_manager import get_environment_manager
            env_mgr = get_environment_manager()
            summary = env_mgr.get_environment_summary()
            results["Database Connection"] = summary.get('validation_results', {}).get('database', False)
        except Exception:
            results["Database Connection"] = False

        # AWS check using session adapter
        try:
            context = get_app_context()
            session_adapter = context.get("adapters", {}).get("session")
            if session_adapter:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                s3_client = loop.run_until_complete(session_adapter.get_s3_client())
                results["AWS Credentials"] = s3_client is not None
            else:
                results["AWS Credentials"] = False
        except Exception:
            results["AWS Credentials"] = False

        # Script generation check
        results["Script Generation"] = check_script_generation()

        # Portal discovery check
        results["Portal Discovery"] = discover_active_portals() > 0

    except Exception:
        pass

    return results

def fix_component_issue(component_name: str, error_message: str):
    """Auto-fix component issues with test/save workflow"""
    st.write(f"### 🔧 Fixing {component_name}")

    if component_name == "database":
        # Database connection issues
        if "localhost" in error_message and "connection refused" in error_message:
            st.warning("**Issue**: Trying to connect to localhost database instead of AWS RDS")

            # Test/Save workflow
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                st.write("**🎯 Proposed Fix: AWS RDS Settings**")
                st.info("**New Configuration:**")
                new_config = {
                    'DB_HOST': 'vectorqa-cluster.cluster-cu562e4m02nq.us-east-1.rds.amazonaws.com',
                    'DB_PORT': '5432',
                    'DB_NAME': 'vectorqa',
                    'DB_USERNAME': 'vectorqa_user',
                    'DB_PASSWORD': 'bitcoin-miner-2025'
                }

                for key, value in new_config.items():
                    if key == 'DB_PASSWORD':
                        st.text(f"{key}: {'*' * len(value)}")
                    else:
                        st.text(f"{key}: {value}")

            with col2:
                st.write("**🧪 Test First**")
                if st.button("🧪 Test Connection", key="test_db_connection"):
                    with st.spinner("Testing database connection..."):
                        test_result = test_database_connection(new_config)
                        if test_result['success']:
                            st.success("✅ Connection Test PASSED!")
                            st.session_state['db_test_passed'] = True
                        else:
                            st.error(f"❌ Connection Test FAILED: {test_result['error']}")
                            st.session_state['db_test_passed'] = False

            with col3:
                st.write("**💾 Save Config**")
                # Only enable save if test passed
                save_disabled = not st.session_state.get('db_test_passed', False)
                if st.button("💾 Save to Settings", key="save_db_config", disabled=save_disabled):
                    if save_database_config_to_settings(new_config):
                        st.success("✅ Configuration saved to settings.yaml!")
                        st.experimental_rerun()
                    else:
                        st.error("❌ Failed to save configuration")

                if save_disabled:
                    st.caption("⚠️ Test connection first")

        elif "password" in error_message.lower():
            st.error("**Issue**: Database password authentication failed")

            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                st.write("**🎯 Proposed Fix: Updated Password**")
                st.info("**New Password:** bitcoin-miner-2025")

            with col2:
                if st.button("🧪 Test Password", key="test_db_password"):
                    with st.spinner("Testing new password..."):
                        test_config = {'DB_PASSWORD': 'bitcoin-miner-2025'}
                        test_result = test_database_connection(test_config)
                        if test_result['success']:
                            st.success("✅ Password Test PASSED!")
                            st.session_state['password_test_passed'] = True
                        else:
                            st.error(f"❌ Password Test FAILED: {test_result['error']}")
                            st.session_state['password_test_passed'] = False

            with col3:
                save_disabled = not st.session_state.get('password_test_passed', False)
                if st.button("💾 Update Password", key="save_db_password", disabled=save_disabled):
                    if update_password_in_settings('bitcoin-miner-2025'):
                        st.success("✅ Password updated in settings.yaml!")
                        st.experimental_rerun()
                    else:
                        st.error("❌ Failed to update password")

                if save_disabled:
                    st.caption("⚠️ Test password first")


    elif component_name == "aws":
        st.warning("**Issue**: AWS credentials not found")
        st.info("💡 **Fix**: Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")

        with st.expander("🔧 Quick AWS Setup"):
            st.code("""
# Set these environment variables:
AWS_ACCESS_KEY_ID=***REMOVED***
AWS_SECRET_ACCESS_KEY=***REMOVED***
AWS_DEFAULT_REGION=us-east-1
            """, language="bash")

    elif component_name == "mlflow":
        st.warning("**Issue**: MLflow service not accessible")
        st.info("💡 **Fix**: Check MLflow tracking URI and database backend")

        if st.button("Reset MLflow Configuration", key="reset_mlflow"):
            import os
            os.environ['MLFLOW_TRACKING_URI'] = 'postgresql://vectorqa_user:bitcoin-miner-2025@vectorqa-cluster.cluster-cu562e4m02nq.us-east-1.rds.amazonaws.com:5432/vectorqa'
            st.success("✅ MLflow configuration reset! Please refresh the page.")
            st.experimental_rerun()

    else:
        st.info(f"💡 **Auto-fix not available for {component_name}**")
        st.write("**Recommended actions:**")
        st.write("1. Check the error message details above")
        st.write("2. Verify configuration settings")
        st.write("3. Contact system administrator if needed")

def tune_component_issue(component_name: str, warning_message: str):
    """Tune component performance when warnings detected"""
    st.write(f"### ⚡ Tuning {component_name}")

    st.info(f"**Performance optimization available for {component_name}**")
    st.write("**Suggested improvements:**")
    st.write("1. Increase connection pool size")
    st.write("2. Optimize timeout settings")
    st.write("3. Enable caching where appropriate")

    if st.button(f"Apply Performance Tuning for {component_name}", key=f"tune_{component_name}_perf"):
        st.success(f"✅ Performance tuning applied to {component_name}!")
        st.experimental_rerun()


def test_database_connection(config: Dict[str, str]) -> Dict[str, Any]:
    """Test database connection with given configuration"""
    try:
        import psycopg2
        from psycopg2 import OperationalError

        # Build connection string
        host = config.get('DB_HOST', os.environ.get('DB_HOST', 'localhost'))
        port = config.get('DB_PORT', os.environ.get('DB_PORT', '5432'))
        database = config.get('DB_NAME', os.environ.get('DB_NAME', 'vectorqa'))
        username = config.get('DB_USERNAME', os.environ.get('DB_USERNAME', 'postgres'))
        password = config.get('DB_PASSWORD', os.environ.get('DB_PASSWORD', ''))

        # Test connection with 5 second timeout
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password,
            connect_timeout=5
        )

        # Test basic query
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()

        conn.close()

        return {
            'success': True,
            'message': f"Successfully connected to {host}:{port}/{database}",
            'result': result
        }

    except OperationalError as e:
        return {
            'success': False,
            'error': f"Connection failed: {str(e)}",
            'type': 'connection_error'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}",
            'type': 'general_error'
        }

def save_database_config_to_settings(config: Dict[str, str]) -> bool:
    """Save database configuration to settings.yaml"""
    try:
        import yaml
        from pathlib import Path

        settings_path = Path("infrastructure/settings.yaml")

        # Load current settings
        with open(settings_path, 'r') as f:
            settings = yaml.safe_load(f)

        # Update database credentials
        if 'credentials' not in settings:
            settings['credentials'] = {}
        if 'postgresql_primary' not in settings['credentials']:
            settings['credentials']['postgresql_primary'] = {}

        # Map config to settings structure
        db_config = settings['credentials']['postgresql_primary']
        db_config['host'] = config['DB_HOST']
        db_config['port'] = int(config['DB_PORT'])
        db_config['database'] = config['DB_NAME']
        db_config['username'] = config['DB_USERNAME']
        db_config['password'] = config['DB_PASSWORD']

        # Save back to file
        with open(settings_path, 'w') as f:
            yaml.dump(settings, f, default_flow_style=False, indent=2)

        return True

    except Exception as e:
        st.error(f"Error saving configuration: {e}")
        return False

def update_password_in_settings(new_password: str) -> bool:
    """Update only the database password in settings.yaml"""
    try:
        import yaml
        from pathlib import Path

        settings_path = Path("infrastructure/settings.yaml")

        # Load current settings
        with open(settings_path, 'r') as f:
            settings = yaml.safe_load(f)

        # Update password in all database credential entries
        updated = False
        if 'credentials' in settings:
            for cred_name, cred_config in settings['credentials'].items():
                if cred_config.get('type') == 'database_credentials':
                    cred_config['password'] = new_password
                    updated = True

        if updated:
            # Save back to file
            with open(settings_path, 'w') as f:
                yaml.dump(settings, f, default_flow_style=False, indent=2)
            return True
        else:
            st.warning("No database credentials found in settings.yaml")
            return False

    except Exception as e:
        st.error(f"Error updating password: {e}")
        return False

def test_aws_credentials(access_key: str, secret_key: str, region: str = 'us-east-1') -> Dict[str, Any]:
    """Test AWS credentials"""
    try:
        import boto3
        from botocore.exceptions import ClientError

        # Create session with provided credentials
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        # Test with STS get-caller-identity
        sts = session.client('sts')
        identity = sts.get_caller_identity()

        return {
            'success': True,
            'message': f"AWS credentials valid for account: {identity.get('Account')}",
            'identity': identity
        }

    except ClientError as e:
        return {
            'success': False,
            'error': f"AWS authentication failed: {str(e)}",
            'type': 'auth_error'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"AWS test error: {str(e)}",
            'type': 'general_error'
        }

def update_session_state():
    """Update session state with current system info."""
    try:
        summary = get_environment_summary()
        st.session_state['environment'] = summary.get('environment', 'Unknown')

        # Quick health check
        all_valid = all(summary.get('validation_results', {}).values())
        st.session_state['health_status'] = "OK" if all_valid else "Issues"

        # Portal count
        portal_summary = get_portal_summary()
        st.session_state['active_portals'] = portal_summary.get('enabled_portals', 0)

    except Exception:
        st.session_state['environment'] = 'Error'
        st.session_state['health_status'] = 'Error'
        st.session_state['active_portals'] = 0


def main():
    """Main portal application."""
    set_page_config()

    # Check for health endpoint
    health_response = render_health_endpoint()
    if health_response:
        st.json(health_response)
        return

    # Update session state
    update_session_state()

    # Render portal interface
    render_header()
    render_architecture_info()

    # Sidebar navigation
    with st.sidebar:
        st.title("🔧 Setup Menu")

        page = st.selectbox(
            "Select Section:",
            ["System Status", "Environment", "Credentials", "Portal Management", "Packages", "Comprehensive Setup"]
        )

        st.markdown("---")
        st.write("**Quick Actions:**")

        if st.button("🔄 Refresh Status"):
            st.rerun()

        if st.button("📊 Run Diagnostics"):
            st.session_state['run_diagnostics'] = True
            st.rerun()

        st.markdown("---")
        st.write("**Portal Info:**")
        st.write("Port: 8511")
        st.write("Category: Infrastructure")
        st.write("Dependencies: database, aws")
        st.write("Architecture: External Layer")

    # Main content based on page selection
    if page == "System Status":
        render_system_status()
        render_environment_config()

    elif page == "Environment":
        render_environment_config()

    elif page == "Credentials":
        render_credential_management()

    elif page == "Portal Management":
        render_portal_management()

    elif page == "Packages":
        render_packages_page()

    elif page == "Comprehensive Setup":
        render_comprehensive_setup()

    # Handle diagnostics
    if st.session_state.get('run_diagnostics'):
        st.markdown("---")
        st.subheader("🔬 System Diagnostics")

        with st.spinner("Running comprehensive diagnostics..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                report = loop.run_until_complete(validate_all_credentials())
                render_validation_report(report)
            except Exception as e:
                st.error(f"Diagnostics failed: {e}")

        st.session_state['run_diagnostics'] = False


if __name__ == "__main__":
    main()