"""
S3 dependencies for FastAPI application.
"""

import os
import boto3
from fastapi import Depends

class S3Dependencies:
    """
    Dependency class for S3 operations.
    
    This class provides access to AWS S3 client and common operations.
    """
    
    def __init__(self):
        """Initialize S3 client with credentials from environment variables."""
        self.client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
        self.bucket_name = os.getenv("BUCKET_NAME", "files-for-team-project")
    
    async def upload_file(self, file_content, key, content_type=None):
        """
        Upload a file to S3.
        
        Args:
            file_content: File content to upload
            key: S3 object key
            content_type: Optional content type
            
        Returns:
            Response from S3
        """
        params = {
            "Bucket": self.bucket_name,
            "Key": key,
            "Body": file_content
        }
        
        if content_type:
            params["ContentType"] = content_type
            
        return self.client.put_object(**params)
    
    async def delete_file(self, key):
        """
        Delete a file from S3.
        
        Args:
            key: S3 object key
            
        Returns:
            Response from S3
        """
        return self.client.delete_object(Bucket=self.bucket_name, Key=key)
    
    async def get_file(self, key):
        """
        Get a file from S3.
        
        Args:
            key: S3 object key
            
        Returns:
            Response from S3
        """
        return self.client.get_object(Bucket=self.bucket_name, Key=key)
    
    async def list_files(self, prefix=None):
        """
        List files in S3 bucket.
        
        Args:
            prefix: Optional prefix to filter results
            
        Returns:
            Response from S3
        """
        params = {"Bucket": self.bucket_name}
        if prefix:
            params["Prefix"] = prefix
            
        return self.client.list_objects_v2(**params)

# Dependency to inject S3 client
def get_s3_client():
    """Dependency for FastAPI to inject S3 client."""
    return S3Dependencies() 