#!/usr/bin/env python3
"""
Run the MODULAR Flow Creator V3 that uses tabfiles.

This is the recommended way to run Flow Creator - it uses
the modular architecture with separate tabfiles for each feature.

Usage:
    python run_modular.py
    OR
    streamlit run run_modular.py
"""

import sys
from pathlib import Path

# Ensure we can import from current directory
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the modular version
from flow_creator_v3_modular import main

if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING MODULAR FLOW CREATOR V3")
    print("=" * 60)
    print()
    print("This version uses TABFILES (t_ files) for each tab:")
    print("  - t_create_flow.py    -> Create tab")
    print("  - t_existing_flows.py -> Manage tab")
    print("  - t_run.py           -> Run tab")
    print("  - t_test_designer.py  -> Optimize tab")
    print("  - t_ai_advisor.py     -> Ask AI tab")
    print()
    print("Benefits: Modular, maintainable, faster loading")
    print("=" * 60)
    print()

    # Run the modular portal
    main()