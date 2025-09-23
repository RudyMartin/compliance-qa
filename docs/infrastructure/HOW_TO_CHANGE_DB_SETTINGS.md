# How to Change Database Settings

## ⚠️ IMPORTANT: Use the Setup Portal FIRST!

### Step 1: Use the Setup Portal (RECOMMENDED)
```bash
# Launch the setup portal
cd portals/setup
streamlit run lean_setup_portal.py

# Or use the direct command
python -m streamlit run portals/setup/lean_setup_portal.py
```

The Setup Portal provides:
- ✅ Visual interface for configuration
- ✅ Real-time connection testing
- ✅ Validation before saving
- ✅ No manual YAML editing
- ✅ Prevents syntax errors

---

## Step 2: If Portal Is Not Available (Manual Fallback)

### Understanding the Database Configuration Structure

```yaml
databases:
  # Shared defaults (inheritance base)
  _defaults:
    host: your-postgres-server.com
    port: 5432
    ssl_mode: require

  # Application database
  postgres_std:
    <<: *defaults  # Inherits from _defaults
    database: app_db
    username: app_user
    password: ${POSTGRES_PASSWORD}

  # MLflow database
  postgres_mlflow:
    <<: *defaults  # Same server, different database
    database: mlflow_db
    username: ${MLFLOW_USER:-app_user}
    password: ${MLFLOW_PASSWORD:-${POSTGRES_PASSWORD}}

  # Vector database
  postgres_vector:
    <<: *defaults
    database: vector_db
    username: ${VECTOR_USER:-app_user}
    password: ${VECTOR_PASSWORD:-${POSTGRES_PASSWORD}}
```

---

## Common Database Changes

### 1. Moving ALL Databases to New Server

**Use Portal**: Database tab → Change host in "Primary Database" section

**Manual**: Edit `infrastructure/settings.yaml`:
```yaml
databases:
  _defaults:
    host: new-server.rds.amazonaws.com  # Change here - affects all!
    port: 5432
```

### 2. Moving ONLY MLflow to Different Server

**Use Portal**: Database tab → MLflow section → Override host

**Manual**: Edit `infrastructure/settings.yaml`:
```yaml
databases:
  postgres_mlflow:
    <<: *defaults
    host: mlflow-dedicated-server.com  # Override just for MLflow
    database: mlflow_db
```

### 3. Changing Database Password

**Use Portal**: Database tab → Enter new password → Test Connection → Save

**Manual**:
```bash
# Set environment variable (preferred)
export POSTGRES_PASSWORD="new-secure-password"

# Or update settings.yaml (be careful!)
databases:
  postgres_std:
    password: ${POSTGRES_PASSWORD:-new-default-password}
```

### 4. Adding Connection Pool Settings

**Use Portal**: Database tab → Advanced Settings → Pool Configuration

**Manual**:
```yaml
databases:
  postgres_std:
    connection_pool:
      min_connections: 5      # Minimum idle connections
      max_connections: 30     # Maximum total connections
      pool_timeout: 30        # Timeout in seconds
      pool_recycle: 3600      # Recycle connections after 1 hour
```

---

## Testing Your Changes

### After Portal Changes:
The portal automatically tests connections before saving!

### After Manual Changes:

1. **Test Database Connection**:
```bash
python functionals/setup/tests/test_setup_portal.py
```

2. **Check MLflow Connection**:
```bash
# MLflow will use postgres_mlflow settings
mlflow ui --backend-store-uri postgresql://...
```

3. **Verify All Services**:
```bash
python test_updated_credentials.py
```

---

## Environment-Specific Settings

### Development
```bash
export DB_ENV=development
export POSTGRES_HOST=localhost
export POSTGRES_PASSWORD=dev_password
```

### Staging
```bash
export DB_ENV=staging
export POSTGRES_HOST=staging.rds.amazonaws.com
export POSTGRES_PASSWORD=staging_password
```

### Production
```bash
export DB_ENV=production
export POSTGRES_HOST=prod.rds.amazonaws.com
export POSTGRES_PASSWORD=prod_secure_password
```

---

## Troubleshooting

### Problem: "Could not translate host name"
**Cause**: Database host doesn't exist or DNS issue

**Fix via Portal**:
- Database tab → Verify host address → Test Connection

**Fix Manually**:
```yaml
# Check the host is correct
databases:
  postgres_mlflow:
    host: localhost  # Use valid host, not non-existent RDS
```

### Problem: "FATAL: password authentication failed"
**Cause**: Wrong password

**Fix via Portal**:
- Database tab → Re-enter password → Test Connection

**Fix Manually**:
```bash
# Update environment variable
export POSTGRES_PASSWORD="correct-password"

# Or check settings.yaml
```

### Problem: "database does not exist"
**Cause**: Database name wrong or not created

**Fix via Portal**:
- Database tab → Verify database name exists

**Fix Manually**:
```yaml
databases:
  postgres_std:
    database: vectorqa  # Must exist on server
```

### Problem: MLflow falls back to SQLite
**Cause**: Can't connect to PostgreSQL

**Fix via Portal**:
- Database tab → MLflow section → Test MLflow Connection

**Fix Manually**:
- Check `postgres_mlflow` settings
- Ensure host is reachable
- Verify credentials

---

## Best Practices

1. **ALWAYS use the Setup Portal when available** - It validates before saving!

2. **Use environment variables for passwords**:
   ```bash
   export POSTGRES_PASSWORD="secure-password"
   export MLFLOW_PASSWORD="mlflow-password"
   ```

3. **Test connections after changes**:
   - Portal does this automatically
   - Manual changes need explicit testing

4. **Keep inheritance structure**:
   - Shared settings in `_defaults`
   - Override only what's different

5. **Document your changes**:
   ```yaml
   databases:
     postgres_mlflow:
       host: new-mlflow.com  # Changed 2025-09-20 for dedicated MLflow server
   ```

---

## Quick Reference

| What to Change | Where in Portal | Where in YAML | Environment Variable |
|---------------|-----------------|---------------|---------------------|
| All DB hosts | Database tab → Primary Host | `_defaults.host` | `POSTGRES_HOST` |
| App database name | Database tab → Application DB | `postgres_std.database` | `POSTGRES_DATABASE` |
| MLflow database | Database tab → MLflow section | `postgres_mlflow.database` | `MLFLOW_DATABASE` |
| Password | Database tab → Password field | `password:` | `POSTGRES_PASSWORD` |
| Connection pool | Database tab → Advanced | `connection_pool:` | N/A |

---

## Security Notes

⚠️ **NEVER commit passwords to git!**

✅ **DO**: Use environment variables
✅ **DO**: Use the Setup Portal (masks passwords)
✅ **DO**: Use `.env` files (add to .gitignore)

❌ **DON'T**: Hardcode passwords in settings.yaml
❌ **DON'T**: Commit .env files
❌ **DON'T**: Share credentials in logs

---

## Need Help?

1. **Check current settings**:
   ```bash
   python test_updated_credentials.py
   ```

2. **View active configuration**:
   ```bash
   python -c "from infrastructure.yaml_loader import SettingsLoader; import json; loader = SettingsLoader(); print(json.dumps(loader.get_database_config(), indent=2))"
   ```

3. **Test with Setup Portal**:
   - Launch portal
   - Go to Database tab
   - Use "Test Connection" button

Remember: **The Setup Portal is your friend - use it first!**