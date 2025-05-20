from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FileResponse(BaseModel):
    """Schema for file information returned from S3"""

    key: str
    size: int
    last_modified: datetime
    etag: str


class FileResponseSchema(BaseModel):
    """Schema for file submission response"""
    
    filename: str
    file_key: str
    file_size: int
    content_type: str
    upload_time: datetime
    assignment_id: Optional[int] = None


class SubmissionResponseSchema(FileResponseSchema):
    """Schema for file submission with assignment information"""
    
    assignment_id: int
    assignment_title: Optional[str] = None
    student_id: Optional[int] = None
    student_name: Optional[str] = None


class FileUploadResponse(BaseModel):
    """Schema for successful file upload response"""

    message: str
    file_key: str


class FileDeleteResponse(BaseModel):
    """Schema for successful file deletion response"""

    message: str
