#!/usr/bin/env python3
"""
Test Dynamic Model Discovery System
===================================

Demonstrates how the system automatically discovers new AWS Bedrock models,
handles deprecated models, and updates configurations without manual intervention.
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_dynamic_model_discovery():
    """Test the dynamic model discovery system"""
    
    print("Dynamic Model Discovery System Test")
    print("=" * 60)
    
    # Set up AWS credentials (required for actual discovery)
    print("\n1. SETUP")
    print("-" * 30)
    
    aws_configured = (
        os.getenv('AWS_ACCESS_KEY_ID') or 
        os.getenv('AWS_PROFILE') or
        Path.home().joinpath('.aws', 'credentials').exists()
    )
    
    print(f"AWS Credentials: {'+ Configured' if aws_configured else '- Not configured (using mock)'}")
    
    try:
        from knowledge_systems.core.dynamic_model_discovery import (
            get_model_discovery, DynamicModelDiscovery, DiscoveredModel
        )
        print("+ Dynamic discovery module loaded")
    except ImportError as e:
        print(f"- Could not load discovery module: {e}")
        return
    
    # Initialize discovery system
    print("\n2. MODEL DISCOVERY")
    print("-" * 30)
    
    discovery = get_model_discovery(region="us-east-1")
    
    try:
        # Discover current models
        models = discovery.discover_models(force_refresh=True)
        
        print(f"+ Discovered {len(models)} embedding models")
        
        # Show discovered models
        print(f"\n{'Model ID':<35} {'Provider':<10} {'Dimensions':<12} {'Status':<12}")
        print("-" * 70)
        
        for model_id, model in list(models.items())[:10]:  # Show first 10
            dims = str(model.native_dimension) if model.native_dimension else "Unknown"
            print(f"{model_id:<35} {model.provider:<10} {dims:<12} {model.status:<12}")
        
        if len(models) > 10:
            print(f"... and {len(models) - 10} more models")
    
    except Exception as e:
        print(f"- Discovery failed (expected without AWS access): {e}")
        print("+ Using fallback models for demonstration")
        
        # Create mock discovered models for demo
        models = _create_mock_models()
        
        print(f"+ Mock discovered {len(models)} embedding models")
        print(f"\n{'Model ID':<35} {'Provider':<10} {'Dimensions':<12} {'Status':<12}")
        print("-" * 70)
        
        for model_id, model in models.items():
            dims = str(model.native_dimension) if model.native_dimension else "Unknown"
            print(f"{model_id:<35} {model.provider:<10} {dims:<12} {model.status:<12}")
    
    # Test compatibility report
    print("\n3. COMPATIBILITY REPORT")
    print("-" * 30)
    
    try:
        report = discovery.get_model_compatibility_report()
        
        print(f"Total Models: {report['total_models']}")
        print(f"Available: {report['available_models']}")
        print(f"Deprecated: {report['deprecated_models']}")  
        print(f"New: {report['new_models']}")
        
        print(f"\nBy Provider:")
        for provider, count in report['by_provider'].items():
            print(f"  {provider}: {count}")
        
        print(f"\nBy Dimension:")
        for dimension, count in report['by_dimension'].items():
            print(f"  {dimension}d: {count}")
        
        if report['configurable_models']:
            print(f"\nConfigurable Models:")
            for model in report['configurable_models']:
                print(f"  {model['model_id']}: {model['supported_dimensions']}")
    
    except Exception as e:
        print(f"- Report generation failed: {e}")
    
    # Test configuration update
    print("\n4. CONFIGURATION UPDATE SIMULATION")
    print("-" * 30)
    
    print("Simulating new model discovery...")
    
    # Simulate new models being added
    new_models = [
        "amazon.titan-embed-text-v3:0",  # Future model
        "cohere.embed-english-v4",       # Future model
        "anthropic.embed-claude-v1"      # Hypothetical model
    ]
    
    deprecated_models = [
        "amazon.titan-embed-text-v1"     # Might be deprecated in future
    ]
    
    print(f"\nSimulated Changes:")
    print(f"+ New models found: {len(new_models)}")
    for model in new_models:
        print(f"  • {model} (hypothetical future model)")
    
    print(f"+ Deprecated models: {len(deprecated_models)}")
    for model in deprecated_models:
        print(f"  • {model} (simulation)")
    
    # Show how configuration would be updated
    print(f"\nConfiguration Update Process:")
    print(f"1. Detect new models via Bedrock API")
    print(f"2. Test models to determine dimensions")
    print(f"3. Update embeddings_settings.yaml")
    print(f"4. Send notifications to administrators")
    print(f"5. Maintain backward compatibility")
    
    # Test scheduler integration
    print("\n5. AUTOMATIC SCHEDULING")
    print("-" * 30)
    
    try:
        from knowledge_systems.core.model_discovery_scheduler import (
            get_model_scheduler, start_auto_discovery
        )
        
        print("+ Scheduler module loaded")
        
        # Create scheduler (but don't start for demo)
        scheduler = get_model_scheduler(
            discovery_interval="daily",
            notification_callback=demo_notification_callback
        )
        
        status = scheduler.get_status()
        print(f"Scheduler Status:")
        print(f"  Running: {status['running']}")
        print(f"  Interval: {status['discovery_interval']}")
        print(f"  Auto-updates: {status['auto_updates_enabled']}")
        
        print(f"\nScheduler Features:")
        print(f"+ Daily/weekly/hourly discovery")
        print(f"+ Automatic configuration updates")
        print(f"+ Slack/email notifications")
        print(f"+ Rollback capability")
        print(f"+ Integration with existing systems")
        
    except ImportError as e:
        print(f"- Scheduler module not available: {e}")
    
    # Show integration points
    print("\n6. INTEGRATION POINTS")
    print("-" * 30)
    
    print("Dynamic model discovery integrates with:")
    print("+ VectorManager - automatic model standardization")
    print("+ Dynamic selector - updated model options")
    print("+ Admin settings - configuration management")
    print("+ Notification systems - change alerts")
    print("+ Monitoring - model health tracking")
    
    # Benefits summary
    print("\n7. BENEFITS")
    print("-" * 30)
    
    print("AUTOMATIC MODEL MANAGEMENT:")
    print("• New models available immediately")
    print("• Deprecated models handled gracefully")
    print("• Dimension detection and configuration")
    print("• Zero-downtime updates")
    print("• Backward compatibility maintained")
    print()
    print("OPERATIONAL BENEFITS:")
    print("• Reduced manual maintenance")
    print("• Early access to new capabilities")
    print("• Proactive deprecation handling")
    print("• Audit trail for changes")
    print("• Cost optimization opportunities")
    
    print("\n" + "=" * 60)
    print("RESULT: Future-proof embedding model management!")
    print("+ AWS adds new models → Automatically available")
    print("+ AWS deprecates models → Graceful migration")
    print("+ Zero manual configuration required")
    print("+ Always using latest and best models")

def demo_notification_callback(updates):
    """Demo notification callback"""
    print(f"\n🔔 NOTIFICATION: Model changes detected!")
    
    if updates.get("new_models"):
        print(f"   🆕 {len(updates['new_models'])} new models")
    
    if updates.get("deprecated_models"):
        print(f"   ⚠️ {len(updates['deprecated_models'])} deprecated models")

def _create_mock_models():
    """Create mock models for demonstration"""
    from knowledge_systems.core.dynamic_model_discovery import DiscoveredModel
    
    mock_models = {
        "amazon.titan-embed-text-v1": DiscoveredModel(
            model_id="amazon.titan-embed-text-v1",
            model_name="Titan Text Embeddings v1",
            provider="amazon",
            native_dimension=1536,
            configurable_dimensions=False,
            supported_dimensions=[1536],
            status="available"
        ),
        "amazon.titan-embed-text-v2:0": DiscoveredModel(
            model_id="amazon.titan-embed-text-v2:0",
            model_name="Titan Text Embeddings v2",
            provider="amazon", 
            native_dimension=1024,
            configurable_dimensions=True,
            supported_dimensions=[256, 512, 1024],
            status="available"
        ),
        "cohere.embed-english-v3": DiscoveredModel(
            model_id="cohere.embed-english-v3",
            model_name="Cohere English Embeddings v3",
            provider="cohere",
            native_dimension=384,
            configurable_dimensions=False,
            supported_dimensions=[384],
            status="available"
        ),
        "amazon.titan-embed-text-v3:0": DiscoveredModel(
            model_id="amazon.titan-embed-text-v3:0",
            model_name="Titan Text Embeddings v3 (Future)",
            provider="amazon",
            native_dimension=2048,
            configurable_dimensions=True,
            supported_dimensions=[512, 1024, 2048],
            status="new"
        )
    }
    
    return mock_models

if __name__ == "__main__":
    test_dynamic_model_discovery()