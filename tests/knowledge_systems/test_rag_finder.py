#!/usr/bin/env python3
"""
Test RAG Finder - Find Your Real RAGs
====================================

Test script to find your actual RAG collections using the existing adapter.
"""

def test_postgres_rag_adapter():
    """Test the PostgresRAGAdapter to find real collections."""
    print("Testing PostgresRAGAdapter to find your real RAG collections...")

    try:
        from rag_adapters.postgres_rag_adapter import PostgresRAGAdapter
        print("✅ Successfully imported PostgresRAGAdapter")

        # Initialize adapter
        adapter = PostgresRAGAdapter()
        print("✅ Successfully initialized PostgresRAGAdapter")

        # Check if SME system is available
        if hasattr(adapter, 'sme_system') and adapter.sme_system:
            print("✅ SME system is available")

            # Try to list collections
            collections = adapter.sme_system.list_collections()
            print(f"✅ Got response from list_collections(): {type(collections)}")

            if collections:
                print(f"🎉 FOUND {len(collections)} REAL RAG COLLECTIONS:")
                print("=" * 60)

                for i, collection in enumerate(collections, 1):
                    print(f"\n{i}. RAG Collection:")
                    print(f"   Name: {collection.get('collection_name', 'Unknown')}")
                    print(f"   ID: {collection.get('collection_id', 'Unknown')}")
                    print(f"   Description: {collection.get('description', 'No description')}")
                    print(f"   Created: {collection.get('created_at', 'Unknown')}")

                    # Check settings for V2 metadata
                    settings = collection.get('settings', {})
                    if settings:
                        print(f"   Settings: {settings}")

                return collections
            else:
                print("❌ No collections found")
                print("   Either no RAGs were created or connection failed")

        else:
            print("❌ SME system not available in adapter")

    except ImportError as e:
        print(f"❌ Import failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    return []

def test_direct_sme_system():
    """Test direct access to SME system."""
    print("\n" + "=" * 60)
    print("Testing direct SME system access...")

    try:
        from _sme_rag_system import SMERAGSystem
        print("✅ Successfully imported SMERAGSystem")

        sme_system = SMERAGSystem()
        print("✅ Successfully initialized SMERAGSystem")

        collections = sme_system.list_collections()
        print(f"✅ Got {len(collections) if collections else 0} collections from direct SME system")

        return collections

    except ImportError as e:
        print(f"❌ Direct SME import failed: {e}")
    except Exception as e:
        print(f"❌ Direct SME error: {e}")

    return []

if __name__ == "__main__":
    print("RAG FINDER - Finding Your Real RAG Collections")
    print("=" * 60)

    # Test 1: PostgresRAGAdapter
    postgres_collections = test_postgres_rag_adapter()

    # Test 2: Direct SME system
    direct_collections = test_direct_sme_system()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"PostgresRAGAdapter found: {len(postgres_collections)} collections")
    print(f"Direct SME system found: {len(direct_collections)} collections")

    if postgres_collections or direct_collections:
        print("🎉 SUCCESS: Found your real RAG collections!")
    else:
        print("❌ No RAG collections found")
        print("   Check if:")
        print("   - Database is running")
        print("   - Collections were actually created")
        print("   - Connection settings are correct")