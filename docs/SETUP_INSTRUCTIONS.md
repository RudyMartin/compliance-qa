# QA-Shipping Setup Instructions

## Quick Start

### Option 1: Automatic Setup (Recommended)
```bash
# Load credentials from settings.yaml automatically
python -c "from infrastructure.yaml_loader import setup_environment_from_settings; setup_environment_from_settings()"
python -m streamlit run portals/setup/setup_portal.py --server.port 8512
```

### Option 2: Generate and Use Environment Scripts
```bash
# Generate all platform-specific scripts from settings.yaml
python infrastructure/make_scripts.py

# Then use the appropriate script for your platform:
```

**Windows:**
```cmd
call infrastructure\set_env.bat
python -m streamlit run portals\setup\setup_portal.py --server.port 8512
```

**Linux/Mac:**
```bash
source infrastructure/set_env.sh
python -m streamlit run portals/setup/setup_portal.py --server.port 8512
```

**PowerShell:**
```powershell
.\infrastructure\set_env.ps1
python -m streamlit run portals\setup\setup_portal.py --server.port 8512
```

## Access Points

- **Setup Portal**: http://localhost:8512
- **Health Check**: http://localhost:8512/?health=true

## Architecture Overview

QA-Shipping uses a clean 4-layer architecture:

```
qa-shipping/
├── portals/              # [UI] PRESENTATION LAYER
│   └── setup/           # Setup Portal (8512)
├── packages/             # [PKG] DOMAIN PACKAGES
│   ├── tidyllm/         # Core business logic
│   ├── tlm/             # TLM core functionality
│   └── tidyllm-sentence/ # Sentence processing logic
├── adapters/             # [ADP] INFRASTRUCTURE ADAPTERS
│   └── session/         # Unified session management
├── common/               # [CMN] COMMON UTILITIES
│   └── utilities/       # Path management, shared tools
└── infrastructure/       # [INFRA] INFRASTRUCTURE LAYER
    ├── environment_manager.py
    ├── credential_validator.py
    ├── portal_config.py
    ├── yaml_loader.py
    └── settings.yaml    # Configuration file
```

## Configuration

### Settings File
Configuration is loaded from `infrastructure/settings.yaml` which contains:
- Database credentials (PostgreSQL)
- AWS credentials and settings
- MLflow configuration
- S3 bucket settings

### Environment Variables
The system supports both automatic loading from YAML and manual environment variables:

**Database:**
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USERNAME`
- `DB_PASSWORD`

**AWS:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`

**MLflow:**
- `MLFLOW_TRACKING_URI`

## Verification

After setup, verify the system:

1. **Check Setup Portal**: http://localhost:8512
2. **Run System Diagnostics**: Use the Setup Portal's diagnostic features
3. **Validate Connections**: Database, AWS, and MLflow connectivity

## Features

### Setup Portal Features
- **[STATUS] System Status**: Real-time health monitoring
- **[ENV] Environment Configuration**: View current settings
- **[CRED] Credential Management**: Secure credential validation
- **[PORTAL] Portal Management**: Manage all portal services
- **[ARCH] Architecture Information**: View 4-layer structure

### Infrastructure Features
- **Settings Loader**: YAML-based configuration
- **Environment Manager**: Centralized credential management
- **Credential Validator**: Async validation of all services
- **Portal Config**: Registry and orchestration of portals
- **Unified Session Manager**: S3, Bedrock, PostgreSQL sessions

## Script Generation Utility

### Make Scripts CLI
```bash
# Generate all environment scripts
python infrastructure/make_scripts.py

# Generate specific script types
python infrastructure/make_scripts.py --windows     # Windows batch only
python infrastructure/make_scripts.py --unix        # Unix shell only
python infrastructure/make_scripts.py --powershell  # PowerShell only
python infrastructure/make_scripts.py --docker      # Docker .env only

# Utility commands
python infrastructure/make_scripts.py --info        # Show configuration info
python infrastructure/make_scripts.py --validate    # Validate existing scripts
```

### Benefits of Generated Scripts
- **Always Current**: Scripts reflect latest settings.yaml configuration
- **Platform Specific**: Optimized for Windows, Linux/Mac, PowerShell, Docker
- **Built-in Testing**: Automatic connectivity validation
- **Comprehensive**: Includes database, AWS, MLflow, and S3 settings

## Troubleshooting

### Common Issues

**Database Connection Error (localhost vs AWS RDS):**
```bash
# Error: connection to server at "localhost" failed
# Solution: Ensure environment variables are set before running
python infrastructure/make_scripts.py                    # Generate fresh scripts
call infrastructure\set_env.bat                          # Windows
# OR
source infrastructure/set_env.sh                         # Linux/Mac
# Then verify environment
echo $DB_HOST                                            # Should show AWS RDS host
```

**Import Errors:**
```bash
# Ensure you're in the qa-shipping directory
cd qa-shipping
python -c "from infrastructure.yaml_loader import setup_environment_from_settings"
```

**Credential Issues:**
```bash
# Verify settings.yaml exists and has correct structure
ls infrastructure/settings.yaml
python -c "from infrastructure.yaml_loader import get_settings_loader; print(get_settings_loader().get_settings_summary())"
```

**Portal Not Starting:**
```bash
# Check if port 8512 is available
netstat -an | grep 8512
# Or try alternative port
python -m streamlit run portals/setup/setup_portal.py --server.port 8513
```

**Environment Variables Not Set:**
```bash
# Check current environment
python infrastructure/make_scripts.py --info
# Regenerate scripts with latest settings
python infrastructure/make_scripts.py --all
# Validate script generation
python infrastructure/make_scripts.py --validate
```

## Architecture Compliance

✅ **Hexagonal Architecture Principles:**
- Physical layer separation
- Dependency inversion (Presentation → Infrastructure → Domain)
- Clean boundaries between layers
- External presentation layer (outside core packages)

✅ **Cross-Platform Compatibility:**
- ASCII-compatible interface elements
- Windows and Linux/Mac environment scripts
- Universal path management

✅ **Security Best Practices:**
- No hardcoded credentials
- Environment variable fallbacks
- Secure credential loading from YAML
- Connection validation and health checks

## Next Steps

1. **Portal Migration**: Move remaining portals to external presentation layer
2. **Infrastructure Completion**: Migrate remaining adapters to adapters layer
3. **Service Layer**: Add service abstractions between infrastructure and domain
4. **Portal Orchestration**: Implement service discovery and load balancing