#!/usr/bin/env python3
"""
Test Embedding Standardization for Multi-Model Support
======================================================

Demonstrates how to standardize embeddings from different models
to a unified dimension (1024) for consistent vector storage.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from knowledge_systems.core.embedding_config import (
    EMBEDDING_MODELS,
    EmbeddingStandardizer,
    standardize_embedding,
    get_target_dimension
)

def test_embedding_standardization():
    """Test embedding standardization across different models"""
    
    print("Embedding Standardization Test")
    print("=" * 60)
    
    # Initialize standardizer
    standardizer = EmbeddingStandardizer(target_dimension=1024)
    
    print(f"\nTarget Dimension: {standardizer.target_dimension}")
    print(f"Padding Strategy: {standardizer.padding_strategy}")
    
    # Show dimension summary
    summary = standardizer.get_dimension_summary()
    
    print(f"\n{'Model':<25} {'Native Dim':<12} {'Action':<10} {'Difference':<10}")
    print("-" * 60)
    
    for model_key, info in summary["models"].items():
        model_config = EMBEDDING_MODELS[model_key]
        print(f"{model_config.display_name:<25} {info['native']:<12} {info['action']:<10} {info['difference']:<10}")
    
    # Test standardization for each model type
    print("\n" + "=" * 60)
    print("STANDARDIZATION EXAMPLES")
    print("=" * 60)
    
    test_cases = [
        ("cohere_english", 384),      # Needs padding (384 -> 1024)
        ("titan_v2_256", 256),         # Needs padding (256 -> 1024)  
        ("titan_v2_512", 512),         # Needs padding (512 -> 1024)
        ("titan_v2", 1024),            # No change (1024 -> 1024)
        ("titan_v1", 1536),            # Needs truncation (1536 -> 1024)
        ("openai_small", 1536),        # Needs truncation (1536 -> 1024)
        ("openai_large", 3072),        # Needs truncation (3072 -> 1024)
    ]
    
    for model_key, native_dim in test_cases:
        # Create mock embedding of native dimension
        mock_embedding = [0.1 * i for i in range(native_dim)]
        
        # Standardize it
        standardized = standardizer.standardize(mock_embedding, model_key)
        
        model_info = EMBEDDING_MODELS[model_key]
        print(f"\n{model_info.display_name}:")
        print(f"  Input dimension:  {len(mock_embedding)}")
        print(f"  Output dimension: {len(standardized)}")
        
        if len(mock_embedding) < 1024:
            # Check padding
            non_zero_count = sum(1 for v in standardized if v != 0.0)
            padding_count = len(standardized) - non_zero_count
            print(f"  Padded with {padding_count} zeros")
        elif len(mock_embedding) > 1024:
            # Check truncation
            print(f"  Truncated by {len(mock_embedding) - len(standardized)} dimensions")
        else:
            print(f"  No change needed")
    
    # Test different padding strategies
    print("\n" + "=" * 60)
    print("PADDING STRATEGIES")
    print("=" * 60)
    
    strategies = ["zeros", "random", "repeat"]
    test_embedding = [0.5, 0.3, 0.7]  # Small 3D vector
    
    for strategy in strategies:
        standardizer_test = EmbeddingStandardizer(target_dimension=10, padding_strategy=strategy)
        padded = standardizer_test._pad_embedding(test_embedding, 10)
        
        print(f"\nStrategy: {strategy}")
        print(f"  Original: {test_embedding}")
        print(f"  Padded:   {padded}")
    
    # pgvector configuration example
    print("\n" + "=" * 60)
    print("PGVECTOR CONFIGURATION")
    print("=" * 60)
    
    print(f"\nFor pgvector, create table with dimension {get_target_dimension()}:")
    print(f"""
    CREATE TABLE document_embeddings (
        id SERIAL PRIMARY KEY,
        document_id UUID,
        chunk_text TEXT,
        embedding vector({get_target_dimension()}),  -- Standardized dimension
        model_used VARCHAR(50),     -- Track which model was used
        native_dimension INTEGER,   -- Original dimension before padding
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)
    
    print("\nUsage in code:")
    print("""
    # When storing embeddings:
    raw_embedding = bedrock_client.get_embedding(text, model="titan_v2_256")  # 256 dims
    standardized = standardize_embedding(raw_embedding, "titan_v2_256")       # 1024 dims
    
    # Store in pgvector:
    cursor.execute(
        "INSERT INTO document_embeddings (embedding, model_used, native_dimension) VALUES (%s, %s, %s)",
        (standardized, "titan_v2_256", 256)
    )
    """)
    
    print("\n" + "=" * 60)
    print("BENEFITS")
    print("=" * 60)
    print("+ Single vector table for all models")
    print("+ Consistent dimension for similarity search")
    print("+ Can mix embeddings from different models")
    print("+ Easy to query across all embeddings")
    print("+ Simplified index management")
    
    print("\n" + "=" * 60)
    print("CONSIDERATIONS")
    print("=" * 60)
    print("- Padding adds storage overhead for small models")
    print("- Truncation may lose information for large models")
    print("- Consider separate tables if dimension differences are extreme")
    print("- Track native dimension for debugging/analysis")

if __name__ == "__main__":
    test_embedding_standardization()