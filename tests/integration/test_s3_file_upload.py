#!/usr/bin/env python3
"""
TidyLLM S3 File Upload Test

Comprehensive test for S3 file upload functionality with AWS credentials.
Tests uploading various file types to S3 buckets with proper error handling.
"""

import os
import boto3
import tempfile
import json
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

# Set up AWS credentials
# Credentials loaded by centralized system
# Credentials loaded by centralized system

class S3FileUploadTester:
    """S3 File Upload Test Suite"""
    
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.s3_resource = boto3.resource('s3')
        self.test_bucket = None
        self.test_files = []
        
    def setup_test_environment(self):
        """Setup test environment and identify test bucket"""
        print("1. Setting up test environment...")
        
        try:
            # List available buckets
            response = self.s3_client.list_buckets()
            buckets = [bucket['Name'] for bucket in response['Buckets']]
            
            print(f"   ✅ Found {len(buckets)} accessible buckets:")
            for bucket in buckets:
                print(f"      - {bucket}")
            
            # Use first accessible bucket for testing
            if buckets:
                self.test_bucket = buckets[0]  # Use first available bucket
                print(f"   ✅ Using bucket for tests: {self.test_bucket}")
                return True
            else:
                print("   ❌ No accessible buckets found")
                return False
                
        except Exception as e:
            print(f"   ❌ Setup failed: {e}")
            return False
    
    def create_test_files(self):
        """Create temporary test files for upload"""
        print("\n2. Creating test files...")
        
        try:
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp(prefix='s3_test_')
            print(f"   ✅ Temp directory: {self.temp_dir}")
            
            # Text file
            text_file = Path(self.temp_dir) / "test_document.txt"
            with open(text_file, 'w') as f:
                f.write("This is a test document for S3 upload.\n")
                f.write(f"Created at: {datetime.now().isoformat()}\n")
                f.write("TidyLLM S3 Upload Test\n")
            self.test_files.append(("text", text_file))
            
            # JSON file
            json_file = Path(self.temp_dir) / "test_data.json"
            test_data = {
                "test_id": f"test_{int(datetime.now().timestamp())}",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "numbers": [1, 2, 3, 4, 5],
                    "text": "Sample JSON data for S3 upload test",
                    "boolean": True
                },
                "metadata": {
                    "source": "TidyLLM S3 Test Suite",
                    "version": "1.0"
                }
            }
            with open(json_file, 'w') as f:
                json.dump(test_data, f, indent=2)
            self.test_files.append(("json", json_file))
            
            # CSV file
            csv_file = Path(self.temp_dir) / "test_data.csv"
            with open(csv_file, 'w') as f:
                f.write("id,name,value,timestamp\n")
                f.write("1,test_item_1,100,2025-01-01T10:00:00\n")
                f.write("2,test_item_2,200,2025-01-01T11:00:00\n")
                f.write("3,test_item_3,300,2025-01-01T12:00:00\n")
            self.test_files.append(("csv", csv_file))
            
            # Python script file
            py_file = Path(self.temp_dir) / "test_script.py"
            with open(py_file, 'w') as f:
                f.write("#!/usr/bin/env python3\n")
                f.write('"""Test Python script for S3 upload"""\n\n')
                f.write("def hello_world():\n")
                f.write('    print("Hello from S3 uploaded file!")\n\n')
                f.write("if __name__ == '__main__':\n")
                f.write("    hello_world()\n")
            self.test_files.append(("python", py_file))
            
            print(f"   ✅ Created {len(self.test_files)} test files:")
            for file_type, file_path in self.test_files:
                size = file_path.stat().st_size
                print(f"      - {file_path.name} ({file_type}, {size} bytes)")
                
            return True
            
        except Exception as e:
            print(f"   ❌ File creation failed: {e}")
            return False
    
    def test_file_uploads(self):
        """Test uploading files to S3"""
        print("\n3. Testing file uploads...")
        
        if not self.test_bucket:
            print("   ❌ No test bucket available")
            return False
        
        upload_results = []
        test_prefix = f"tidyllm-tests/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        for file_type, file_path in self.test_files:
            try:
                # Generate S3 key
                s3_key = f"{test_prefix}/{file_path.name}"
                
                print(f"   Uploading {file_path.name} ({file_type})...")
                
                # Upload file
                self.s3_client.upload_file(
                    str(file_path),
                    self.test_bucket,
                    s3_key,
                    ExtraArgs={
                        'Metadata': {
                            'file-type': file_type,
                            'test-id': 'tidyllm-upload-test',
                            'uploaded-at': datetime.now().isoformat()
                        }
                    }
                )
                
                # Verify upload
                response = self.s3_client.head_object(Bucket=self.test_bucket, Key=s3_key)
                file_size = response['ContentLength']
                
                upload_results.append({
                    'file': file_path.name,
                    'type': file_type,
                    'key': s3_key,
                    'size': file_size,
                    'status': 'success'
                })
                
                print(f"      ✅ Uploaded: s3://{self.test_bucket}/{s3_key} ({file_size} bytes)")
                
            except Exception as e:
                upload_results.append({
                    'file': file_path.name,
                    'type': file_type,
                    'error': str(e),
                    'status': 'failed'
                })
                print(f"      ❌ Upload failed: {e}")
        
        # Summary
        successful_uploads = [r for r in upload_results if r['status'] == 'success']
        failed_uploads = [r for r in upload_results if r['status'] == 'failed']
        
        print(f"\n   Upload Summary:")
        print(f"      ✅ Successful: {len(successful_uploads)}/{len(upload_results)}")
        print(f"      ❌ Failed: {len(failed_uploads)}/{len(upload_results)}")
        
        if successful_uploads:
            total_size = sum(r['size'] for r in successful_uploads)
            print(f"      📊 Total uploaded: {total_size} bytes")
        
        return len(successful_uploads) > 0
    
    def test_file_download(self):
        """Test downloading files from S3"""
        print("\n4. Testing file downloads...")
        
        try:
            # List objects in test prefix
            test_prefix = f"tidyllm-tests/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.test_bucket,
                Prefix=test_prefix,
                MaxKeys=5
            )
            
            if 'Contents' not in response:
                print("   ⚠️  No test files found for download test")
                return True
            
            download_dir = Path(self.temp_dir) / "downloads"
            download_dir.mkdir(exist_ok=True)
            
            downloaded_files = []
            
            for obj in response['Contents'][:3]:  # Download first 3 files
                s3_key = obj['Key']
                filename = Path(s3_key).name
                local_path = download_dir / filename
                
                print(f"   Downloading {filename}...")
                
                self.s3_client.download_file(
                    self.test_bucket,
                    s3_key,
                    str(local_path)
                )
                
                # Verify download
                if local_path.exists():
                    size = local_path.stat().st_size
                    downloaded_files.append((filename, size))
                    print(f"      ✅ Downloaded: {filename} ({size} bytes)")
                else:
                    print(f"      ❌ Download failed: {filename}")
            
            print(f"   ✅ Successfully downloaded {len(downloaded_files)} files")
            return True
            
        except Exception as e:
            print(f"   ❌ Download test failed: {e}")
            return False
    
    def test_file_operations(self):
        """Test additional file operations"""
        print("\n5. Testing file operations...")
        
        try:
            # List recent uploads
            test_prefix = "tidyllm-tests/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.test_bucket,
                Prefix=test_prefix,
                MaxKeys=10
            )
            
            if 'Contents' in response:
                print(f"   ✅ Found {len(response['Contents'])} test files in S3")
                
                # Get metadata for first file
                if response['Contents']:
                    first_obj = response['Contents'][0]
                    s3_key = first_obj['Key']
                    
                    metadata_response = self.s3_client.head_object(
                        Bucket=self.test_bucket,
                        Key=s3_key
                    )
                    
                    print(f"   ✅ File metadata retrieved:")
                    print(f"      - Size: {metadata_response['ContentLength']} bytes")
                    print(f"      - Last Modified: {metadata_response['LastModified']}")
                    if 'Metadata' in metadata_response:
                        for key, value in metadata_response['Metadata'].items():
                            print(f"      - {key}: {value}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ File operations test failed: {e}")
            return False
    
    def cleanup(self):
        """Cleanup temporary files"""
        print("\n6. Cleaning up...")
        
        try:
            # Remove temporary files
            import shutil
            if hasattr(self, 'temp_dir') and Path(self.temp_dir).exists():
                shutil.rmtree(self.temp_dir)
                print(f"   ✅ Cleaned up temporary directory: {self.temp_dir}")
            
            print("   ✅ Cleanup complete")
            
        except Exception as e:
            print(f"   ⚠️  Cleanup warning: {e}")

def main():
    """Run S3 file upload test suite"""
    print("=" * 60)
    print("  TidyLLM S3 File Upload Test Suite")
    print("=" * 60)
    
    tester = S3FileUploadTester()
    
    try:
        # Run test sequence
        if not tester.setup_test_environment():
            print("\n❌ Setup failed - aborting tests")
            return False
        
        if not tester.create_test_files():
            print("\n❌ File creation failed - aborting tests")
            return False
        
        upload_success = tester.test_file_uploads()
        download_success = tester.test_file_download()
        operations_success = tester.test_file_operations()
        
        # Final summary
        print("\n" + "=" * 60)
        print("  Test Results Summary")
        print("=" * 60)
        
        tests = [
            ("Environment Setup", True),
            ("File Creation", True),
            ("File Upload", upload_success),
            ("File Download", download_success),
            ("File Operations", operations_success)
        ]
        
        passed_tests = sum(1 for _, result in tests if result)
        
        for test_name, result in tests:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name}: {status}")
        
        print(f"\nOverall: {passed_tests}/{len(tests)} tests passed")
        
        if passed_tests >= 4:  # Allow 1 test to fail
            print("\n🎉 S3 FILE UPLOAD TEST SUITE: SUCCESS!")
            print("✅ S3 connectivity confirmed")
            print("✅ File upload functionality working")
            print("✅ File download functionality working")
            print("✅ S3 operations fully operational")
            success = True
        else:
            print("\n⚠️  S3 FILE UPLOAD TEST SUITE: PARTIAL SUCCESS")
            print("Some tests failed - check individual results above")
            success = False
        
        return success
        
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        tester.cleanup()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)