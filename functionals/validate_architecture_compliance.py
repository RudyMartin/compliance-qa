#!/usr/bin/env python3
"""
Architecture Compliance Validator
==================================

This script validates that the codebase follows hexagonal architecture principles.
Run this regularly to ensure compliance is maintained.
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import List, Dict, Tuple, Set
from datetime import datetime


class ArchitectureValidator:
    """Validates hexagonal architecture compliance."""

    def __init__(self, root_path: str = None):
        """Initialize validator with project root."""
        self.root_path = Path(root_path or os.getcwd())
        self.violations = []
        self.warnings = []
        self.passed = []

    def validate_all(self) -> Dict:
        """Run all validation checks."""
        print("\n" + "="*60)
        print("ARCHITECTURE COMPLIANCE VALIDATION")
        print("="*60)

        results = {
            'timestamp': datetime.now().isoformat(),
            'checks': []
        }

        # Run all checks
        checks = [
            ("Domain Layer Isolation", self.check_domain_isolation),
            ("Port Definitions", self.check_port_definitions),
            ("Adapter Implementation", self.check_adapter_implementation),
            ("Infrastructure Independence", self.check_infrastructure_independence),
            ("Circular Dependencies", self.check_circular_dependencies),
            ("Delegate Pattern", self.check_delegate_pattern),
            ("Test Structure", self.check_test_structure),
        ]

        for check_name, check_func in checks:
            print(f"\nChecking: {check_name}")
            print("-" * 40)

            result = check_func()
            results['checks'].append({
                'name': check_name,
                'result': result
            })

            if result['status'] == 'PASS':
                print(f"[PASS] {result['message']}")
                self.passed.append(check_name)
            elif result['status'] == 'WARNING':
                print(f"[WARNING] {result['message']}")
                self.warnings.append(check_name)
            else:
                print(f"[FAIL] {result['message']}")
                self.violations.append(check_name)

            if 'details' in result:
                for detail in result['details'][:5]:  # Show first 5
                    print(f"  - {detail}")
                if len(result['details']) > 5:
                    print(f"  ... and {len(result['details']) - 5} more")

        # Summary
        self.print_summary()
        results['summary'] = self.get_summary()

        return results

    def check_domain_isolation(self) -> Dict:
        """Check that domain layer doesn't import from infrastructure or adapters."""
        violations = []
        domain_path = self.root_path / "domain"

        if not domain_path.exists():
            return {
                'status': 'FAIL',
                'message': 'Domain directory not found',
                'details': []
            }

        for py_file in domain_path.rglob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for infrastructure imports
            if 'from infrastructure' in content or 'import infrastructure' in content:
                violations.append(f"{py_file.relative_to(self.root_path)}: imports from infrastructure")

            # Check for adapter imports (except in ports)
            if '/ports/' not in str(py_file):
                if 'from adapters' in content or 'import adapters' in content:
                    violations.append(f"{py_file.relative_to(self.root_path)}: imports from adapters")

        if violations:
            return {
                'status': 'FAIL',
                'message': f'Found {len(violations)} domain isolation violations',
                'details': violations
            }

        return {
            'status': 'PASS',
            'message': 'Domain layer properly isolated',
            'details': []
        }

    def check_port_definitions(self) -> Dict:
        """Check that all required ports are defined."""
        required_ports = [
            'SessionPort',
            'StoragePort',  # For S3
            'LLMPort',  # For Bedrock
            'SetupDependenciesPort'
        ]

        ports_path = self.root_path / "domain" / "ports"
        if not ports_path.exists():
            return {
                'status': 'FAIL',
                'message': 'Ports directory not found',
                'details': []
            }

        found_ports = set()
        missing_ports = []

        for py_file in ports_path.rglob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Look for class definitions
            for port in required_ports:
                if f'class {port}' in content:
                    found_ports.add(port)

        for port in required_ports:
            if port not in found_ports:
                missing_ports.append(port)

        if missing_ports:
            return {
                'status': 'WARNING',
                'message': f'Missing {len(missing_ports)} port definitions',
                'details': missing_ports
            }

        return {
            'status': 'PASS',
            'message': 'All required ports defined',
            'details': list(found_ports)
        }

    def check_adapter_implementation(self) -> Dict:
        """Check that ports have corresponding adapter implementations."""
        adapters_path = self.root_path / "adapters"

        if not adapters_path.exists():
            return {
                'status': 'FAIL',
                'message': 'Adapters directory not found',
                'details': []
            }

        adapter_files = list(adapters_path.rglob("*.py"))
        adapter_count = len([f for f in adapter_files if 'adapter' in f.name.lower()])

        if adapter_count < 3:  # We expect at least 3 adapters
            return {
                'status': 'WARNING',
                'message': f'Only {adapter_count} adapters found',
                'details': [str(f.relative_to(self.root_path)) for f in adapter_files]
            }

        return {
            'status': 'PASS',
            'message': f'Found {adapter_count} adapter implementations',
            'details': []
        }

    def check_infrastructure_independence(self) -> Dict:
        """Check that infrastructure doesn't import from domain (except ports)."""
        violations = []
        infra_path = self.root_path / "infrastructure"

        if not infra_path.exists():
            return {
                'status': 'WARNING',
                'message': 'Infrastructure directory not found',
                'details': []
            }

        for py_file in infra_path.rglob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Infrastructure should not import from domain services
            if 'from domain.services' in content:
                violations.append(f"{py_file.relative_to(self.root_path)}: imports domain services")

            # Infrastructure should not import from adapters
            if 'from adapters' in content:
                violations.append(f"{py_file.relative_to(self.root_path)}: imports from adapters")

        if violations:
            return {
                'status': 'FAIL',
                'message': f'Infrastructure has {len(violations)} dependency violations',
                'details': violations
            }

        return {
            'status': 'PASS',
            'message': 'Infrastructure properly independent',
            'details': []
        }

    def check_circular_dependencies(self) -> Dict:
        """Check for circular import dependencies."""
        # Simplified check - look for infrastructure importing from packages
        violations = []
        infra_path = self.root_path / "infrastructure"

        if infra_path.exists():
            for py_file in infra_path.rglob("*.py"):
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                if 'from packages' in content:
                    violations.append(f"{py_file.relative_to(self.root_path)}: imports from packages")

        # Check if packages import from each other in circular way
        packages_path = self.root_path / "packages"
        if packages_path.exists():
            for py_file in packages_path.rglob("*.py"):
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Package should use delegates, not direct infrastructure
                if 'import boto3' in content and 'delegate' not in py_file.name:
                    violations.append(f"{py_file.relative_to(self.root_path)}: directly imports boto3")

        if violations:
            return {
                'status': 'WARNING',
                'message': f'Found {len(violations)} potential circular dependencies',
                'details': violations
            }

        return {
            'status': 'PASS',
            'message': 'No circular dependencies detected',
            'details': []
        }

    def check_delegate_pattern(self) -> Dict:
        """Check that delegate pattern is properly implemented."""
        delegates = []
        delegate_path = self.root_path / "packages" / "tidyllm" / "infrastructure"

        if delegate_path.exists():
            for py_file in delegate_path.glob("*_delegate.py"):
                delegates.append(py_file.name)

        expected_delegates = ['bedrock_delegate.py', 's3_delegate.py', 'aws_delegate.py']
        missing = [d for d in expected_delegates if d not in delegates]

        if missing:
            return {
                'status': 'WARNING',
                'message': f'Missing {len(missing)} delegate implementations',
                'details': missing
            }

        return {
            'status': 'PASS',
            'message': f'Found {len(delegates)} delegate implementations',
            'details': delegates
        }

    def check_test_structure(self) -> Dict:
        """Check that tests follow proper structure."""
        test_issues = []

        # Check for functional tests
        functional_path = self.root_path / "functionals"
        if not functional_path.exists():
            test_issues.append("Functionals directory missing")

        # Check for specific test suites
        expected_tests = ['bedrock', 's3', 'setup', 'rag']
        for test in expected_tests:
            test_path = functional_path / test
            if not test_path.exists():
                test_issues.append(f"Missing functional test: {test}")

        if test_issues:
            return {
                'status': 'WARNING',
                'message': f'Found {len(test_issues)} test structure issues',
                'details': test_issues
            }

        return {
            'status': 'PASS',
            'message': 'Test structure properly organized',
            'details': []
        }

    def get_summary(self) -> Dict:
        """Get validation summary."""
        total = len(self.passed) + len(self.warnings) + len(self.violations)

        return {
            'total_checks': total,
            'passed': len(self.passed),
            'warnings': len(self.warnings),
            'violations': len(self.violations),
            'compliance_score': (len(self.passed) / total * 100) if total > 0 else 0
        }

    def print_summary(self):
        """Print validation summary."""
        print("\n" + "="*60)
        print("COMPLIANCE SUMMARY")
        print("="*60)

        summary = self.get_summary()

        print(f"Total Checks: {summary['total_checks']}")
        print(f"Passed: {summary['passed']}")
        print(f"Warnings: {summary['warnings']}")
        print(f"Violations: {summary['violations']}")
        print(f"Compliance Score: {summary['compliance_score']:.1f}%")

        if self.violations:
            print("\n[X] CRITICAL VIOLATIONS:")
            for violation in self.violations:
                print(f"  - {violation}")

        if self.warnings:
            print("\n[!] WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")

        # Recommendations
        print("\n" + "="*60)
        print("RECOMMENDATIONS")
        print("="*60)

        if self.violations:
            print("\n[CRITICAL] IMMEDIATE ACTIONS REQUIRED:")
            if "Domain Layer Isolation" in self.violations:
                print("  1. Remove all infrastructure imports from domain layer")
                print("     - Use dependency injection instead")
                print("     - Define ports for infrastructure access")

            if "Infrastructure Independence" in self.violations:
                print("  2. Remove domain service imports from infrastructure")
                print("     - Infrastructure should be independent")
                print("     - Use interfaces/ports for communication")

        if self.warnings:
            print("\n[RECOMMENDED] IMPROVEMENTS:")
            for warning in self.warnings:
                if "Port Definitions" in warning:
                    print("  - Define missing port interfaces")
                elif "Adapter Implementation" in warning:
                    print("  - Implement adapters for all ports")
                elif "Circular Dependencies" in warning:
                    print("  - Review and refactor circular dependencies")

        if summary['compliance_score'] == 100:
            print("\n[EXCELLENT] Full architecture compliance achieved!")
        elif summary['compliance_score'] >= 80:
            print("\n[GOOD] Minor improvements needed for full compliance.")
        else:
            print("\n[ATTENTION] Significant architecture refactoring required.")


def main():
    """Main entry point."""
    # Find project root
    current_path = Path(__file__).parent.parent

    validator = ArchitectureValidator(current_path)
    results = validator.validate_all()

    # Save results
    output_file = Path(__file__).parent / "compliance_report.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nDetailed report saved to: {output_file}")

    # Exit with error code if violations found
    if validator.violations:
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    main()