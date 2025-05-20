from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.dependencies.getdb import get_db
from backend.models import Course
from backend.models.review import Review
from backend.oauth2 import get_current_user_jwt
from backend.schemas.review import ReviewCreate, ReviewResponse, ReviewUpdate, ReviewWithUserInfo
from backend.services import review as review_service
from backend.services.websocket import manager

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/courses/{course_id}", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_course_review(
    course_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_jwt),
):
    """
    Создать новый отзыв для курса.
    Пользователь может оставить только один отзыв на курс.
    """
    user_id = current_user.get("user_id")
    
    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )
    
    # Create review
    new_review = review_service.create_review(db, user_id, course_id, review_data)
    
    # Send WebSocket notification
    try:
        room_id = f"course_{course_id}"
        await manager.broadcast_to_room(
            {
                "event": "review_created",
                "course_id": course_id,
                "review_id": new_review.id,
                "user_id": user_id
            },
            room_id
        )
    except Exception as e:
        # Log the exception but don't fail the request
        print(f"Error broadcasting review creation: {str(e)}")
    
    return new_review


@router.get("/courses/{course_id}", response_model=List[ReviewWithUserInfo])
async def get_course_reviews(
    course_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Получить все отзывы для курса вместе с информацией о пользователях.
    """
    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )
    
    reviews = review_service.get_course_reviews(db, course_id, skip, limit)
    return reviews


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_jwt),
):
    """
    Обновить существующий отзыв.
    Пользователь может обновлять только свои отзывы.
    """
    user_id = current_user.get("user_id")
    
    updated_review = review_service.update_review(db, review_id, user_id, review_data)
    
    # Send WebSocket notification
    try:
        review = db.query(Review).filter(Review.id == review_id).first()
        if review:
            room_id = f"course_{review.course_id}"
            await manager.broadcast_to_room(
                {
                    "event": "review_updated",
                    "course_id": review.course_id,
                    "review_id": review_id,
                    "user_id": user_id
                },
                room_id
            )
    except Exception as e:
        # Log the exception but don't fail the request
        print(f"Error broadcasting review update: {str(e)}")
    
    return updated_review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_jwt),
):
    """
    Удалить существующий отзыв.
    Пользователь может удалять только свои отзывы.
    Администраторы могут удалять любые отзывы.
    """
    user_id = current_user.get("user_id")
    is_admin = current_user.get("role") == "admin"
    
    # Get course_id for WebSocket notification before deletion
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отзыв не найден"
        )
    
    course_id = review.course_id
    
    # Delete review
    review_service.delete_review(db, review_id, user_id, is_admin)
    
    # Send WebSocket notification
    try:
        room_id = f"course_{course_id}"
        await manager.broadcast_to_room(
            {
                "event": "review_deleted",
                "course_id": course_id,
                "review_id": review_id,
                "user_id": user_id
            },
            room_id
        )
    except Exception as e:
        # Log the exception but don't fail the request
        print(f"Error broadcasting review deletion: {str(e)}")
    
    return None


@router.get("/users/{user_id}", response_model=List[ReviewResponse])
async def get_user_reviews(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_jwt),
):
    """
    Получить все отзывы, оставленные пользователем.
    Пользователи могут видеть только свои отзывы, администраторы - отзывы всех пользователей.
    """
    current_user_id = current_user.get("user_id")
    is_admin = current_user.get("role") == "admin"
    
    # Check permissions
    if user_id != current_user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете просматривать только свои отзывы"
        )
    
    reviews = review_service.get_user_reviews(db, user_id, skip, limit)
    return reviews 