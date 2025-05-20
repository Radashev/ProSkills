from datetime import datetime
from typing import List, Optional, Literal

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict, computed_field

from backend.schemas.comment import CommentResponse
from backend.schemas.progress import AssignmentStatusEnum


class AssignmentBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    teacher_comments: Optional[str] = None
    order: Optional[int] = None
    submission_type: Optional[Literal["autoComplete", "fileSubmission"]] = "autoComplete"


class AssignmentCreate(AssignmentBase):
    section_id: Optional[int] = None


class AssignmentWithFileCreate(AssignmentCreate):
    file: Optional[UploadFile] = None


class AssignmentFile(BaseModel):
    key: str
    size: int
    last_modified: datetime
    filename: str


class AssignmentResponse(AssignmentBase):
    id: int
    course_id: int
    section_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    files: List[AssignmentFile] = []

    model_config = ConfigDict(from_attributes=True)


class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    teacher_comments: Optional[str] = None
    section_id: Optional[int] = None
    order: Optional[int] = None
    submission_type: Optional[Literal["autoComplete", "fileSubmission"]] = None


class AssignmentInDB(AssignmentBase):
    id: int
    course_id: int
    section_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    is_completed: bool

    model_config = ConfigDict(from_attributes=True)


class AssignmentWithCommentsResponse(AssignmentResponse):
    comments: List[CommentResponse] = []
    is_completed: bool = False

    model_config = ConfigDict(from_attributes=True)


class AssignmentWithProgressResponse(AssignmentResponse):
    submission_file_key: Optional[str] = None
    score: Optional[float] = None
    feedback: Optional[str] = None
    status: AssignmentStatusEnum = AssignmentStatusEnum.NOT_STARTED
    
    @computed_field
    @property
    def is_completed(self) -> bool:
        """For backwards compatibility"""
        return self.status in [AssignmentStatusEnum.COMPLETED, AssignmentStatusEnum.GRADED]

    model_config = ConfigDict(from_attributes=True)
