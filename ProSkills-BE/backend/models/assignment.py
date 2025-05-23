from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.basemodel import BaseModel


class Assignment(BaseModel):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    section_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("sections.id"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    teacher_comments: Mapped[str] = mapped_column(String, default="")
    order: Mapped[int] = mapped_column(default=0)  # Order within the section
    is_completed: Mapped[bool] = mapped_column(default=False)
    submission_type: Mapped[str] = mapped_column(String, default="autoComplete")  # "autoComplete" or "fileSubmission"

    # Relationships
    course = relationship("Course", back_populates="assignments")
    section = relationship("Section", back_populates="assignments")

    def to_dict(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "section_id": self.section_id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "teacher_comments": self.teacher_comments,
            "order": self.order,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_completed": self.is_completed,
            "submission_type": self.submission_type,
        }
