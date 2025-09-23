#!/usr/bin/env python3
"""
Compliance-QA Setup Portal
==========================

Step 2: Visit the friendly setup portal to test configuration and explore features
This interactive portal helps you:
- Test database connections
- Configure AWS services (optional)
- Set up MLflow tracking
- Explore available portals
- Run system health checks
"""

import subprocess
import sys
import webbrowser
import time
from pathlib import Path
import os
import socket

def check_prerequisites():
    """Check that Step 1 has been completed"""
    checks_passed = True

    print("\n" + "="*60)
    print("  Checking prerequisites...")
    print("="*60 + "\n")

    # Check settings.yaml exists
    if not Path("settings.yaml").exists():
        print("❌ settings.yaml not found")
        print("   Please run: python 1_install_requirements_cli.py")
        checks_passed = False
    else:
        print("✅ settings.yaml found")

    # Check if packages are installed
    try:
        import streamlit
        print("✅ Streamlit installed")
    except ImportError:
        print("❌ Streamlit not installed")
        checks_passed = False

    try:
        import tlm
        print("✅ TLM (numpy-free math) installed")
    except ImportError:
        print("❌ TLM package not installed")
        checks_passed = False

    try:
        import tidyllm
        print("✅ TidyLLM installed")
    except ImportError:
        print("❌ TidyLLM package not installed")
        checks_passed = False

    return checks_passed

def find_available_port(start_port=8501, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            # Try to bind to the port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            # Port is in use, try next one
            continue
    return None

def find_setup_portal():
    """Find the correct setup portal script"""
    portal_candidates = [
        "portals/setup/first_time_setup_app.py",
        "portals/setup/first_time_setup_app_new.py",
        "portals/setup/setup_portal.py",
        "adapters/primary/web/setup/setup_portal.py",
        "start_setup_app.py"
    ]

    for candidate in portal_candidates:
        if Path(candidate).exists():
            return candidate

    # If none found, list what's available
    print("\n⚠️  No standard setup portal found")
    print("Available portal files:")

    portals_dir = Path("portals")
    if portals_dir.exists():
        for py_file in portals_dir.rglob("*setup*.py"):
            print(f"  - {py_file}")

    return None

def launch_setup_portal():
    """Launch the Streamlit setup portal"""
    print("\n" + "="*60)
    print("  COMPLIANCE-QA SETUP PORTAL")
    print("="*60)
    print("\nNUMPY-FREE ZONE - All math operations use TLM")
    print("-" * 60 + "\n")

    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met!")
        print("Please run: python 1_install_requirements_cli.py first")
        sys.exit(1)

    # Find setup portal
    portal_script = find_setup_portal()

    if not portal_script:
        print("\n❌ Could not find setup portal script")
        print("\nTrying to create a minimal launcher...")

        # Create a minimal setup launcher
        minimal_launcher = """
import streamlit as st

st.set_page_config(
    page_title="Compliance-QA Setup",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Compliance-QA Setup Portal")
st.info("This is a minimal setup interface. Looking for full setup portal...")

# Try to import the actual setup
try:
    from portals.setup import setup_portal
    setup_portal.main()
except ImportError:
    st.error("Could not import setup portal")
    st.write("Please ensure all packages are installed correctly")

    with st.expander("Installation Check"):
        import subprocess
        import sys

        packages = ["streamlit", "boto3", "mlflow", "dspy", "tlm", "tidyllm"]
        for pkg in packages:
            try:
                __import__(pkg)
                st.success(f"✅ {pkg} installed")
            except ImportError:
                st.error(f"❌ {pkg} not installed")
"""

        temp_portal = Path("temp_setup_portal.py")
        with open(temp_portal, 'w') as f:
            f.write(minimal_launcher)

        portal_script = str(temp_portal)

    print(f"Using portal: {portal_script}")
    print("\nThe setup portal will:")
    print("  • Check system requirements")
    print("  • Configure database connections")
    print("  • Set up AWS credentials")
    print("  • Configure MLflow tracking")
    print("  • Validate all services")
    print("  • Guide you through portal selection")

    # Find an available port
    port = find_available_port()
    if not port:
        print("\n❌ All ports 8501-8510 are in use!")
        print("Please free up a port and try again")
        return

    print("\n" + "-"*60)
    print("Starting Streamlit server...")
    print(f"Portal will open at: http://localhost:{port}")
    print("\nPress Ctrl+C to stop the server")
    print("-"*60 + "\n")

    # Wait a moment
    time.sleep(2)

    # Open browser after delay
    def open_browser():
        time.sleep(3)
        webbrowser.open(f"http://localhost:{port}")
        print(f"📌 Browser should have opened. If not, go to: http://localhost:{port}")

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Launch the portal
    try:
        env = os.environ.copy()
        # Add project root to Python path
        env['PYTHONPATH'] = str(Path.cwd())

        result = subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            portal_script,
            "--server.port", str(port),
            "--server.address", "localhost",
            "--server.headless", "false"
        ], env=env)

        if result.returncode != 0 and result.returncode != -2:  # -2 is Ctrl+C
            print(f"\n⚠️  Streamlit exited with code {result.returncode}")

    except KeyboardInterrupt:
        print("\n\n✅ Setup portal stopped by user")

    except Exception as e:
        print(f"\n❌ Error launching portal: {e}")
        print("\nTrying alternative launch method...")

        try:
            # Try direct Python execution
            subprocess.run([sys.executable, portal_script])
        except Exception as e2:
            print(f"❌ Alternative launch also failed: {e2}")

    finally:
        # Clean up temp file if created
        temp_portal = Path("temp_setup_portal.py")
        if temp_portal.exists():
            temp_portal.unlink()
            print("Cleaned up temporary files")

def show_next_steps():
    """Show what to do after setup"""
    print("\n" + "="*60)
    print("  SETUP COMPLETE - NEXT STEPS")
    print("="*60)
    print("\nAfter configuring the system through the portal:")
    print("\n1. Launch specific portals:")
    print("   python portals/chat/chat_app.py        - Chat interface")
    print("   python portals/rag/rag_app.py          - RAG builder")
    print("   python portals/flow/flow_app.py        - Workflow designer")
    print("   python portals/dspy/dspy_app.py        - DSPy configurator")
    print("\n2. Or use the unified launcher:")
    print("   python start_all_apps.py               - Launch all portals")
    print("\n3. Start MLflow server (optional):")
    print("   python start_mlflow_server.py          - MLflow tracking UI")
    print("\n" + "="*60)

def main():
    """Main launcher function"""
    try:
        launch_setup_portal()
        show_next_steps()

    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure you ran: python 1_install_requirements_cli.py")
        print("2. Check that all packages installed correctly")
        print("3. Verify settings.yaml exists")
        print("4. Check for port conflicts on 8501")
        sys.exit(1)

if __name__ == "__main__":
    main()