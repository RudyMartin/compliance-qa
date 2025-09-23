#!/usr/bin/env python3
"""
Compliance-QA Initial Setup CLI
================================

Step 1: Install requirements and prepare environment
This script:
1. Installs production requirements
2. Installs the three local packages (tlm, tidyllm, tidyllm-sentence)
3. Creates a clean settings.yaml configuration
4. Guides user to next step (2_launch_setup.py)
"""

import subprocess
import sys
import os
from pathlib import Path
import json
import yaml
import socket

# Add parent path for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "common" / "utilities"))

try:
    from common.utilities.path_manager import PathManager
    path_manager = PathManager()
    # Ensure we're in the root folder
    os.chdir(path_manager.root_folder)
    print(f"[INFO] Working directory set to: {path_manager.root_folder}")
except ImportError:
    print("[WARNING] PathManager not available, using current directory")
    # Fallback - ensure we're in the project root
    current_file = Path(__file__).resolve()
    if current_file.parent.name != "compliance-qa":
        print(f"[ERROR] This script must be run from the compliance-qa root directory")
        print(f"[INFO] Current location: {current_file.parent}")
        sys.exit(1)

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_step(step_num, text):
    """Print formatted step"""
    print(f"\n[Step {step_num}] {text}")
    print("-" * 40)

def check_python_version():
    """Ensure Python 3.8+ is being used"""
    if sys.version_info < (3, 8):
        print("[X] Error: Python 3.8+ required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"[OK] Python version: {sys.version.split()[0]}")

def parse_version_spec(package_spec):
    """Parse package specification with various version operators"""
    import re

    # Handle different version specifiers
    # ==, >=, <=, >, <, !=, ~=
    pattern = r'^([a-zA-Z0-9\-_\.]+)\s*([><=!~]+)\s*([\d\.]+(?:\.[\*\d]+)?)'
    match = re.match(pattern, package_spec)

    if match:
        pkg_name = match.group(1)
        operator = match.group(2)
        version = match.group(3)
        return pkg_name, operator, version
    else:
        # No version specified
        return package_spec.strip(), None, None

def compare_versions(installed, required, operator):
    """Compare installed version with required version based on operator"""
    try:
        # Convert version strings to tuples for comparison
        def version_tuple(v):
            return tuple(map(int, (v.split(".")[:3])))  # Major.Minor.Patch

        inst_tuple = version_tuple(installed)
        req_tuple = version_tuple(required)

        if operator == '==':
            return inst_tuple == req_tuple
        elif operator == '>=':
            return inst_tuple >= req_tuple
        elif operator == '<=':
            return inst_tuple <= req_tuple
        elif operator == '>':
            return inst_tuple > req_tuple
        elif operator == '<':
            return inst_tuple < req_tuple
        elif operator == '!=':
            return inst_tuple != req_tuple
        elif operator == '~=':  # Compatible release
            # ~=1.4.2 means >=1.4.2, <1.5.0
            return inst_tuple >= req_tuple and inst_tuple[0:2] == req_tuple[0:2]
        else:
            # Unknown operator, be safe and reinstall
            return False
    except:
        # If comparison fails, be safe and say it doesn't match
        return False

def check_installed_package(package_spec):
    """Check if a package is already installed with correct version"""
    try:
        pkg_name, operator, required_version = parse_version_spec(package_spec)

        # Check if package is installed
        result = subprocess.run([
            sys.executable, "-m", "pip", "show", pkg_name
        ], capture_output=True, text=True)

        if result.returncode != 0:
            return False, None

        # Parse installed version
        installed_version = None
        for line in result.stdout.split('\n'):
            if line.startswith('Version:'):
                installed_version = line.split(':')[1].strip()
                break

        if not installed_version:
            return False, None

        # If no version requirement, any version is OK
        if not operator:
            return True, installed_version

        # Check if installed version meets requirements
        meets_requirement = compare_versions(installed_version, required_version, operator)

        if not meets_requirement:
            return False, f"{installed_version} (need {operator}{required_version})"

        return True, installed_version

    except Exception as e:
        # If anything goes wrong, assume not installed
        return False, None

def install_requirements(force_exact=False, no_prompt=False):
    """Install production requirements - smart check what's needed first"""
    print_step(1, "Installing production requirements")

    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("[X] Error: requirements.txt not found")
        sys.exit(1)

    print(f"[FOUND] requirements.txt with production dependencies")
    print("[CHECKING] Analyzing installed packages...")

    # Read and parse requirements
    with open(req_file, 'r') as f:
        lines = f.readlines()

    # Count total packages first
    total_packages = sum(1 for line in lines
                        if line.strip() and not line.strip().startswith('#'))
    print(f"[INFO] Checking {total_packages} packages...")

    packages_to_install = []
    already_installed = []
    checked_count = 0

    for line in lines:
        line = line.strip()
        # Skip comments and empty lines
        if not line or line.startswith('#'):
            continue

        # Extract package spec
        package_spec = line.split('#')[0].strip()
        if not package_spec:
            continue

        checked_count += 1
        # Show progress every 5 packages
        if checked_count % 5 == 0:
            print(f"  [PROGRESS] Checked {checked_count}/{total_packages} packages...")

        # Check if already installed
        pkg_name, _, _ = parse_version_spec(package_spec)
        is_installed, version_info = check_installed_package(package_spec)

        if is_installed:
            already_installed.append(f"{pkg_name} ({version_info})")
        else:
            if version_info:  # Version mismatch
                print(f"  [!] {pkg_name}: {version_info}")
            packages_to_install.append(package_spec)

    # Report status
    print(f"\n[COMPLETE] Checked {total_packages} packages")
    print(f"[INFO] Already installed: {len(already_installed)} packages")
    print(f"[INFO] Need to install: {len(packages_to_install)} packages")

    if len(already_installed) > 0 and len(already_installed) <= 5:
        for pkg in already_installed:
            print(f"  [OK] {pkg}")

    if len(packages_to_install) == 0:
        print("\n[OK] All requirements already satisfied!")

        # Ask if user wants to force reinstall to exact versions
        if len(already_installed) > 0:
            if force_exact:
                # Force mode enabled via command line
                print("\n[FORCE] Updating all packages to exact versions (--force-exact flag)")
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--force-reinstall"
                ], check=True)
                print("[OK] All packages updated to exact versions")
            elif not no_prompt:
                # Interactive mode - ask user
                print("\n[OPTIONAL] Force update to exact versions specified?")
                print("This will ensure all packages match requirements.txt exactly.")
                response = input("Force reinstall to specific versions? (y/N): ").strip().lower()

                if response == 'y':
                    print("\n[FORCE] Reinstalling all packages to exact versions...")
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--force-reinstall"
                    ], check=True)
                    print("[OK] All packages updated to exact versions")
        return

    try:
        # Install only missing packages
        print(f"\n[INSTALLING] Installing {len(packages_to_install)} missing packages...")
        for pkg in packages_to_install[:5]:  # Show first 5
            print(f"  - {pkg}")
        if len(packages_to_install) > 5:
            print(f"  ... and {len(packages_to_install) - 5} more")

        # Create temp requirements file with only missing packages
        temp_req = Path("temp_requirements.txt")
        with open(temp_req, 'w') as f:
            f.write('\n'.join(packages_to_install))

        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(temp_req)
        ], check=True)

        temp_req.unlink()  # Clean up temp file
        print("[OK] Missing packages installed successfully")

    except subprocess.CalledProcessError as e:
        print(f"[X] Error installing requirements: {e}")
        sys.exit(1)

def check_local_package_installed(package_name):
    """Check if a local package is installed in editable mode"""
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "show", package_name
        ], capture_output=True, text=True)

        if result.returncode != 0:
            return False, None

        # Check if it's editable (development) install
        for line in result.stdout.split('\n'):
            if 'Editable project location' in line or 'Location:' in line:
                location = line.split(':')[1].strip() if ':' in line else ''
                return True, location

        return False, None
    except:
        return False, None

def install_local_packages():
    """Install the three local packages in editable mode - smart check first"""
    print_step(2, "Installing local packages")

    # Use PathManager paths if available
    try:
        base_path = Path(path_manager.packages_folder)
    except NameError:
        base_path = Path("packages")

    packages = [
        (base_path / "tlm", "tlm", "TLM (numpy-free math library)"),
        (base_path / "tidyllm", "tidyllm", "TidyLLM (core framework)"),
        (base_path / "tidyllm-sentence", "tidyllm_sentence", "TidyLLM-Sentence (embeddings)")
    ]

    print(f"[CHECKING] {len(packages)} local packages...")

    packages_to_install = []
    already_installed = []

    for package_path, import_name, description in packages:
        if not package_path.exists():
            print(f"[X] Error: {package_path} not found")
            sys.exit(1)

        # Check if already installed
        is_installed, location = check_local_package_installed(import_name)

        if is_installed:
            # Check if it's the right location (editable from our packages folder)
            if str(package_path.resolve()) in str(location):
                already_installed.append(f"{import_name} (editable at {package_path})")
                print(f"  ✓ {description} - ready to go!")
            else:
                # Wrong location, need to reinstall
                packages_to_install.append((package_path, description))
                print(f"  → {description} - updating to use your local version")
        else:
            packages_to_install.append((package_path, description))
            print(f"  + {description} - setting up")

    if len(packages_to_install) == 0:
        print("\n[OK] All local packages already installed in editable mode!")
        return

    print(f"\n[INFO] Installing {len(packages_to_install)} local package(s)...")

    for package_path, description in packages_to_install:
        try:
            print(f"[INSTALLING] {description}...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-e", str(package_path)
            ], check=True)
            print(f"[OK] {description} installed in editable mode")
        except subprocess.CalledProcessError as e:
            print(f"[X] Error installing {package_path}: {e}")
            sys.exit(1)

def create_settings_yaml(no_prompt=False, force_settings=False):
    """Create a clean settings.yaml file"""
    print_step(3, "Preparing settings configuration")

    settings_path = Path("settings.yaml")

    # Check if settings.yaml already exists
    if settings_path.exists():
        print("[FOUND] Existing settings.yaml file")

        if force_settings:
            print("[FORCE] Creating new settings file (--force-settings flag)")
        elif not no_prompt:
            print("\nWant me to prepare a fresh blank settings file?")
            print("(This will backup your existing settings.yaml)")
            response = input("Create new settings file? (Y/n): ").strip().lower()

            if response == 'n' or response == 'no':
                print("[KEEPING] Using existing settings.yaml")
                return
        else:
            print("[INFO] Keeping existing settings.yaml (use --force-settings to override)")
            return
    else:
        if not no_prompt:
            print("\nNo settings.yaml found.")
            response = input("Want me to prepare a blank settings file? (Y/n): ").strip().lower()

            if response == 'n' or response == 'no':
                print("[SKIPPED] Settings file creation skipped")
                print("[NOTE] You'll need to create settings.yaml manually")
                return

    print("\n[CREATING] Clean settings.yaml...")

    # Use PathManager paths if available
    try:
        root_path = path_manager.root_folder
        packages_path = path_manager.packages_folder
        data_path = os.path.join(root_path, "data")
        logs_path = os.path.join(root_path, "logs")
    except NameError:
        root_path = str(Path.cwd())
        packages_path = str(Path.cwd() / "packages")
        data_path = str(Path.cwd() / "data")
        logs_path = str(Path.cwd() / "logs")

    settings = {
        "project": {
            "name": "compliance-qa",
            "version": "1.0.0",
            "description": "Compliance QA System - NUMPY-FREE ZONE",
            "environment": "development"
        },
        "paths": {
            "root": root_path,
            "packages": packages_path,
            "data": data_path,
            "logs": logs_path,
            "cache": os.path.join(root_path, "infrastructure", "cache"),
            "temp": os.path.join(root_path, "infrastructure", "temp")
        },
        # Flat structure for simple access
        "database": {
            "host": "localhost",
            "port": 5432,
            "database": "compliance_qa",
            "username": "postgres",
            "password": "",
            "pool_size": 5,
            "connection_timeout": 30
        },
        "mlflow": {
            "tracking_uri": "http://localhost:5000",
            "artifact_root": "s3://compliance-qa-artifacts/mlflow",
            "experiment_name": "compliance-qa-default"
        },
        "aws": {
            "region": "us-east-1",
            "access_key_id": "",
            "secret_access_key": "",
            "s3_bucket": "compliance-qa-data"
        },
        # Nested structure for yaml_loader compatibility
        "credentials": {
            "postgresql_primary": {
                "host": "localhost",
                "port": 5432,
                "database": "compliance_qa",
                "username": "postgres",
                "password": ""
            },
            "aws": {
                "access_key_id": "",
                "secret_access_key": "",
                "default_region": "us-east-1"
            },
            "bedrock_llm": {
                "service_provider": "aws_bedrock",
                "region": "us-east-1",
                "default_model": "anthropic.claude-3-sonnet-20240229-v1:0"
            }
        },
        "services": {
            "mlflow": {
                "tracking_uri": "http://localhost:5000",
                "artifact_store": "s3://compliance-qa-artifacts/mlflow"
            },
            "s3": {
                "bucket": "compliance-qa-data",
                "prefix": "compliance-qa/",
                "region": "us-east-1"
            }
        },
        "integrations": {
            "mlflow": {
                "tracking_uri": "http://localhost:5000",
                "artifact_store": "s3://compliance-qa-artifacts/mlflow",
                "experiment_name": "compliance-qa-default"
            }
        },
        "ai": {
            "provider": "aws_bedrock",
            "model": "anthropic.claude-3-sonnet-20240229-v1:0",
            "temperature": 0.7,
            "max_tokens": 4096
        },
        "security": {
            "enable_ssl": False,
            "jwt_secret_key": "",
            "session_timeout": 3600
        },
        "features": {
            "enable_rag": True,
            "enable_dspy": True,
            "enable_mlflow_tracking": True,
            "enable_s3_storage": True
        }
    }

    settings_path = Path("settings.yaml")

    # Backup existing settings if present
    if settings_path.exists():
        # Find a unique backup filename
        backup_num = 1
        while True:
            backup_path = Path(f"settings.yaml.backup{backup_num if backup_num > 1 else ''}")
            if not backup_path.exists():
                break
            backup_num += 1
        print(f"[!] Existing settings.yaml found, backing up to {backup_path}")
        settings_path.rename(backup_path)

    # Write new settings
    with open(settings_path, 'w') as f:
        yaml.dump(settings, f, default_flow_style=False, sort_keys=False)

    print("[OK] Clean settings.yaml created")

    # Also create infrastructure/settings.yaml for the portal
    infra_path = Path("infrastructure")
    if not infra_path.exists():
        infra_path.mkdir(parents=True, exist_ok=True)

    infra_settings_path = infra_path / "settings.yaml"
    with open(infra_settings_path, 'w') as f:
        yaml.dump(settings, f, default_flow_style=False, sort_keys=False)
    print("[OK] Also created infrastructure/settings.yaml for portal")

    print("\n[NOTE] Edit settings.yaml to add your credentials:")
    print("   - Database password")
    print("   - AWS credentials (if using)")
    print("   - Other service configurations")

def create_env_file():
    """Create a template .env file"""
    print_step(4, "Creating environment file template")

    env_content = """# =============================================================================
# ENVIRONMENT VARIABLES FOR COMPLIANCE-QA
# =============================================================================
#
# What is this file?
# ------------------
# This is a template for storing sensitive information like passwords and API keys.
# These values should NEVER be put directly in your code or settings.yaml!
#
# How to use:
# -----------
# 1. Make a copy of this file and name it exactly: .env (just remove .template)
# 2. Fill in any passwords or API keys you have
# 3. The .env file is automatically ignored by Git (won't be uploaded)
#
# Note: Most values are OPTIONAL - the system works without them!
# =============================================================================

# DATABASE SETTINGS (Optional - defaults work for local PostgreSQL)
# ---------------------------------------------------------------------
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=compliance_qa
DB_USERNAME=postgres
DB_PASSWORD=
# ^ Add your PostgreSQL password here if you have one

# AWS SETTINGS (Optional - only if using AWS services)
# ---------------------------------------------------------------------
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=
# ^ Your AWS access key (looks like: AKIAIOSFODNN7EXAMPLE)
AWS_SECRET_ACCESS_KEY=
# ^ Your AWS secret key (looks like: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY)
AWS_S3_BUCKET=compliance-qa-data

# MLFLOW TRACKING (Optional - for ML experiment tracking)
# ---------------------------------------------------------------------
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_ARTIFACT_ROOT=./mlruns

# AI MODEL SETTINGS (Optional - defaults to Claude)
# ---------------------------------------------------------------------
AI_PROVIDER=aws_bedrock
AI_MODEL=anthropic.claude-3-sonnet-20240229-v1:0

# SECURITY (Optional - for production use)
# ---------------------------------------------------------------------
JWT_SECRET_KEY=
# ^ Random string for session security (you can leave blank for development)
SESSION_TIMEOUT=3600
# ^ How long before users need to log in again (in seconds)
"""

    env_template_path = Path(".env.template")
    with open(env_template_path, 'w') as f:
        f.write(env_content)

    print("[OK] Created .env.template with explanations")

    if not Path(".env").exists():
        print("\n[INFO] About environment files:")
        print("  • .env files store passwords/keys separate from code")
        print("  • They're like a private notepad for sensitive info")
        print("  • Git automatically ignores .env (keeps secrets safe)")
        print("\n[OPTIONAL] Two ways to set up environment variables:")
        print("\n  Option 1: Use the Setup Portal (easier!)")
        print("  • The portal can create your .env file for you")
        print("  • Just enter values in the web interface")
        print("\n  Option 2: Manual setup")
        print("  • Copy .env.template → .env")
        print("  • Add any passwords/keys you have")
        print("  • Leave blank if you don't have them yet!")
    else:
        print("[FOUND] .env file already exists - keeping it")

def verify_installation():
    """Verify packages are importable"""
    print_step(5, "Verifying installation")

    # Add local packages to path for verification
    import sys
    sys.path.insert(0, str(Path("packages/tlm")))
    sys.path.insert(0, str(Path("packages/tidyllm")))
    sys.path.insert(0, str(Path("packages/tidyllm-sentence")))

    packages_to_verify = [
        ("streamlit", "Streamlit"),
        ("boto3", "AWS SDK"),
        ("mlflow", "MLflow"),
        ("ujson", "UltraJSON (DSPy dependency)"),
        ("datasets", "Datasets (DSPy dependency)"),
        ("dspy", "DSPy framework"),
        ("tlm", "TLM (numpy replacement)"),
        ("tidyllm", "TidyLLM"),
        ("tidyllm_sentence", "TidyLLM-Sentence")
    ]

    all_good = True
    critical_failures = 0
    for package, name in packages_to_verify:
        try:
            __import__(package)
            print(f"[OK] {name} imported successfully")
        except ImportError as e:
            # DSPy and its dependencies are important but not critical
            if package in ["dspy", "ujson", "datasets"]:
                print(f"[!] {name} not available: {e}")
                print("     Run: pip install ujson datasets dspy-ai")
            else:
                print(f"[X] Failed to import {name}: {e}")
                critical_failures += 1

    # Only fail if critical packages failed
    return critical_failures == 0

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

def create_launch_setup_script():
    """Create the 2_visit_setup_portal.py script if it doesn't exist"""
    launch_script_path = Path("2_visit_setup_portal.py")

    if not launch_script_path.exists():
        print("\nCreating 2_visit_setup_portal.py...")

        launch_content = '''#!/usr/bin/env python3
"""
Compliance-QA Setup Portal
==========================

Step 2: Visit the friendly setup portal to test configuration and explore features
"""

import subprocess
import sys
import webbrowser
import time
from pathlib import Path
import socket

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

def launch_setup_portal():
    """Launch the Streamlit setup portal"""
    print("\\n" + "="*60)
    print("  Launching Compliance-QA Setup Portal")
    print("="*60 + "\\n")

    # Check if settings.yaml exists
    if not Path("settings.yaml").exists():
        print("❌ Error: settings.yaml not found")
        print("   Please run 1_install_requirements_cli.py first")
        sys.exit(1)

    # Find an available port
    port = find_available_port()
    if not port:
        print("❌ Error: Could not find an available port (8501-8510)")
        print("   Please free up a port and try again")
        sys.exit(1)

    print("Starting Streamlit setup portal...")
    print(f"The portal will open in your browser at http://localhost:{port}")
    print("\\nPress Ctrl+C to stop the server\\n")

    # Give user time to read
    time.sleep(2)

    # Open browser after a delay
    def open_browser():
        time.sleep(3)
        webbrowser.open(f"http://localhost:{port}")

    import threading
    threading.Thread(target=open_browser).start()

    # Run the setup portal
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "portals/setup/first_time_setup_app.py",
            "--server.port", str(port),
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\\n\\nSetup portal stopped.")
    except FileNotFoundError:
        # Fallback to alternative setup portal locations
        portal_paths = [
            "portals/setup/setup_portal.py",
            "adapters/primary/web/setup/setup_portal.py",
            "start_setup_app.py"
        ]

        for portal_path in portal_paths:
            if Path(portal_path).exists():
                print(f"Using alternative portal: {portal_path}")
                try:
                    subprocess.run([
                        sys.executable, "-m", "streamlit", "run",
                        portal_path,
                        "--server.port", str(port)
                    ])
                    break
                except KeyboardInterrupt:
                    print("\\n\\nSetup portal stopped.")
                    break
        else:
            print("❌ Error: No setup portal found")
            print("   Available Python files:")
            for p in Path("portals/setup").glob("*.py"):
                print(f"   - {p}")

if __name__ == "__main__":
    launch_setup_portal()
'''

        with open(launch_script_path, 'w') as f:
            f.write(launch_content)

        print("[OK] Created 2_visit_setup_portal.py")

def main():
    """Main installation process"""
    print_header("COMPLIANCE-QA INSTALLATION")
    print("NUMPY-FREE ZONE - Using TLM for all mathematical operations")

    # Check for command-line arguments
    force_exact = '--force-exact' in sys.argv
    force_settings = '--force-settings' in sys.argv
    no_prompt = '--no-prompt' in sys.argv or '-y' in sys.argv

    if force_exact:
        print("[MODE] Force exact versions enabled")
    if force_settings:
        print("[MODE] Force new settings file enabled")
    if no_prompt:
        print("[MODE] Non-interactive mode enabled")

    # Check Python version
    check_python_version()

    # Install requirements
    install_requirements(force_exact=force_exact, no_prompt=no_prompt)

    # Install local packages
    install_local_packages()

    # Create settings.yaml
    create_settings_yaml(no_prompt=no_prompt, force_settings=force_settings)

    # Create .env template
    create_env_file()

    # Verify installation
    if verify_installation():
        print("\n" + "="*60)
        print("  [SUCCESS] INSTALLATION COMPLETE!")
        print("="*60)

        # Create launch script
        create_launch_setup_script()

        print("\n[WHAT'S BEEN INSTALLED]:")
        print("-" * 40)
        print("[OK] All production requirements")
        print("[OK] TLM - numpy-free math library")
        print("[OK] TidyLLM - core framework")
        print("[OK] TidyLLM-Sentence - embeddings")
        print("[OK] Clean settings.yaml created")
        print("[OK] Environment template created")

        print("\n[NEXT STEPS]:")
        print("-" * 40)
        print("")
        print("1. CONFIGURE CREDENTIALS (Optional):")
        print("   =====================================")
        print("   Go to: infrastructure/settings.yaml")
        print("")
        print("   IMPORTANT: Do NOT change the format or add/delete any items!")
        print("   Only fill in the empty '' values where needed:")
        print("")
        print("   Database credentials:")
        print("     - credentials.postgresql_primary.password: ''  <- Your DB password here")
        print("")
        print("   AWS credentials (if using AWS):")
        print("     - credentials.aws.access_key_id: ''  <- Your AWS key")
        print("     - credentials.aws.secret_access_key: ''  <- Your AWS secret")
        print("")
        print("   You can also set these via environment variables instead.")
        print("")
        print("2. LAUNCH SETUP PORTAL:")
        print("   ====================")
        print("   >>> Run: python 2_visit_setup_portal.py")
        print("")
        print("   The first_time_setup_app provides:")
        print("   ✓ System Health Check - Test your Python environment")
        print("   ✓ Prerequisites Verification - Check all dependencies")
        print("   ✓ Database Connection Testing - PostgreSQL connectivity")
        print("   ✓ AWS Services Configuration - S3, Bedrock, Secrets Manager")
        print("   ✓ MLflow Setup - Experiment tracking and model registry")
        print("   ✓ AI Model Selection - Choose and test LLM models")
        print("   ✓ Portal Directory - Explore all available interfaces")
        print("   ✓ Interactive Configuration - Safely modify settings")
        print("   ✓ Connection Pool Testing - Validate database pooling")
        print("   ✓ Integration Validation - Test all service connections")
        print("   ✓ Quick Start Guide - Step-by-step onboarding")
        print("   ✓ Troubleshooting Help - Debug connection issues")
        print("")
        print("   Note: The portal works even without credentials!")
        print("         You can configure everything interactively.")
        print("\n" + "="*60)

        # Ask if ready to continue
        if not no_prompt:
            print("\nReady to launch the setup portal?")
            response = input("Continue to Step 2? (Y/n): ").strip().lower()

            if response == '' or response == 'y' or response == 'yes':
                print("\nLaunching setup portal...")
                print("="*60)

                # Find an available port
                port = find_available_port()
                if not port:
                    print("\n❌ Could not find an available port")
                    print("All ports 8501-8510 are in use")
                    print("Please run manually: python 2_visit_setup_portal.py")
                    return

                print("\nStarting Streamlit server...")
                print(f"Portal will be available at: http://localhost:{port}")
                print(f"\n>>> Open your browser and go to: http://localhost:{port}")
                print("\nPress Ctrl+C to stop the server")
                print("="*60 + "\n")

                # Launch the portal - simple and direct
                try:
                    subprocess.run([
                        sys.executable, "-m", "streamlit", "run",
                        "portals/setup/first_time_setup_app.py",
                        "--server.port", str(port),
                        "--server.address", "localhost"
                    ])
                except KeyboardInterrupt:
                    print("\n\nSetup portal stopped by user.")
                except FileNotFoundError:
                    print("\n❌ Could not find setup portal")
                    print("Please run manually: python 2_visit_setup_portal.py")
            else:
                print("\nSetup complete! When ready, run:")
                print("  python 2_visit_setup_portal.py")
                print("="*60)
        else:
            print("\nSetup complete! Run: python 2_visit_setup_portal.py")
            print("="*60)
    else:
        print("\n[!] Some packages failed to import")
        print("Please check the errors above and try again")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[X] Unexpected error: {e}")
        sys.exit(1)