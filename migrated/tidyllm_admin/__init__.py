"""
TidyLLM Admin Backend - Configuration and Management System

Repurposed from tidyllm-demos for backend administration.
Provides centralized configuration management for the complete TidyLLM ecosystem.

Features:
- Configuration management for all 9 integrated modules
- Database settings (PostgreSQL, MLFlow)
- Gateway control and monitoring
- Enterprise settings and compliance
- Audit logging and monitoring
- Multi-environment support (dev/staging/prod)

Backend Components:
- ConfigManager: Centralized settings management
- GatewayControl: MLFlow gateway administration  
- DatabaseAdmin: PostgreSQL and MLFlow DB management
- ComplianceMonitor: Enterprise compliance monitoring
- AuditLogger: Complete audit trail management
"""

# Core admin functionality
try:
    from ..tidyllm.infrastructure import ConfigManager, GatewayController, GatewayMonitor
    # Local functions that stayed in admin
    try:
        from .config_manager import load_config, save_config
    except ImportError:
        load_config, save_config = None, None
    try:
        from .gateway_control import create_gateway_controller
    except ImportError:
        create_gateway_controller = None
    ADMIN_CORE_AVAILABLE = True
except ImportError:
    ConfigManager = None
    GatewayController = None  
    create_gateway_controller = None
    load_config = None
    save_config = None
    ADMIN_CORE_AVAILABLE = False

# Optional components (not critical for core functionality)
try:
    from .database_admin import DatabaseAdmin, ConnectionTester
    DATABASE_ADMIN_AVAILABLE = True
except ImportError:
    DatabaseAdmin = None
    ConnectionTester = None
    DATABASE_ADMIN_AVAILABLE = False

try:
    from .compliance_monitor import ComplianceMonitor, AuditLogger  
    COMPLIANCE_MONITOR_AVAILABLE = True
except ImportError:
    ComplianceMonitor = None
    AuditLogger = None
    COMPLIANCE_MONITOR_AVAILABLE = False

# Settings management
try:
    from .settings import (
        TidyLLMSettings,
        PostgreSQLSettings, 
        AWSSettings,
        GatewaySettings,
        ComplianceSettings,
        get_default_settings,
        validate_settings
    )
    SETTINGS_AVAILABLE = True
except ImportError:
    TidyLLMSettings = None
    get_default_settings = None
    SETTINGS_AVAILABLE = False

__version__ = "0.1.0"
__author__ = "Rudy Martin"

__all__ = [
    # Core admin classes  
    "ConfigManager",
    "GatewayController",
    "GatewayMonitor", 
    "create_gateway_controller",
    
    # Settings classes
    "TidyLLMSettings",
    "PostgreSQLSettings",
    "AWSSettings", 
    "GatewaySettings",
    "ComplianceSettings",
    
    # Utility functions
    "load_config", 
    "save_config",
    "get_default_settings",
    "validate_settings",
    
    # Feature flags
    "ADMIN_CORE_AVAILABLE",
    "SETTINGS_AVAILABLE"
]

# Package metadata
DESCRIPTION = "TidyLLM Admin Backend - Configuration and Management System"
PURPOSE = "Centralized administration for complete TidyLLM ecosystem"