#!/usr/bin/env python3
"""
Compliance QA Command Line Interface
Main entry point for compliance-qa CLI with help and subcommands
Uses TidyLLM as a library for AI/ML functionality
"""

import argparse
import sys
from pathlib import Path

# Get version from tidyllm library (proper import)
try:
    from packages.tidyllm.interfaces import __version__
except ImportError:
    try:
        from tidyllm.interfaces import __version__
    except ImportError:
        __version__ = "0.1.0"

def show_ecosystem_help():
    """Show comprehensive ecosystem help with available functions."""
    help_text = f"""
Compliance QA Ecosystem - Complete Function Reference
Version: {__version__}
Powered by TidyLLM Library

=== WORKING COMPONENTS ===

TLM (Pure Python ML) - 70 Functions Available:
  Core ML Algorithms:
    tlm.kmeans_fit(data, k=3)           # K-means clustering
    tlm.logreg_fit(X, y)                # Logistic regression  
    tlm.svm_fit(X, y)                   # Support Vector Machine
    tlm.pca_power_fit(X)                # Principal Component Analysis
    tlm.gmm_fit(X, k=3)                 # Gaussian Mixture Models
    tlm.nb_fit(X, y)                    # Naive Bayes

  Math Operations:
    tlm.l2_normalize(vectors)           # L2 normalization
    tlm.dot(vec1, vec2)                 # Dot product
    tlm.matmul(A, B)                    # Matrix multiplication
    tlm.transpose(matrix)               # Matrix transpose

  Neural Network Components:
    tlm.softmax(logits)                 # Softmax activation
    tlm.sigmoid(x)                      # Sigmoid activation
    tlm.multi_head_attention(Q, K, V)   # Attention mechanism

tidyllm-sentence (Educational Embeddings) - 25 Functions Available:
  Embedding Methods:
    tls.tfidf_fit_transform(docs)       # TF-IDF embeddings
    tls.word_avg_fit_transform(docs)    # Word averaging
    tls.lsa_fit_transform(docs)         # Latent Semantic Analysis

  Text Processing:
    tls.word_tokenize(text)             # Word tokenization
    tls.cosine_similarity(v1, v2)       # Cosine similarity
    tls.semantic_search(q, corpus)      # Semantic search

=== STATUS ===
[OK] TLM: 70 pure Python ML functions available
[OK] tidyllm-sentence: 25 embedding functions available
[ERROR] Main TidyLLM: No functional methods (only imports/flags)

=== USAGE EXAMPLES ===

# Pure Python Machine Learning:
import tlm
data = [[1,2], [3,4], [5,6]]
centers, labels, inertia = tlm.kmeans_fit(data, k=2)
normalized = tlm.l2_normalize(data)

# Educational Embeddings:
import tidyllm_sentence as tls
docs = ["Hello world", "Machine learning"]  
embeddings, model = tls.tfidf_fit_transform(docs)
similarity = tls.cosine_similarity(embeddings[0], embeddings[1])

Type 'tidyllm help commands' for CLI command reference.
"""
    print(help_text)

def show_main_help():
    """Show main TidyLLM help with available commands."""
    help_text = f"""
Compliance QA - Enterprise AI Platform
Version: {__version__}
Powered by TidyLLM Library

USAGE:
    compliance-qa <command> [options]

AVAILABLE COMMANDS:

Core Commands:
    help                Show this help message
    help functions      Show all available functions in ecosystem
    version             Show Compliance QA version information
    init                Initialize Compliance QA in current directory
    config              Show current configuration
    status              Show system status and health check

QA Processing:
    qa                  QA file processing commands
    qa-processor        Launch QA processor (alias for qa)
    chat-pdf           Interactive PDF chat mode
    
Testing & Validation:
    test                Run TidyLLM test suites
    test-runner         Launch QA test runner
    validate            Validate TidyLLM installation

Workflow Management:
    workflow            Workflow management commands
    demo                Launch demo interface
    
Development:
    debug               Debug and diagnostic commands
    admin               Administrative commands

EXAMPLES:
    compliance-qa help                    # Show this help
    compliance-qa qa --help              # QA processing help
    compliance-qa chat-pdf document.pdf  # Chat with PDF
    compliance-qa test --all             # Run all tests
    compliance-qa demo                   # Launch demo interface
    compliance-qa status                 # System health check

For detailed help on any command:
    compliance-qa <command> --help

Get started:
    compliance-qa init                   # Initialize Compliance QA
    compliance-qa status                 # Check system health
    compliance-qa demo                   # Try the demo
    
Visit: https://docs.tidyllm.ai for full documentation
"""
    print(help_text)

def show_version():
    """Show version information."""
    print(f"Compliance QA version {__version__}")
    print("Enterprise AI Platform powered by TidyLLM")

    # Show component availability
    try:
        from packages.tidyllm.interfaces import GATEWAYS_AVAILABLE, KNOWLEDGE_SYSTEMS_AVAILABLE, KNOWLEDGE_SERVER_AVAILABLE
        print(f"\nTidyLLM Components:")
        print(f"  Gateways: {'Available' if GATEWAYS_AVAILABLE else 'Not Available'}")
        print(f"  Knowledge Systems: {'Available' if KNOWLEDGE_SYSTEMS_AVAILABLE else 'Not Available'}")
        print(f"  Knowledge Server: {'Available' if KNOWLEDGE_SERVER_AVAILABLE else 'Not Available'}")
    except ImportError:
        try:
            from tidyllm.interfaces import GATEWAYS_AVAILABLE, KNOWLEDGE_SYSTEMS_AVAILABLE, KNOWLEDGE_SERVER_AVAILABLE
            print(f"\nTidyLLM Components:")
            print(f"  Gateways: {'Available' if GATEWAYS_AVAILABLE else 'Not Available'}")
            print(f"  Knowledge Systems: {'Available' if KNOWLEDGE_SYSTEMS_AVAILABLE else 'Not Available'}")
            print(f"  Knowledge Server: {'Available' if KNOWLEDGE_SERVER_AVAILABLE else 'Not Available'}")
        except ImportError:
            print(f"\nTidyLLM Components: Import Error - Check installation")

def init_compliance_qa():
    """Initialize Compliance QA in current directory."""
    print("[INIT] Initializing Compliance QA in current directory...")
    
    # Create standard folders
    folders = ['qa_files', 'qa_reports', 'qa_config', 'workflows', 'knowledge']
    for folder in folders:
        Path(folder).mkdir(exist_ok=True)
        print(f"  Created: {folder}/")
    
    # Create basic config
    config_content = """# Compliance QA Configuration
# Auto-generated configuration file
# Uses TidyLLM as AI/ML library

# QA Processing Settings
qa:
  watch_folder: './qa_files'
  output_folder: './qa_reports'
  config_folder: './qa_config'
  mlflow_enabled: true

# Model Settings  
model:
  default_provider: 'anthropic'
  default_model: 'claude-3-sonnet'
  experiment_prefix: 'tidyllm'

# Integration Settings
integrations:
  aws_enabled: true
  mlflow_enabled: true
  database_enabled: false
"""
    
    config_path = Path('compliance_qa_config.yaml')
    if not config_path.exists():
        with open(config_path, 'w') as f:
            f.write(config_content)
        print(f"  Created: {config_path}")
    else:
        print(f"  Exists: {config_path}")
    
    print("\n[SUCCESS] Compliance QA initialized!")
    print("Next steps:")
    print("  compliance-qa status     # Check system health")
    print("  compliance-qa qa --help  # Learn about QA processing")
    print("  compliance-qa demo       # Try the demo interface")

def show_status():
    """Show system status and health check."""
    print("[STATUS] Compliance QA System Health Check")
    print("=" * 40)

    # Check TidyLLM imports
    try:
        from packages.tidyllm import gateways
        print("[OK] TidyLLM Gateways: Available")

        # Try to init gateways
        gateway_registry = gateways.init_gateways()
        print("[OK] Gateway Registry: Initialized")

    except Exception as e:
        try:
            from tidyllm import gateways
            print("[OK] TidyLLM Gateways: Available")
            gateway_registry = gateways.init_gateways()
            print("[OK] Gateway Registry: Initialized")
        except Exception as e2:
            print(f"[ERROR] TidyLLM Gateways: Error - {e} / {e2}")
    
    # Check MLflow
    try:
        import mlflow
        print(f"[OK] MLflow: Available ({mlflow.__version__})")
        print(f"  Tracking URI: {mlflow.get_tracking_uri()}")
    except ImportError:
        print("[ERROR] MLflow: Not available")
    
    # Check AWS
    try:
        import boto3
        print(f"[OK] AWS SDK: Available ({boto3.__version__})")
    except ImportError:
        print("[ERROR] AWS SDK: Not available")
    
    # Check key dependencies
    deps = {
        'pandas': 'pandas',
        'yaml': 'pyyaml', 
        'dspy': 'dspy-ai',
        'openai': 'openai',
        'anthropic': 'anthropic'
    }
    
    for import_name, package_name in deps.items():
        try:
            module = __import__(import_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"[OK] {package_name}: Available ({version})")
        except ImportError:
            print(f"[ERROR] {package_name}: Not available")
    
    print("\n[RECOMMENDATION]")
    print("If any components show as 'Not available':")
    print("  pip install -e .[all]")

def launch_qa_processor():
    """Launch QA processor with arguments."""
    print("[LAUNCH] Starting QA Processor...")

    # Import and run qa_processor from parent level
    try:
        # QA processor should be at parent level
        import qa_processor
        qa_processor.main()

    except ImportError as e:
        print(f"[ERROR] Could not launch QA processor: {e}")
        print("Ensure qa_processor.py is available in the root directory")
        print("Run 'compliance-qa init' to set up the environment")
        sys.exit(1)

def launch_test_runner():
    """Launch QA test runner with arguments."""
    print("[LAUNCH] Starting QA Test Runner...")

    try:
        # Test runner should be at parent level
        import qa_test_runner
        qa_test_runner.main()

    except ImportError as e:
        print(f"[ERROR] Could not launch test runner: {e}")
        print("Ensure qa_test_runner.py is available in the root directory")
        print("Run 'compliance-qa init' to set up the environment")
        sys.exit(1)

def launch_demo():
    """Launch Compliance QA demo interface."""
    print("[LAUNCH] Starting Compliance QA Demo Interface...")

    try:
        # Try to launch chat portal from parent portals
        import subprocess
        import os

        portal_path = Path(__file__).parent.parent / "portals" / "chat" / "chat_portal.py"
        if portal_path.exists():
            print(f"[INFO] Launching chat portal: {portal_path}")
            os.system(f"streamlit run {portal_path} --server.port 8502")
        else:
            print(f"[ERROR] Chat portal not found at: {portal_path}")

    except Exception as e:
        print(f"[ERROR] Could not launch demo: {e}")
        print("Try manually: streamlit run portals/chat/chat_portal.py --server.port 8502")

def show_config():
    """Show current Compliance QA configuration."""
    print("[CONFIG] Compliance QA Configuration")
    print("=" * 30)

    # Show version and components
    show_version()

    # Show config file if exists
    config_path = Path('compliance_qa_config.yaml')
    if config_path.exists():
        print(f"\nConfiguration file: {config_path}")
        with open(config_path, 'r') as f:
            content = f.read()
        print("\nCurrent configuration:")
        print(content)
    else:
        print(f"\nNo configuration file found at: {config_path}")
        print("Run 'compliance-qa init' to create default configuration")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='compliance-qa',
        description='Compliance QA - Enterprise AI Platform powered by TidyLLM',
        add_help=False  # We'll handle help ourselves
    )
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        show_main_help()
        return
    
    command = sys.argv[1].lower()
    
    # Handle main commands
    if command in ['help', '--help', '-h']:
        # Check if there's a subcommand
        if len(sys.argv) > 2 and sys.argv[2].lower() == 'functions':
            show_ecosystem_help()
        else:
            show_main_help()
    elif command in ['version', '--version', '-v']:
        show_version()
    elif command == 'init':
        init_compliance_qa()
    elif command == 'status':
        show_status()
    elif command == 'config':
        show_config()
    elif command in ['qa', 'qa-processor']:
        # Remove the command from sys.argv and launch QA processor
        sys.argv = ['qa_processor.py'] + sys.argv[2:]
        launch_qa_processor()
    elif command in ['test', 'test-runner']:
        # Remove the command from sys.argv and launch test runner
        sys.argv = ['qa_test_runner.py'] + sys.argv[2:]
        launch_test_runner()
    elif command == 'chat-pdf':
        # Handle chat-pdf command
        if len(sys.argv) < 3:
            print("[ERROR] chat-pdf requires a PDF file argument")
            print("Usage: tidyllm chat-pdf <file.pdf>")
            sys.exit(1)
        
        pdf_file = sys.argv[2]
        sys.argv = ['qa_processor.py', '--chat-pdf', pdf_file] + sys.argv[3:]
        launch_qa_processor()
    elif command == 'demo':
        launch_demo()
    elif command == 'workflow':
        print("[INFO] Workflow management commands coming soon!")
        print("For now, use: python -m tidyllm.workflows")
    elif command == 'debug':
        # Launch QA processor in debug mode
        sys.argv = ['qa_processor.py', '--debug-config'] + sys.argv[2:]
        launch_qa_processor()
    elif command == 'admin':
        print("[INFO] Admin commands coming soon!")
        print("For now, use: python -m tidyllm.admin")
    elif command == 'validate':
        # Run validation/health check
        show_status()
    else:
        print(f"[ERROR] Unknown command: '{command}'")
        print("Run 'tidyllm help' to see available commands")
        sys.exit(1)

if __name__ == '__main__':
    main()