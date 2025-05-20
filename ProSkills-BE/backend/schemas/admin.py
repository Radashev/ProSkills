"""
Pydantic models for admin panel data.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class UserStatistics(BaseModel):
    """Base statistics for users in the admin dashboard"""
    total: int
    students: int
    teachers: int
    admins: int


class CourseStatistics(BaseModel):
    """Base statistics for courses in the admin dashboard"""
    total: int
    active: int


class AssignmentStatistics(BaseModel):
    """Base statistics for assignments in the admin dashboard"""
    total: int
    completed: int


class OverviewResponse(BaseModel):
    """Response model for the overview statistics endpoint"""
    users: UserStatistics
    courses: CourseStatistics
    assignments: AssignmentStatistics
    enrollments: int


class UserBrief(BaseModel):
    """Brief user information for activity feeds"""
    id: int
    name: str
    email: str
    role: str
    created_at: datetime


class CourseBrief(BaseModel):
    """Brief course information for activity feeds"""
    id: int
    title: str
    teacher_id: int
    created_at: datetime


class CompletionBrief(BaseModel):
    """Brief completion information for activity feeds"""
    student_id: int
    assignment_id: int
    completed_at: datetime
    score: Optional[int] = None


class ActivityPeriod(BaseModel):
    """Time period for activity data"""
    start_date: datetime
    end_date: datetime
    days: int


class ActivityResponse(BaseModel):
    """Response model for the recent activity endpoint"""
    new_users: List[UserBrief]
    new_courses: List[CourseBrief]
    recent_completions: List[CompletionBrief]
    period: ActivityPeriod


class CourseTeacher(BaseModel):
    """Brief teacher information for course details"""
    id: int
    name: str


class CourseStats(BaseModel):
    """Statistics for a course"""
    enrollments: int
    assignments: int
    completion_rate: float


class CourseDetailedResponse(BaseModel):
    """Detailed course information for admin panel"""
    id: int
    title: str
    description: str
    teacher: CourseTeacher
    statistics: CourseStats
    created_at: datetime


class StudentStats(BaseModel):
    """Statistics for a student"""
    enrollments: int
    completed_assignments: int
    total_assignments: int
    completion_rate: float


class TeacherStats(BaseModel):
    """Statistics for a teacher"""
    courses: int
    students: int


class UserDetailedResponse(BaseModel):
    """Detailed user information for admin panel"""
    id: int
    name: str
    email: str
    role: str
    created_at: datetime
    statistics: Optional[Dict[str, Any]] = None 