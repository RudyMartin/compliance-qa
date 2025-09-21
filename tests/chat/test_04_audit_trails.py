#!/usr/bin/env python3
"""
Test 4: Audit Trail Validation
Purpose: Ensure all responses have proper audit trails
Status: READY TO RUN
"""

import tidyllm

def test_audit_trails():
    """Test audit trail completeness and accuracy"""
    print("=== Audit Trail Test ===")

    test_message = "Audit test"
    required_fields = ['timestamp', 'user_id', 'model_id', 'success']

    print("Testing audit trail generation...")

    try:
        response = tidyllm.chat(test_message, chat_type='direct', reasoning=True)

        if isinstance(response, dict):
            audit_trail = response.get('audit_trail', {})

            print(f"Response type: {type(response)}")
            print(f"Has audit_trail field: {'audit_trail' in response}")

            if audit_trail:
                print(f"Audit trail fields: {list(audit_trail.keys())}")

                # Check required fields
                missing_fields = [field for field in required_fields
                                if field not in audit_trail]
                present_fields = [field for field in required_fields
                                if field in audit_trail]

                print(f"Required fields present: {len(present_fields)}/{len(required_fields)}")
                if missing_fields:
                    print(f"Missing fields: {missing_fields}")
                else:
                    print("All required fields present")

                # Validate field values
                validations = {}
                for field in present_fields:
                    value = audit_trail[field]
                    if field == 'timestamp':
                        validations[field] = isinstance(value, str) and len(value) > 10
                    elif field == 'user_id':
                        validations[field] = isinstance(value, str) and len(value) > 0
                    elif field == 'model_id':
                        validations[field] = isinstance(value, str) and len(value) > 0
                    elif field == 'success':
                        validations[field] = isinstance(value, bool)
                    else:
                        validations[field] = True

                # Display validation results
                print("Field validations:")
                for field, is_valid in validations.items():
                    status = "[OK]" if is_valid else "[FAIL]"
                    value = audit_trail[field]
                    print(f"  {status} {field}: {value}")

                # Additional audit fields
                additional_fields = [k for k in audit_trail.keys()
                                   if k not in required_fields]
                if additional_fields:
                    print(f"Additional fields: {additional_fields}")

                audit_complete = len(missing_fields) == 0 and all(validations.values())
                audit_status = "COMPLETE" if audit_complete else "INCOMPLETE"

            else:
                print("No audit trail found")
                audit_status = "MISSING"
                missing_fields = required_fields
                present_fields = []
                validations = {}

        else:
            print(f"Response is not dict: {type(response)}")
            audit_status = "NO_DICT_RESPONSE"
            missing_fields = required_fields
            present_fields = []
            validations = {}

        result = {
            'test_name': 'audit_trails',
            'audit_status': audit_status,
            'required_fields': required_fields,
            'present_fields': present_fields,
            'missing_fields': missing_fields,
            'field_validations': validations,
            'status': 'COMPLETED'
        }

    except Exception as e:
        print(f"ERROR during audit trail test: {e}")
        result = {
            'test_name': 'audit_trails',
            'audit_status': 'ERROR',
            'error': str(e),
            'status': 'ERROR'
        }

    print(f"\nAudit Trail Status: {result['audit_status']}")
    return result

if __name__ == "__main__":
    result = test_audit_trails()
    print(f"\nTest completed: {result['test_name']}")