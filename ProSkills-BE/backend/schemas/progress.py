from datetime import datetime
from typing import Optional, Literal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, validator, computed_field


class AssignmentStatusEnum(str, Enum):
    NOT_STARTED = "not_started"
    SUBMITTED = "submitted"
    GRADED = "graded"
    COMPLETED = "completed"


class AssignmentProgressBase(BaseModel):
    student_id: int
    assignment_id: int
    course_id: Optional[int] = None
    status: AssignmentStatusEnum = AssignmentStatusEnum.NOT_STARTED
    submission_file_key: Optional[str] = None
    score: Optional[int] = None
    feedback: Optional[str] = None
    completed_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    
    @computed_field
    @property
    def is_completed(self) -> bool:
        """For backwards compatibility"""
        return self.status in [AssignmentStatusEnum.COMPLETED, AssignmentStatusEnum.GRADED]


class AssignmentProgressCreate(AssignmentProgressBase):
    pass


class AssignmentProgressUpdate(BaseModel):
    status: Optional[AssignmentStatusEnum] = None
    submission_file_key: Optional[str] = None
    score: Optional[int] = None
    feedback: Optional[str] = None
    completed_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None


class AssignmentProgressInDB(AssignmentProgressBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class AssignmentProgressResponse(AssignmentProgressInDB):
    pass


class CourseProgressBase(BaseModel):
    student_id: int
    course_id: int
    completed_assignments: int = Field(default=0, ge=0)
    total_assignments: int = Field(default=0, ge=0)
    last_activity: Optional[datetime] = None


class CourseProgressCreate(CourseProgressBase):
    pass


class CourseProgressUpdate(BaseModel):
    completed_assignments: Optional[int] = Field(default=None, ge=0)
    total_assignments: Optional[int] = Field(default=None, ge=0)
    last_activity: Optional[datetime] = None


class CourseProgressInDB(CourseProgressBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CourseProgressResponse(CourseProgressInDB):
    completion_percentage: float = Field(default=0.0, ge=0.0, le=100.0)

    @validator("completion_percentage", pre=True)
    def validate_completion_percentage(cls, v):
        if v is None:
            return 0.0
        try:
            value = float(v)
            return round(max(0.0, min(100.0, value)), 2)
        except (TypeError, ValueError):
            return 0.0

    model_config = ConfigDict(from_attributes=True)
