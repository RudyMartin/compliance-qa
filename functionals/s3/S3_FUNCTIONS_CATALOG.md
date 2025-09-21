# S3 Functions Catalog

## Core S3 Service Functions (infrastructure/services/s3_service.py)

### 1. S3Service Class

#### Constructor
```python
def __init__(self, config: Optional[Dict] = None)
```
- **Purpose**: Initialize S3 service with configuration
- **Parameters**:
  - `config` (Optional[Dict]): Configuration dictionary
- **Config Keys**:
  - `region` (str): AWS region (default: 'us-east-1' or AWS_REGION env)
  - `bucket` (str): Default S3 bucket (or S3_BUCKET env)
  - `access_key_id` (str): AWS access key (optional, uses env if not provided)
  - `secret_access_key` (str): AWS secret key (optional, uses env if not provided)

#### is_available()
```python
def is_available(self) -> bool
```
- **Purpose**: Check if S3 service is available
- **Returns**: bool - True if boto3 and clients are initialized

#### upload_file()
```python
def upload_file(self, file_path: str, s3_key: str, bucket: Optional[str] = None) -> bool
```
- **Purpose**: Upload a file to S3
- **Parameters**:
  - `file_path` (str): Local file path
  - `s3_key` (str): S3 object key
  - `bucket` (Optional[str]): S3 bucket (uses default if not provided)
- **Returns**: bool - True if successful

#### download_file()
```python
def download_file(self, s3_key: str, local_path: str, bucket: Optional[str] = None) -> bool
```
- **Purpose**: Download a file from S3
- **Parameters**:
  - `s3_key` (str): S3 object key
  - `local_path` (str): Local file path to save to
  - `bucket` (Optional[str]): S3 bucket (uses default if not provided)
- **Returns**: bool - True if successful

#### list_objects()
```python
def list_objects(self, prefix: str = "", bucket: Optional[str] = None) -> List[str]
```
- **Purpose**: List objects in S3 bucket
- **Parameters**:
  - `prefix` (str): Prefix to filter objects
  - `bucket` (Optional[str]): S3 bucket (uses default if not provided)
- **Returns**: List[str] - List of object keys

#### read_json()
```python
def read_json(self, s3_key: str, bucket: Optional[str] = None) -> Optional[Dict]
```
- **Purpose**: Read a JSON file from S3
- **Parameters**:
  - `s3_key` (str): S3 object key
  - `bucket` (Optional[str]): S3 bucket (uses default if not provided)
- **Returns**: Optional[Dict] - Parsed JSON data or None

#### write_json()
```python
def write_json(self, data: Dict, s3_key: str, bucket: Optional[str] = None) -> bool
```
- **Purpose**: Write JSON data to S3
- **Parameters**:
  - `data` (Dict): Data to write as JSON
  - `s3_key` (str): S3 object key
  - `bucket` (Optional[str]): S3 bucket (uses default if not provided)
- **Returns**: bool - True if successful

#### exists()
```python
def exists(self, s3_key: str, bucket: Optional[str] = None) -> bool
```
- **Purpose**: Check if an S3 object exists
- **Parameters**:
  - `s3_key` (str): S3 object key
  - `bucket` (Optional[str]): S3 bucket (uses default if not provided)
- **Returns**: bool - True if object exists

#### delete()
```python
def delete(self, s3_key: str, bucket: Optional[str] = None) -> bool
```
- **Purpose**: Delete an S3 object
- **Parameters**:
  - `s3_key` (str): S3 object key
  - `bucket` (Optional[str]): S3 bucket (uses default if not provided)
- **Returns**: bool - True if successful

#### get_presigned_url()
```python
def get_presigned_url(self, s3_key: str, expires_in: int = 3600, bucket: Optional[str] = None) -> Optional[str]
```
- **Purpose**: Generate a presigned URL for S3 object
- **Parameters**:
  - `s3_key` (str): S3 object key
  - `expires_in` (int): URL expiration time in seconds (default: 3600)
  - `bucket` (Optional[str]): S3 bucket (uses default if not provided)
- **Returns**: Optional[str] - Presigned URL or None

### 2. Module Functions

#### get_s3_service()
```python
def get_s3_service(config: Optional[Dict] = None) -> S3Service
```
- **Purpose**: Get the singleton S3 service instance
- **Parameters**:
  - `config` (Optional[Dict]): Optional configuration dictionary
- **Returns**: S3Service instance

#### inject_s3_config()
```python
def inject_s3_config(config: Dict)
```
- **Purpose**: Inject S3 configuration for child packages
- **Parameters**:
  - `config` (Dict): Configuration dictionary
- **Returns**: S3Service instance

## S3 Delegate Functions (packages/tidyllm/infrastructure/s3_delegate.py)

### S3Delegate Class
This class delegates all operations to the parent infrastructure's S3Service.

#### Methods (all delegate to parent)
- `__init__(config: Optional[Dict] = None)`
- `is_available() -> bool`
- `upload_file(file_path: str, s3_key: str, bucket: Optional[str] = None) -> bool`
- `download_file(s3_key: str, local_path: str, bucket: Optional[str] = None) -> bool`
- `list_objects(prefix: str = "", bucket: Optional[str] = None) -> List[str]`
- `read_json(s3_key: str, bucket: Optional[str] = None) -> Optional[Dict]`
- `write_json(data: Dict, s3_key: str, bucket: Optional[str] = None) -> bool`
- `exists(s3_key: str, bucket: Optional[str] = None) -> bool`
- `delete(s3_key: str, bucket: Optional[str] = None) -> bool`
- `get_presigned_url(s3_key: str, expires_in: int = 3600, bucket: Optional[str] = None) -> Optional[str]`

#### Module Functions
```python
def get_s3_delegate(config: Optional[Dict] = None) -> S3Delegate
```

#### Compatibility Functions
```python
def get_s3_config() -> Dict[str, Any]
def build_s3_path(*args) -> str
```

## AWS Service S3 Functions (infrastructure/services/aws_service.py)

### AWSService Class S3 Methods

#### get_s3_client()
```python
def get_s3_client(self)
```
- **Purpose**: Get or create S3 client (lazy initialization)
- **Returns**: boto3 S3 client or None

#### upload_file()
```python
def upload_file(self, file_path: str, s3_key: str, bucket: Optional[str] = None) -> bool
```
- **Purpose**: Upload file to S3
- **Returns**: True if successful

#### download_file()
```python
def download_file(self, s3_key: str, local_path: str, bucket: Optional[str] = None) -> bool
```
- **Purpose**: Download file from S3
- **Returns**: True if successful

#### list_s3_objects()
```python
def list_s3_objects(self, prefix: str = "", bucket: Optional[str] = None) -> List[str]
```
- **Purpose**: List objects in S3 bucket
- **Returns**: List of object keys

#### read_json_from_s3()
```python
def read_json_from_s3(self, s3_key: str, bucket: Optional[str] = None) -> Optional[Dict]
```
- **Purpose**: Read JSON from S3
- **Returns**: Parsed JSON or None

#### write_json_to_s3()
```python
def write_json_to_s3(self, data: Dict, s3_key: str, bucket: Optional[str] = None) -> bool
```
- **Purpose**: Write JSON to S3
- **Returns**: True if successful

#### s3_object_exists()
```python
def s3_object_exists(self, s3_key: str, bucket: Optional[str] = None) -> bool
```
- **Purpose**: Check if S3 object exists
- **Returns**: True if exists

#### delete_s3_object()
```python
def delete_s3_object(self, s3_key: str, bucket: Optional[str] = None) -> bool
```
- **Purpose**: Delete S3 object
- **Returns**: True if successful

#### get_s3_presigned_url()
```python
def get_s3_presigned_url(self, s3_key: str, expires_in: int = 3600, bucket: Optional[str] = None) -> Optional[str]
```
- **Purpose**: Generate presigned URL
- **Returns**: URL string or None

## Unified Session Manager S3 Functions (adapters/session/unified_session_manager.py)

### UnifiedSessionManager Class

#### _init_s3()
```python
def _init_s3(self)
```
- **Purpose**: Initialize S3 connection
- **Creates**: _s3_client and _s3_resource

#### get_s3_client()
```python
def get_s3_client(self)
```
- **Purpose**: Get S3 client (thread-safe) - lazy initialization
- **Returns**: boto3 S3 client

#### get_s3_resource()
```python
def get_s3_resource(self)
```
- **Purpose**: Get S3 resource (thread-safe) - lazy initialization
- **Returns**: boto3 S3 resource

#### _test_s3_connection()
```python
def _test_s3_connection(self) -> Dict[str, Any]
```
- **Purpose**: Test S3 connection with timing and details
- **Returns**: Dict with status, latency, bucket_count, error

### Module Function
```python
def get_s3_client()
```
- **Purpose**: Get S3 client from global session manager
- **Returns**: S3 client

## Configuration Functions

### YAMLSettingsLoader (infrastructure/yaml_loader.py)
```python
def get_s3_config(self) -> Dict[str, Any]
```
- **Purpose**: Get S3 configuration from settings
- **Returns**: Dict with S3 configuration from YAML

### CredentialLoader (packages/tidyllm/admin/credential_loader.py)
```python
def get_s3_configuration(self, environment=None)
def _get_default_s3_config(self)
def get_s3_config(environment=None)  # Module function
def build_s3_path(base_prefix, requirement, environment=None)  # Module function
```

## Port Definitions (domain/ports/outbound/session_port.py)

### SessionPort (Abstract)
```python
@abstractmethod
async def get_s3_client(self) -> Any:
    """Get an AWS S3 client"""
    pass
```

### UnifiedSessionPort (Abstract)
```python
@abstractmethod
async def get_s3_client(self) -> Any:
    """Get S3 client"""
    pass
```

## Adapter Implementation (adapters/secondary/session/unified_session_adapter.py)

```python
async def get_s3_client(self) -> Any:
    """Get an AWS S3 client"""
    try:
        return self._session_manager.get_s3_client()
    except Exception as e:
        logger.error(f"Failed to get S3 client: {e}")
        return None
```

## Important Notes

1. **Real vs Mock Implementations**:
   - The main S3Service (infrastructure/services/s3_service.py) is REAL - it uses boto3
   - S3Delegate has fallback mocks when parent infrastructure isn't available
   - All functions check BOTO3_AVAILABLE before attempting real operations

2. **Authentication**:
   - Uses AWS credentials from environment variables or configuration
   - Supports IAM roles, access keys, and session tokens

3. **Error Handling**:
   - All functions return False/None/empty on failure
   - Errors are logged but not raised to maintain stability

4. **Thread Safety**:
   - UnifiedSessionManager uses lazy initialization with thread safety
   - Singleton patterns used for service instances

5. **Default Bucket**:
   - Can be configured via settings, environment variable (S3_BUCKET), or per-call
   - Fallback chain: method parameter → config → environment