from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from backend.models.basemodel import BaseModel


class Review(BaseModel):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    text = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("our_users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    # Relationships
    user = relationship("OurUsers", back_populates="reviews")
    course = relationship("Course", back_populates="reviews")
    
    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "user_id": self.user_id,
            "course_id": self.course_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        } 