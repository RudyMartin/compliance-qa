#!/usr/bin/env python3
"""
QA-Shipping Package Installation Script
=====================================

Installs the three core packages as independent packages:
- tlm (Transparent Learning Machines)
- tidyllm (Core TidyLLM business logic)
- tidyllm-sentence (Sentence processing)

This is the FIRST STEP in the setup process to make packages work independently.

**IMPORTANT:** The installer will attempt to install any packages that have proper
packaging structure (setup.py files) and will fail if packaging is incorrect.
Ensure all packages have valid setup.py files before running the installer.

# future_feature: create function to determine best install order and how to manage that sequence
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class PackageInstaller:
    """Installs the three core packages as independent packages."""

    def __init__(self, qa_shipping_root: str = None):
        self.qa_shipping_root = Path(qa_shipping_root) if qa_shipping_root else Path(__file__).parent.parent
        self.packages_dir = self.qa_shipping_root / "packages"

        # Auto-discover packages instead of hardcoding
        self.packages = self._discover_packages()

    def _discover_packages(self) -> Dict[str, Dict[str, Any]]:
        """Automatically discover all installable packages in the packages directory."""
        discovered_packages = {}

        if not self.packages_dir.exists():
            print(f"[WARN]  Packages directory not found: {self.packages_dir}")
            return discovered_packages

        print(f"[SCAN] Auto-discovering packages in: {self.packages_dir}")

        # Scan packages directory for potential packages
        for item in self.packages_dir.iterdir():
            if item.is_dir():
                package_name = item.name
                package_path = item

                # Special handling for nested packages (like tlm/tlm)
                nested_path = item / package_name
                if nested_path.exists() and nested_path.is_dir():
                    # Check if nested directory has setup.py
                    if (nested_path / "setup.py").exists():
                        package_path = nested_path
                        print(f"  [PKG] Found nested package: {package_name} at {package_path}")
                    else:
                        # Check if parent directory has setup.py
                        if (item / "setup.py").exists():
                            print(f"  [PKG] Found package: {package_name} at {package_path}")
                        else:
                            print(f"  [SKIP]  Skipping {package_name} - no setup.py found")
                            continue
                elif (item / "setup.py").exists():
                    print(f"  [PKG] Found package: {package_name} at {package_path}")
                else:
                    print(f"  [SKIP]  Skipping {package_name} - no setup.py found")
                    continue

                # Determine package type and dependencies
                package_info = self._analyze_package(package_name, package_path)
                discovered_packages[package_name] = package_info

        print(f"[OK] Discovered {len(discovered_packages)} installable packages")
        return discovered_packages

    def _analyze_package(self, package_name: str, package_path: Path) -> Dict[str, Any]:
        """Analyze a package to determine its properties."""
        setup_py_path = package_path / "setup.py"
        has_setup = setup_py_path.exists()

        # Try to read description from setup.py
        description = f"{package_name} package"
        if has_setup:
            try:
                with open(setup_py_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract description from setup.py
                    if 'description=' in content:
                        for line in content.split('\n'):
                            if 'description=' in line and not line.strip().startswith('#'):
                                # Extract description between quotes
                                import re
                                match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', line)
                                if match:
                                    description = match.group(1)
                                    break
            except Exception:
                pass

        return {
            "path": package_path,
            "name": package_name,
            "description": description,
            "has_setup": has_setup,
            "auto_discovered": True
        }

    def check_package_structure(self) -> Dict[str, bool]:
        """Check if package directories exist."""
        results = {}

        print(f"[SCAN] Checking package structure in: {self.packages_dir}")

        for pkg_name, pkg_info in self.packages.items():
            pkg_path = pkg_info["path"]
            exists = pkg_path.exists()

            print(f"  [PKG] {pkg_name}: {'[OK] Found' if exists else '[ERR] Missing'} at {pkg_path}")

            if exists and pkg_info["has_setup"]:
                setup_py = pkg_path / "setup.py"
                has_setup = setup_py.exists()
                print(f"     setup.py: {'[OK] Found' if has_setup else '[ERR] Missing'}")
                results[pkg_name] = has_setup
            else:
                results[pkg_name] = exists

        return results

    def create_setup_py_for_tidyllm(self):
        """Create setup.py for tidyllm package."""
        setup_content = '''#!/usr/bin/env python3
"""
TidyLLM - Core Business Logic Package
===================================
"""

from setuptools import setup, find_packages

setup(
    name="tidyllm",
    version="2.0.0",
    author="TidyLLM Team",
    author_email="info@tidyllm.ai",
    description="Core TidyLLM business logic package",
    long_description="TidyLLM core business logic for QA-Shipping 4-layer architecture",
    url="https://github.com/tidyllm/tidyllm",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "sqlalchemy>=2.0.0",
        "asyncio-mqtt",
        "aiofiles",
        "httpx",
        "pyyaml",
        "python-dotenv",
    ],
    include_package_data=True,
    zip_safe=False,
)
'''

        setup_path = self.packages_dir / "tidyllm" / "setup.py"
        with open(setup_path, 'w') as f:
            f.write(setup_content)

        print(f"[OK] Created setup.py for tidyllm at {setup_path}")

    def create_setup_py_for_tidyllm_sentence(self):
        """Create setup.py for tidyllm-sentence package."""
        setup_content = '''#!/usr/bin/env python3
"""
TidyLLM-Sentence - Sentence Processing Package
============================================
"""

from setuptools import setup, find_packages

setup(
    name="tidyllm-sentence",
    version="1.0.0",
    author="TidyLLM Team",
    author_email="info@tidyllm.ai",
    description="Sentence processing logic for TidyLLM",
    long_description="TidyLLM sentence processing package for QA-Shipping 4-layer architecture",
    url="https://github.com/tidyllm/tidyllm-sentence",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
    install_requires=[
        "nltk>=3.8",
        "spacy>=3.4.0",
        "transformers>=4.20.0",
        "torch>=1.12.0",
        "numpy>=1.21.0",
    ],
    include_package_data=True,
    zip_safe=False,
)
'''

        setup_path = self.packages_dir / "tidyllm-sentence" / "setup.py"
        with open(setup_path, 'w') as f:
            f.write(setup_content)

        print(f"[OK] Created setup.py for tidyllm-sentence at {setup_path}")

    def install_package(self, package_name: str, development_mode: bool = True) -> bool:
        """Install a single package."""
        pkg_info = self.packages[package_name]
        pkg_path = pkg_info["path"]

        if not pkg_path.exists():
            print(f"[ERR] Package directory not found: {pkg_path}")
            return False

        print(f"[PKG] Installing {package_name} from {pkg_path}")

        try:
            # Change to package directory
            original_cwd = os.getcwd()
            os.chdir(pkg_path)

            # Install in development mode (-e) or regular mode
            if development_mode:
                cmd = [sys.executable, "-m", "pip", "install", "-e", "."]
                print(f"   Running: pip install -e . (development mode)")
            else:
                cmd = [sys.executable, "-m", "pip", "install", "."]
                print(f"   Running: pip install .")

            result = subprocess.run(cmd, capture_output=True, text=True)

            os.chdir(original_cwd)

            if result.returncode == 0:
                print(f"[OK] {package_name} installed successfully")
                return True
            else:
                print(f"[ERR] {package_name} installation failed:")
                print(f"   stdout: {result.stdout}")
                print(f"   stderr: {result.stderr}")
                return False

        except Exception as e:
            os.chdir(original_cwd)
            print(f"[ERR] Exception installing {package_name}: {e}")
            return False

    def install_all_packages(self, development_mode: bool = True) -> Dict[str, bool]:
        """Install all discovered packages dynamically."""
        print("[INST] Starting QA-Shipping Package Installation")
        print("=" * 50)
        print("**IMPORTANT:** Installer will attempt to install packages with proper")
        print("packaging structure and will fail if packaging is incorrect!")
        print("=" * 50)

        # Re-discover packages to get latest state
        self.packages = self._discover_packages()

        if not self.packages:
            print("[ERR] No installable packages found!")
            return {}

        # Check structure first
        structure_check = self.check_package_structure()

        print(f"\n[PKG] Installing {len(self.packages)} packages in {'development' if development_mode else 'production'} mode")
        print("-" * 50)

        results = {}

        # Create installation order - prioritize packages with no dependencies first
        install_order = self._determine_install_order()

        for package_name in install_order:
            if package_name in self.packages:
                pkg_info = self.packages[package_name]
                print(f"\n[PROC] Processing: {package_name}")
                print(f"   Description: {pkg_info['description']}")
                print(f"   Path: {pkg_info['path']}")

                if pkg_info.get('has_setup', False):
                    success = self.install_package(package_name, development_mode)
                    results[package_name] = success
                else:
                    print(f"   [WARN]  No setup.py found - skipping installation")
                    results[package_name] = False
            else:
                print(f"[SKIP]  Package {package_name} not found in discovered packages")
                results[package_name] = False

        # Summary
        print("\n" + "=" * 50)
        print("[LIST] PACKAGE INSTALLATION SUMMARY")
        print("=" * 50)

        successful = 0
        for pkg_name, success in results.items():
            status = "[OK] SUCCESS" if success else "[ERR] FAILED"
            description = self.packages.get(pkg_name, {}).get('description', 'Unknown package')
            print(f"  {status} {pkg_name} - {description}")
            if success:
                successful += 1

        print(f"\n[RSLT] RESULT: {successful}/{len(results)} packages installed successfully")

        if successful == len(results) and successful > 0:
            print("[DONE] All packages installed! You can now use them as independent packages.")
            print("\n[NEXT] Next steps:")
            print("   1. Run '[ENV] Setup Environment' in the Setup Portal")
            print("   2. Run '[CONN] Initialize Connection Pool'")
            print("   3. Run '[TEST] Run Complete Validation'")
        elif successful > 0:
            print(f"[OK] {successful} packages installed successfully.")
            print("[WARN]  Some packages failed to install. Check the output above for details.")
        else:
            print("[ERR] No packages were installed successfully.")

        return results

    def _determine_install_order(self) -> List[str]:
        """Determine the optimal installation order for packages."""
        # For now, use a simple heuristic: packages with fewer dependencies first
        order = []

        # TLM typically has no dependencies, install first
        if 'tlm' in self.packages:
            order.append('tlm')

        # Add remaining packages
        for pkg_name in self.packages.keys():
            if pkg_name not in order:
                order.append(pkg_name)

        print(f"[LIST] Installation order: {' -> '.join(order)}")
        return order

    def verify_installations(self) -> Dict[str, bool]:
        """Verify that packages are properly installed."""
        print("\n[SCAN] Verifying package installations...")

        verification_results = {}

        for pkg_name in self.packages.keys():
            try:
                # Determine import name for the package
                import_name = self._get_import_name(pkg_name)

                result = subprocess.run([
                    sys.executable, "-c", f"import {import_name}; print('[OK] {pkg_name} import successful')"
                ], capture_output=True, text=True)

                success = result.returncode == 0
                verification_results[pkg_name] = success

                if success:
                    print(f"[OK] {pkg_name}: Import successful as '{import_name}'")
                else:
                    print(f"[ERR] {pkg_name}: Import failed - {result.stderr.strip()}")

            except Exception as e:
                verification_results[pkg_name] = False
                print(f"[ERR] {pkg_name}: Verification failed - {e}")

        return verification_results

    def _get_import_name(self, package_name: str) -> str:
        """Get the correct import name for a package."""
        # Handle special cases for import names
        import_mapping = {
            "tidyllm-sentence": "tidyllm_sentence",  # Hyphens become underscores
        }

        return import_mapping.get(package_name, package_name)


def main():
    """Main function for standalone execution."""
    installer = PackageInstaller()

    # Install packages in development mode
    results = installer.install_all_packages(development_mode=True)

    # Verify installations
    verification = installer.verify_installations()

    # Exit with appropriate code
    all_successful = all(results.values()) and all(verification.values())
    sys.exit(0 if all_successful else 1)


if __name__ == "__main__":
    main()