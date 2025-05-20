from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from typing import List, Optional
from fastapi import HTTPException, status

from backend.models.review import Review
from backend.models.ourusers import OurUsers
from backend.models.course import Course
from backend.schemas.review import ReviewCreate, ReviewUpdate, ReviewWithUserInfo


def create_review(db: Session, user_id: int, course_id: int, review_data: ReviewCreate) -> Review:
    """
    Создать новый отзыв для курса
    """
    # Проверяем существование курса
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Курс с ID {course_id} не найден"
        )
    
    # Проверяем, не оставлял ли пользователь уже отзыв на этот курс
    existing_review = db.query(Review).filter(
        Review.user_id == user_id,
        Review.course_id == course_id
    ).first()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже оставили отзыв на этот курс"
        )
    
    # Создаем новый отзыв
    new_review = Review(
        user_id=user_id,
        course_id=course_id,
        text=review_data.text
    )
    
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review


def get_course_reviews(db: Session, course_id: int, skip: int = 0, limit: int = 100) -> List[dict]:
    """
    Получить все отзывы для курса с информацией о пользователях
    """
    # Проверяем существование курса
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Курс с ID {course_id} не найден"
        )
    
    # Получаем отзывы с информацией о пользователях
    reviews = (
        db.query(
            Review.id,
            Review.text,
            Review.user_id,
            Review.course_id,
            Review.created_at,
            Review.updated_at,
            OurUsers.first_name.label("user_first_name"),
            OurUsers.last_name.label("user_last_name")
        )
        .join(OurUsers, Review.user_id == OurUsers.id)
        .filter(Review.course_id == course_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return [
        {
            "id": review.id,
            "text": review.text,
            "user_id": review.user_id,
            "course_id": review.course_id,
            "created_at": review.created_at,
            "updated_at": review.updated_at,
            "user_first_name": review.user_first_name,
            "user_last_name": review.user_last_name
        }
        for review in reviews
    ]


def update_review(db: Session, review_id: int, user_id: int, review_data: ReviewUpdate) -> Review:
    """
    Обновить существующий отзыв
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Отзыв с ID {review_id} не найден"
        )
    
    # Проверяем, принадлежит ли отзыв пользователю
    if review.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете редактировать только свои отзывы"
        )
    
    # Обновляем отзыв
    review.text = review_data.text
    
    db.commit()
    db.refresh(review)
    return review


def delete_review(db: Session, review_id: int, user_id: int, is_admin: bool = False) -> bool:
    """
    Удалить существующий отзыв
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Отзыв с ID {review_id} не найден"
        )
    
    # Проверяем, принадлежит ли отзыв пользователю или является ли пользователь администратором
    if review.user_id != user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете удалять только свои отзывы"
        )
    
    # Удаляем отзыв
    db.delete(review)
    db.commit()
    return True


def get_user_reviews(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
    """
    Получить все отзывы, оставленные пользователем
    """
    reviews = (
        db.query(Review)
        .filter(Review.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return reviews


def get_review_by_id(db: Session, review_id: int) -> Optional[Review]:
    """
    Получить отзыв по его ID
    """
    return db.query(Review).filter(Review.id == review_id).first() 