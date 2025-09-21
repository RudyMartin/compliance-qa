#!/usr/bin/env python3
"""
Test Template Field Extraction from Criteria
===========================================

Simple test of the template field extraction system with criteria.json
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any

def test_criteria_extraction():
    """Test extraction of template fields from criteria.json"""

    # Load the criteria.json file
    criteria_file = Path(__file__).parent / "criteria" / "criteria.json"

    if not criteria_file.exists():
        print(f"ERROR: Criteria file not found: {criteria_file}")
        return

    with open(criteria_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("Template Field Extraction Test")
    print("=" * 50)

    # Extract document qualifiers with template_field: true
    print("\nDocument Qualifiers (template_field: true):")
    if 'document_qualifiers' in data:
        qualifiers = data['document_qualifiers']
        for field_name, field_config in qualifiers.items():
            if isinstance(field_config, dict) and field_config.get('template_field', False):
                field_value = field_config.get('value')
                description = field_config.get('description', f"Document qualifier: {field_name}")

                # Determine data type
                data_type = 'string'
                if isinstance(field_value, int):
                    data_type = 'integer'
                elif isinstance(field_value, float):
                    data_type = 'number'
                elif isinstance(field_value, bool):
                    data_type = 'boolean'
                elif isinstance(field_value, list):
                    data_type = 'array'
                elif isinstance(field_value, dict):
                    data_type = 'object'

                print(f"  {field_name}:")
                print(f"    Type: {data_type}")
                print(f"    Default: {field_value}")
                print(f"    Description: {description}")

    # Extract whitepaper fields with template_field: true
    print("\nWhitepaper Fields (template_field: true):")
    if 'whitepaper_fields' in data:
        whitepaper_fields = data['whitepaper_fields']
        for field_name, field_config in whitepaper_fields.items():
            if isinstance(field_config, dict) and field_config.get('template_field', False):
                field_value = field_config.get('value')
                description = field_config.get('description', f"Whitepaper field: {field_name}")

                data_type = 'string'
                if isinstance(field_value, list):
                    data_type = 'array'
                elif isinstance(field_value, dict):
                    data_type = 'object'

                print(f"  {field_name}:")
                print(f"    Type: {data_type}")
                print(f"    Default: {field_value}")
                print(f"    Description: {description}")

    # Extract explicit template_fields
    print("\nExplicit Template Fields:")
    if 'template_fields' in data:
        template_fields_data = data['template_fields']
        if isinstance(template_fields_data, dict):
            for field_name, field_spec in template_fields_data.items():
                if isinstance(field_spec, dict):
                    data_type = field_spec.get('type', 'string')
                    required = field_spec.get('required', True)
                    default = field_spec.get('default')
                    description = field_spec.get('description', f'Template field: {field_name}')

                    print(f"  {field_name}:")
                    print(f"    Type: {data_type}")
                    print(f"    Required: {required}")
                    print(f"    Default: {default}")
                    print(f"    Description: {description}")

                    # Show validation rules if present
                    if 'range' in field_spec:
                        print(f"    Range: {field_spec['range']}")
                    if 'enum' in field_spec:
                        print(f"    Enum: {field_spec['enum']}")
                    if 'pattern' in field_spec:
                        print(f"    Pattern: {field_spec['pattern']}")

    print("\n" + "=" * 50)
    print("Extraction complete!")

if __name__ == "__main__":
    test_criteria_extraction()