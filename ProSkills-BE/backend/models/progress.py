from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.basemodel import BaseModel


class AssignmentStatus(str, Enum):
    NOT_STARTED = "not_started"    # Задание не начато
    SUBMITTED = "submitted"        # Студент загрузил решение, ожидает проверки
    GRADED = "graded"              # Учитель поставил оценку
    COMPLETED = "completed"        # Задание полностью выполнено


class AssignmentProgress(BaseModel):
    __tablename__ = "assignment_progress"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("our_users.id"),
        nullable=False,
    )
    assignment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("assignments.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String, default=AssignmentStatus.NOT_STARTED)
    submission_file_key: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )  # S3 file key for submission
    score: Mapped[int] = mapped_column(Integer, nullable=True)  # Optional score/grade
    feedback: Mapped[str] = mapped_column(String, nullable=True)  # Teacher feedback
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    student = relationship("OurUsers", backref="assignment_progress")
    assignment = relationship("Assignment", backref="student_progress")

    @property
    def course_id(self) -> int:
        """Get the course_id through the assignment relationship"""
        if self.assignment:
            return self.assignment.course_id
        return None
            
    @property
    def is_completed(self) -> bool:
        """Backward compatibility property for is_completed"""
        return self.status in [AssignmentStatus.COMPLETED, AssignmentStatus.GRADED]

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "assignment_id": self.assignment_id,
            "course_id": self.course_id,
            "is_completed": self.is_completed,
            "status": self.status,
            "submission_file_key": self.submission_file_key,
            "score": self.score,
            "feedback": self.feedback,
            "completed_at": self.completed_at,
            "submitted_at": self.submitted_at,
        }


class CourseProgress(BaseModel):
    __tablename__ = "course_progress"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("our_users.id"),
        nullable=False,
    )
    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False,
    )
    completed_assignments: Mapped[int] = mapped_column(Integer, default=0)
    total_assignments: Mapped[int] = mapped_column(Integer, default=0)
    last_activity: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    student = relationship("OurUsers", backref="course_progress")
    course = relationship("Course", backref="student_progress")

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "completed_assignments": self.completed_assignments,
            "total_assignments": self.total_assignments,
            "last_activity": self.last_activity,
            "completion_percentage": self.completion_percentage(),
        }

    def completion_percentage(self):
        """Calculate completion percentage with proper type handling"""
        try:
            if not isinstance(
                self.completed_assignments,
                (int, float),
            ) or not isinstance(self.total_assignments, (int, float)):
                return 0.0
            if self.total_assignments <= 0:
                return 0.0
            percentage = (
                float(self.completed_assignments) / float(self.total_assignments)
            ) * 100.0
            return float(round(percentage, 2))
        except Exception:
            return 0.0
