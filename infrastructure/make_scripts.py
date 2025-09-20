#!/usr/bin/env python3
"""
Make Scripts - Infrastructure CLI Utility

Simple command-line tool to generate environment setup scripts from settings.yaml.
Usage: python infrastructure/make_scripts.py [options]
"""

import sys
import argparse
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.script_generator import ScriptGenerator

def main():
    parser = argparse.ArgumentParser(description='Generate environment setup scripts from settings.yaml')

    parser.add_argument('--all', action='store_true',
                       help='Generate all script types (default)')
    parser.add_argument('--windows', action='store_true',
                       help='Generate Windows batch script only')
    parser.add_argument('--unix', action='store_true',
                       help='Generate Unix shell script only')
    parser.add_argument('--powershell', action='store_true',
                       help='Generate PowerShell script only')
    parser.add_argument('--docker', action='store_true',
                       help='Generate Docker .env file only')
    parser.add_argument('--validate', action='store_true',
                       help='Validate existing scripts')
    parser.add_argument('--info', action='store_true',
                       help='Show script generation info')
    parser.add_argument('--output-dir', type=str, default=None,
                       help='Output directory (default: infrastructure/)')

    args = parser.parse_args()

    try:
        generator = ScriptGenerator()

        # Show info if requested
        if args.info:
            info = generator.get_script_info()
            print("Script Generation Info:")
            print(f"  Source settings: {info['source_settings']}")
            print(f"  Output directory: {info['output_directory']}")
            print(f"  Environment: {info['environment_type']}")
            print(f"  Database: {info['database_host']}")
            print(f"  AWS Region: {info['aws_region']}")
            print(f"  MLflow URI: {info['mlflow_uri']}")
            return

        # Validate existing scripts
        if args.validate:
            validation = generator.validate_generated_scripts()
            print("Script Validation:")
            for script, valid in validation.items():
                status = "[OK]" if valid else "[MISSING]"
                print(f"  {status} {script}")
            return

        # Generate scripts based on arguments
        generated = {}

        if args.windows:
            path = generator.generate_windows_script()
            generated['Windows Batch'] = path

        elif args.unix:
            path = generator.generate_unix_script()
            generated['Unix Shell'] = path

        elif args.powershell:
            path = generator.generate_powershell_script()
            generated['PowerShell'] = path

        elif args.docker:
            path = generator.generate_docker_env()
            generated['Docker Env'] = path

        else:
            # Default: generate all scripts
            all_scripts = generator.generate_all_scripts()
            generated = {
                'Windows Batch': all_scripts['windows_bat'],
                'Unix Shell': all_scripts['unix_sh'],
                'PowerShell': all_scripts['powershell'],
                'Docker Env': all_scripts['docker_env']
            }

        # Show results
        print(f"Generated {len(generated)} script(s):")
        for script_type, path in generated.items():
            print(f"  {script_type}: {path}")

        print("\nUsage:")
        print("  Windows: call infrastructure\\set_env.bat")
        print("  Unix/Mac: source infrastructure/set_env.sh")
        print("  PowerShell: .\\infrastructure\\set_env.ps1")
        print("  Docker: docker run --env-file infrastructure/.env")
        print("  Auto Setup: python -c \"from infrastructure.settings_loader import setup_environment_from_settings; setup_environment_from_settings()\"")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()