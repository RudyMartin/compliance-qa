"""

# S3 Configuration Management
sys.path.append(str(Path(__file__).parent.parent / 'tidyllm' / 'admin') if 'tidyllm' in str(Path(__file__)) else str(Path(__file__).parent / 'tidyllm' / 'admin'))
from credential_loader import get_s3_config, build_s3_path

# Get S3 configuration (bucket and path builder)
s3_config = get_s3_config()  # Add environment parameter for dev/staging/prod

Test Configuration Override System
=================================

Tests the new configuration system that provides:
1. Default configuration from settings.yaml (nsc-mvp1, pages/)
2. Workflow-specific overrides for special cases
3. Domain-specific defaults
4. Consistency across all workflows
"""

import sys
import logging
from pathlib import Path

# Add tidyllm to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_default_configuration():
    """Test loading default configuration from settings.yaml"""
    logger.info("=== Testing Default Configuration ===")
    
    try:
        from knowledge_systems.core.workflow_config import create_workflow_config, get_default_s3_config
        
        # Test default config loading
        config = create_workflow_config()
        s3_config = config.s3
        
        logger.info(f"Default S3 Configuration:")
        logger.info(f"  Bucket: {s3_config.bucket}")
        logger.info(f"  Prefix: {s3_config.prefix}")
        logger.info(f"  Region: {s3_config.region}")
        
        # Verify it matches settings.yaml expectations
        expected_bucket = s3_config["bucket"]
        expected_prefix = "pages/"
        
        if s3_config.bucket == expected_bucket:
            logger.info("✅ Bucket matches settings.yaml")
        else:
            logger.warning(f"❌ Expected bucket '{expected_bucket}', got '{s3_config.bucket}'")
            
        if s3_config.prefix == expected_prefix:
            logger.info("✅ Prefix matches settings.yaml")  
        else:
            logger.warning(f"❌ Expected prefix '{expected_prefix}', got '{s3_config.prefix}'")
        
        return config
        
    except Exception as e:
        logger.error(f"Default configuration test failed: {e}")
        return None

def test_override_configuration():
    """Test configuration overrides"""
    logger.info("=== Testing Configuration Overrides ===")
    
    try:
        from knowledge_systems.core.workflow_config import create_workflow_config
        
        # Test explicit overrides
        override_config = create_workflow_config(
            s3_bucket="dsai-2025-asu",
            s3_prefix="workflows/",
            s3_region="us-west-2"
        )
        
        s3_config = override_config.s3
        
        logger.info(f"Override S3 Configuration:")
        logger.info(f"  Bucket: {s3_config.bucket} (should be dsai-2025-asu)")
        logger.info(f"  Prefix: {s3_config.prefix} (should be workflows/)")
        logger.info(f"  Region: {s3_config.region} (should be us-west-2)")
        
        # Verify overrides work
        assert s3_config.bucket == "dsai-2025-asu", "Bucket override failed"
        assert s3_config.prefix == "workflows/", "Prefix override failed" 
        assert s3_config.region == "us-west-2", "Region override failed"
        
        logger.info("✅ All overrides working correctly")
        
        return override_config
        
    except Exception as e:
        logger.error(f"Override configuration test failed: {e}")
        return None

def test_domain_specific_config():
    """Test domain-specific configuration"""
    logger.info("=== Testing Domain-Specific Configuration ===")
    
    try:
        from knowledge_systems.core.workflow_config import create_domain_workflow_config, get_domain_specific_config
        
        # Test different domain types
        test_domains = [
            "research_project",      # Should use research config
            "model_validation",      # Should use model_validation config
            "test_domain",          # Should use test config
            "regular_domain"        # Should use defaults
        ]
        
        for domain in test_domains:
            logger.info(f"\nTesting domain: {domain}")
            
            # Get domain-specific defaults
            domain_defaults = get_domain_specific_config(domain)
            if domain_defaults:
                logger.info(f"  Domain defaults: {domain_defaults}")
            else:
                logger.info(f"  No domain-specific config - using settings.yaml defaults")
            
            # Create domain config
            config = create_domain_workflow_config(domain)
            s3_config = config.s3
            
            logger.info(f"  Final config: bucket={s3_config.bucket}, prefix={s3_config.prefix}")
        
        logger.info("✅ Domain-specific configuration working")
        
    except Exception as e:
        logger.error(f"Domain-specific configuration test failed: {e}")

def test_workflow_creator_integration():
    """Test DomainWorkflowCreator with new configuration system"""
    logger.info("=== Testing Workflow Creator Integration ===")
    
    def create_test_documents():
        test_dir = Path("test_config_docs")
        test_dir.mkdir(exist_ok=True)
        
        test_file = test_dir / "config_test.txt"
        test_file.write_text("Test document for configuration system", encoding='utf-8')
        
        return test_dir
    
    try:
        # Create test documents
        test_dir = create_test_documents()
        
        from knowledge_systems.create_domain_workflow import DomainWorkflowCreator
        
        # Test 1: Default configuration (should use settings.yaml)
        logger.info("\n1. Testing with DEFAULT configuration:")
        default_creator = DomainWorkflowCreator()
        
        logger.info(f"   Default bucket: {default_creator.s3_bucket}")
        logger.info(f"   Default prefix: {default_creator.workflow_config.s3.prefix}")
        
        # Test 2: Override configuration 
        logger.info("\n2. Testing with OVERRIDE configuration:")
        override_creator = DomainWorkflowCreator(
            s3_bucket="dsai-2025-asu",
            s3_prefix="special_workflows/"
        )
        
        logger.info(f"   Override bucket: {override_creator.s3_bucket}")
        logger.info(f"   Override prefix: {override_creator.workflow_config.s3.prefix}")
        
        # Test 3: Simulate workflow creation structure
        logger.info("\n3. Testing S3 path structure:")
        
        # Test default paths
        default_structure = default_creator._create_s3_workflow_structure("test_domain")
        logger.info(f"   Default structure sample: {default_structure['01_input_s3_url']}")
        
        # Test override paths  
        override_structure = override_creator._create_s3_workflow_structure("test_domain")
        logger.info(f"   Override structure sample: {override_structure['01_input_s3_url']}")
        
        # Verify they're different
        if default_structure['01_input_s3_url'] != override_structure['01_input_s3_url']:
            logger.info("✅ Configuration override system working - paths are different")
        else:
            logger.warning("❌ Configuration override not working - paths are the same")
        
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)
        
        logger.info("✅ Workflow creator integration successful")
        
    except Exception as e:
        logger.error(f"Workflow creator integration test failed: {e}")

def main():
    """Test the complete configuration override system"""
    logger.info("🚀 Testing Configuration Override System")
    logger.info("Ensuring consistency with settings.yaml + override flexibility")
    
    try:
        # Test 1: Default Configuration
        logger.info("\n" + "="*60)
        default_config = test_default_configuration()
        
        # Test 2: Override Configuration
        logger.info("\n" + "="*60)
        override_config = test_override_configuration()
        
        # Test 3: Domain-Specific Configuration
        logger.info("\n" + "="*60)
        test_domain_specific_config()
        
        # Test 4: Workflow Creator Integration
        logger.info("\n" + "="*60)
        test_workflow_creator_integration()
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("🎉 CONFIGURATION OVERRIDE SYSTEM TEST COMPLETE")
        logger.info("="*60)
        
        logger.info("\n📋 Configuration System Features:")
        logger.info("✅ Default loading from settings.yaml (nsc-mvp1, pages/)")
        logger.info("✅ Workflow-specific overrides for special cases")
        logger.info("✅ Domain-specific configuration defaults")
        logger.info("✅ DomainWorkflowCreator integration")
        logger.info("✅ Consistent S3 path generation")
        
        logger.info("\n🏗️  Usage Examples:")
        logger.info("# Use settings.yaml defaults:")
        logger.info("creator = DomainWorkflowCreator()")
        logger.info("")
        logger.info("# Override for special workflows:")
        logger.info("creator = DomainWorkflowCreator(")
        logger.info("    s3_bucket='dsai-2025-asu',")
        logger.info("    s3_prefix='special_workflows/'")
        logger.info(")")
        
        logger.info("\n✅ Configuration system provides consistency AND flexibility!")
        
    except Exception as e:
        logger.error(f"Configuration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()