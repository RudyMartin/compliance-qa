import os
import re

# Files using numpy
numpy_files = {
    "packages/tidyllm/embedding/faiss_vector_manager.py": "PRODUCTION",
    "packages/tidyllm/embedding/titan_adapter.py": "PRODUCTION", 
    "packages/tidyllm/embedding_validator.py": "NON-PRODUCTION (validator/test)",
    "packages/tidyllm/infrastructure/delegates/embedding_delegate.py": "PRODUCTION",
    "packages/tidyllm/infrastructure/infra_delegate.py": "PRODUCTION",
    "packages/tidyllm/knowledge_systems/adapters/dspy_rag/rl_dspy_adapter.py": "PRODUCTION",
    "packages/tidyllm/services/smart_embedding_service.py": "PRODUCTION",
    "packages/tidyllm/workflows/projects/code_review/code_review_dspy_signature.py": "PRODUCTION",
    "packages/tidyllm/workflows/projects/code_review/code_review_sme.py": "PRODUCTION",
    "packages/tidyllm-sentence/academic_benchmark.py": "NON-PRODUCTION (benchmark)",
    "packages/tidyllm-sentence/benchmark_comparison.py": "NON-PRODUCTION (benchmark)",
    "packages/tidyllm-sentence/benchmark_comparison_ascii.py": "NON-PRODUCTION (benchmark)",
    "packages/tlm/docs/comprehensive_math_validation.py": "NON-PRODUCTION (validation)"
}

print("## NumPy Usage Analysis\n")
print("### PRODUCTION FILES (need tlm replacement):")
for f, t in numpy_files.items():
    if "PRODUCTION" in t and "NON-PRODUCTION" not in t:
        print(f"  - {f}")

print("\n### NON-PRODUCTION FILES (keep numpy for comparison):")
for f, t in numpy_files.items():
    if "NON-PRODUCTION" in t:
        print(f"  - {f}: {t}")
