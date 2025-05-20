"""
Module for admin panel statistics and monitoring endpoints.
"""

import os
import re
import time
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from starlette import status
from datetime import datetime, timedelta

from backend.dependencies.getdb import get_db
from backend.oauth2 import get_current_user_jwt
from backend.models import OurUsers, Course, Enrollment, Assignment, AssignmentProgress
from backend.schemas.admin import (
    OverviewResponse, ActivityResponse, CourseDetailedResponse, UserDetailedResponse
)
from backend.models.progress import AssignmentStatus

router = APIRouter(prefix="/admin", tags=["admin"])


_error_logs = []


def check_admin_permission(current_user: dict):
    """
    Verify that the current user has admin privileges.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access this endpoint"
        )


@router.get("/statistics/overview", response_model=OverviewResponse)
async def get_platform_overview(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_jwt),
):
    """
    Get overview statistics for the admin dashboard.
    
    """
    check_admin_permission(current_user)
    
    # Count total users by role
    total_students = db.query(func.count(OurUsers.id)).filter(OurUsers.role == "student").scalar()
    total_teachers = db.query(func.count(OurUsers.id)).filter(OurUsers.role == "teacher").scalar()
    total_admins = db.query(func.count(OurUsers.id)).filter(OurUsers.role == "admin").scalar()
    
    # Count courses, assignments, and enrollments
    total_courses = db.query(func.count(Course.id)).scalar()
    total_assignments = db.query(func.count(Assignment.id)).scalar()
    total_enrollments = db.query(func.count(Enrollment.id)).scalar()
    
    # Get active courses (with at least one enrollment)
    active_courses = db.query(func.count(func.distinct(Enrollment.course_id))).scalar()
    
    # Count completed assignments
    completed_assignments = (
        db.query(func.count(AssignmentProgress.id))
        .filter((AssignmentProgress.status == AssignmentStatus.COMPLETED) | (AssignmentProgress.status == AssignmentStatus.GRADED))
        .scalar()
    )
    
    return {
        "users": {
            "total": total_students + total_teachers + total_admins,
            "students": total_students,
            "teachers": total_teachers,
            "admins": total_admins
        },
        "courses": {
            "total": total_courses,
            "active": active_courses
        },
        "assignments": {
            "total": total_assignments,
            "completed": completed_assignments
        },
        "enrollments": total_enrollments
    }


@router.get("/statistics/recent-activity", response_model=ActivityResponse)
async def get_recent_activity(
    days: Optional[int] = 7,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_jwt),
):
    """
    Get recent platform activity for the specified number of days.
    
    Args:
        days: Number of days to look back (default: 7)
        
    Returns:
        ActivityResponse: Recent activity statistics
    """
    check_admin_permission(current_user)
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Recent user registrations
    new_users = (
        db.query(OurUsers)
        .filter(OurUsers.created_at >= start_date)
        .order_by(desc(OurUsers.created_at))
        .limit(10)
        .all()
    )
    
    # Recent course creations
    new_courses = (
        db.query(Course)
        .filter(Course.created_at >= start_date)
        .order_by(desc(Course.created_at))
        .limit(10)
        .all()
    )
    
    # Recent assignment completions
    recent_completions = (
        db.query(AssignmentProgress)
        .filter(
            (AssignmentProgress.status == AssignmentStatus.COMPLETED) | (AssignmentProgress.status == AssignmentStatus.GRADED),
            AssignmentProgress.completed_at >= start_date
        )
        .order_by(desc(AssignmentProgress.completed_at))
        .limit(10)
        .all()
    )
    
    # Format the response
    return {
        "new_users": [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at
            }
            for user in new_users
        ],
        "new_courses": [
            {
                "id": course.id,
                "title": course.title,
                "teacher_id": course.teacher_id,
                "created_at": course.created_at
            }
            for course in new_courses
        ],
        "recent_completions": [
            {
                "student_id": completion.student_id,
                "assignment_id": completion.assignment_id,
                "completed_at": completion.completed_at,
                "score": completion.score
            }
            for completion in recent_completions
        ],
        "period": {
            "start_date": start_date,
            "end_date": end_date,
            "days": days
        }
    }


@router.get("/courses/detailed", response_model=List[CourseDetailedResponse])
async def get_courses_detailed(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_jwt),
):
    """
    Get detailed information about all courses.
    
    """
    check_admin_permission(current_user)
    
    # Get all courses
    courses = db.query(Course).all()
    
    result = []
    for course in courses:
        # Count enrollments for this course
        enrollment_count = (
            db.query(func.count(Enrollment.id))
            .filter(Enrollment.course_id == course.id)
            .scalar()
        )
        
        # Count assignments for this course
        assignment_count = (
            db.query(func.count(Assignment.id))
            .filter(Assignment.course_id == course.id)
            .scalar()
        )
        
        # Get teacher info
        teacher = db.query(OurUsers).filter(OurUsers.id == course.teacher_id).first()
        teacher_name = teacher.name if teacher else "Unknown"
        
        # Calculate completion rate
        total_possible_completions = enrollment_count * assignment_count if assignment_count > 0 else 0
        if total_possible_completions > 0:
            actual_completions = (
                db.query(func.count(AssignmentProgress.id))
                .join(Assignment, Assignment.id == AssignmentProgress.assignment_id)
                .filter(
                    Assignment.course_id == course.id,
                    (AssignmentProgress.status == AssignmentStatus.COMPLETED) | (AssignmentProgress.status == AssignmentStatus.GRADED)
                )
                .scalar()
            )
            completion_rate = round((actual_completions / total_possible_completions) * 100, 2)
        else:
            completion_rate = 0
        
        result.append({
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "teacher": {
                "id": course.teacher_id,
                "name": teacher_name
            },
            "statistics": {
                "enrollments": enrollment_count,
                "assignments": assignment_count,
                "completion_rate": completion_rate
            },
            "created_at": course.created_at
        })
    
    return result


@router.get("/users/detailed", response_model=List[UserDetailedResponse])
async def get_users_detailed(
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_jwt),
):
    """
    Get detailed information about users.
    
    """
    check_admin_permission(current_user)
    
    # Base query
    query = db.query(OurUsers)
    
    # Apply role filter if specified
    if role and role in ["student", "teacher", "admin"]:
        query = query.filter(OurUsers.role == role)
    
    # Get users
    users = query.all()
    
    result = []
    for user in users:
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at
        }
        
        # Add role-specific statistics
        if user.role == "student":
            # Get enrollment count
            enrollment_count = (
                db.query(func.count(Enrollment.id))
                .filter(Enrollment.user_id == user.id)
                .scalar()
            )
            
            # Get assignment completion stats
            completed_assignments = (
                db.query(func.count(AssignmentProgress.id))
                .filter(
                    (AssignmentProgress.status == AssignmentStatus.COMPLETED) | (AssignmentProgress.status == AssignmentStatus.GRADED),
                    AssignmentProgress.student_id == user.id
                )
                .scalar()
            )
            
            # Total assignments available to this student
            total_assignments = (
                db.query(func.count(Assignment.id))
                .join(Enrollment, Enrollment.course_id == Assignment.course_id)
                .filter(Enrollment.user_id == user.id)
                .scalar() or 0
            )
            
            completion_rate = round((completed_assignments / total_assignments) * 100, 2) if total_assignments > 0 else 0
            
            user_data["statistics"] = {
                "enrollments": enrollment_count,
                "completed_assignments": completed_assignments,
                "total_assignments": total_assignments,
                "completion_rate": completion_rate
            }
            
        elif user.role == "teacher":
            # Count courses taught
            course_count = (
                db.query(func.count(Course.id))
                .filter(Course.teacher_id == user.id)
                .scalar()
            )
            
            # Count students enrolled in their courses
            student_count = (
                db.query(func.count(func.distinct(Enrollment.user_id)))
                .join(Course, Course.id == Enrollment.course_id)
                .filter(Course.teacher_id == user.id)
                .scalar()
            )
            
            user_data["statistics"] = {
                "courses": course_count,
                "students": student_count
            }
        
        result.append(user_data)
    
    return result


@router.get("/courses/{course_id}/statistics")
async def get_course_statistics(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_jwt),
):
    """
    Get detailed statistics for a specific course.
    
    """
    check_admin_permission(current_user)
    
    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Get teacher info
    teacher = db.query(OurUsers).filter(OurUsers.id == course.teacher_id).first()
    teacher_name = teacher.name if teacher else "Unknown"
    
    # Get all students enrolled in this course
    enrolled_students = (
        db.query(OurUsers)
        .join(Enrollment, OurUsers.id == Enrollment.user_id)
        .filter(Enrollment.course_id == course_id)
        .all()
    )
    
    # Get all assignments for this course
    assignments = db.query(Assignment).filter(Assignment.course_id == course_id).all()
    
    # Calculate completion statistics
    assignment_stats = []
    for assignment in assignments:
        # Count submissions and completions
        submissions_count = (
            db.query(func.count(AssignmentProgress.id))
            .filter(
                AssignmentProgress.assignment_id == assignment.id,
                AssignmentProgress.submission_file_key != None
            )
            .scalar() or 0
        )
        
        completions_count = (
            db.query(func.count(AssignmentProgress.id))
            .filter(
                AssignmentProgress.assignment_id == assignment.id,
                (AssignmentProgress.status == AssignmentStatus.COMPLETED) | (AssignmentProgress.status == AssignmentStatus.GRADED)
            )
            .scalar() or 0
        )
        
        # Calculate average score
        avg_score = (
            db.query(func.avg(AssignmentProgress.score))
            .filter(
                AssignmentProgress.assignment_id == assignment.id,
                AssignmentProgress.score != None
            )
            .scalar() or 0
        )
        
        # Get students with pending submissions (submitted but not graded)
        pending_review_count = (
            db.query(func.count(AssignmentProgress.id))
            .filter(
                AssignmentProgress.assignment_id == assignment.id,
                AssignmentProgress.submission_file_key != None,
                AssignmentProgress.score == None
            )
            .scalar() or 0
        )
        
        assignment_stats.append({
            "id": assignment.id,
            "title": assignment.title,
            "due_date": assignment.due_date,
            "submissions": submissions_count,
            "completions": completions_count,
            "completion_rate": round((completions_count / len(enrolled_students)) * 100, 2) if enrolled_students else 0,
            "average_score": round(float(avg_score), 2),
            "pending_review": pending_review_count
        })
    
    # Get student progress data
    student_progress = []
    for student in enrolled_students:
        # Count completed assignments for this student in this course
        completed_count = (
            db.query(func.count(AssignmentProgress.id))
            .join(Assignment, Assignment.id == AssignmentProgress.assignment_id)
            .filter(
                Assignment.course_id == course_id,
                (AssignmentProgress.status == AssignmentStatus.COMPLETED) | (AssignmentProgress.status == AssignmentStatus.GRADED),
                AssignmentProgress.student_id == student.id
            )
            .scalar() or 0
        )
        
        # Calculate average score
        avg_score = (
            db.query(func.avg(AssignmentProgress.score))
            .join(Assignment, Assignment.id == AssignmentProgress.assignment_id)
            .filter(
                Assignment.course_id == course_id,
                (AssignmentProgress.status == AssignmentStatus.COMPLETED) | (AssignmentProgress.status == AssignmentStatus.GRADED),
                AssignmentProgress.student_id == student.id
            )
            .scalar() or 0
        )
        
        student_progress.append({
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "completed_assignments": completed_count,
            "total_assignments": len(assignments),
            "completion_rate": round((completed_count / len(assignments)) * 100, 2) if assignments else 0,
            "average_score": round(float(avg_score), 2)
        })
    
    # Get overall course activity
    latest_activity = (
        db.query(func.max(AssignmentProgress.last_activity))
        .join(Assignment, Assignment.id == AssignmentProgress.assignment_id)
        .filter(Assignment.course_id == course_id)
        .scalar()
    )
    
    return {
        "course": {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "teacher": {
                "id": course.teacher_id,
                "name": teacher_name
            },
            "created_at": course.created_at
        },
        "enrollment": {
            "total_students": len(enrolled_students),
            "last_activity": latest_activity
        },
        "assignments": {
            "total": len(assignments),
            "details": assignment_stats
        },
        "students": {
            "progress": student_progress
        },
        "overall_completion_rate": sum(s["completion_rate"] for s in student_progress) / len(student_progress) if student_progress else 0
    }


@router.get("/users/{user_id}/statistics")
async def get_user_statistics(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_jwt),
):
    """
    Get detailed statistics for a specific user.
    
    """
    check_admin_permission(current_user)
    
    # Check if user exists
    user = db.query(OurUsers).filter(OurUsers.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    result = {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at
        }
    }
    
    # Role-specific statistics
    if user.role == "student":
        # Get all enrollments
        enrollments = (
            db.query(Enrollment)
            .filter(Enrollment.user_id == user_id)
            .all()
        )
        
        # Get course details for each enrollment
        courses_data = []
        total_assignments = 0
        total_completed = 0
        total_score_sum = 0
        total_scored_assignments = 0
        
        for enrollment in enrollments:
            course = db.query(Course).filter(Course.id == enrollment.course_id).first()
            if not course:
                continue
                
            # Get assignments for this course
            assignments = db.query(Assignment).filter(Assignment.course_id == course.id).all()
            
            # Get progress for each assignment
            assignment_progress = []
            course_completed = 0
            course_score_sum = 0
            course_scored_assignments = 0
            
            for assignment in assignments:
                progress = (
                    db.query(AssignmentProgress)
                    .filter(
                        AssignmentProgress.student_id == user_id,
                        AssignmentProgress.assignment_id == assignment.id
                    )
                    .first()
                )
                
                is_completed = False
                score = None
                submission_date = None
                
                if progress:
                    is_completed = (progress.status == AssignmentStatus.COMPLETED) | (progress.status == AssignmentStatus.GRADED)
                    score = progress.score
                    submission_date = progress.submitted_at
                    
                    if is_completed:
                        course_completed += 1
                        total_completed += 1
                    
                    if score is not None:
                        course_score_sum += score
                        total_score_sum += score
                        course_scored_assignments += 1
                        total_scored_assignments += 1
                
                assignment_progress.append({
                    "assignment_id": assignment.id,
                    "title": assignment.title,
                    "is_completed": is_completed,
                    "score": score,
                    "submission_date": submission_date
                })
            
            # Calculate completion rate for this course
            completion_rate = round((course_completed / len(assignments)) * 100, 2) if assignments else 0
            avg_score = round(course_score_sum / course_scored_assignments, 2) if course_scored_assignments > 0 else None
            
            courses_data.append({
                "course_id": course.id,
                "title": course.title,
                "enrollment_date": enrollment.created_at,
                "assignments_total": len(assignments),
                "assignments_completed": course_completed,
                "completion_rate": completion_rate,
                "average_score": avg_score,
                "assignments": assignment_progress
            })
            
            total_assignments += len(assignments)
        
        # Calculate overall statistics
        overall_completion_rate = round((total_completed / total_assignments) * 100, 2) if total_assignments > 0 else 0
        overall_avg_score = round(total_score_sum / total_scored_assignments, 2) if total_scored_assignments > 0 else None
        
        # Add student-specific statistics to result
        result["statistics"] = {
            "enrollments": len(enrollments),
            "total_assignments": total_assignments,
            "completed_assignments": total_completed,
            "completion_rate": overall_completion_rate,
            "average_score": overall_avg_score
        }
        result["courses"] = courses_data
        
    elif user.role == "teacher":
        # Get all courses taught by this teacher
        courses = db.query(Course).filter(Course.teacher_id == user_id).all()
        
        courses_data = []
        total_students = set()
        total_assignments = 0
        
        for course in courses:
            # Get enrollments for this course
            enrollments = db.query(Enrollment).filter(Enrollment.course_id == course.id).all()
            student_ids = [enrollment.user_id for enrollment in enrollments]
            
            # Add to total unique students
            total_students.update(student_ids)
            
            # Get assignments for this course
            assignments = db.query(Assignment).filter(Assignment.course_id == course.id).all()
            total_assignments += len(assignments)
            
            # Get completion statistics
            if student_ids and assignments:
                completed_count = (
                    db.query(func.count(AssignmentProgress.id))
                    .join(Assignment, Assignment.id == AssignmentProgress.assignment_id)
                    .filter(
                        Assignment.course_id == course.id,
                        (AssignmentProgress.status == AssignmentStatus.COMPLETED) | (AssignmentProgress.status == AssignmentStatus.GRADED),
                        AssignmentProgress.student_id.in_(student_ids)
                    )
                    .scalar() or 0
                )
                
                total_possible = len(student_ids) * len(assignments)
                completion_rate = round((completed_count / total_possible) * 100, 2) if total_possible > 0 else 0
            else:
                completion_rate = 0
            
            courses_data.append({
                "course_id": course.id,
                "title": course.title,
                "created_at": course.created_at,
                "students_count": len(student_ids),
                "assignments_count": len(assignments),
                "completion_rate": completion_rate
            })
        
        # Add teacher-specific statistics to result
        result["statistics"] = {
            "courses_count": len(courses),
            "total_students": len(total_students),
            "total_assignments": total_assignments
        }
        result["courses"] = courses_data
    
    return result


def log_error(error_data: dict):
    """Add error to the error log"""
    _error_logs.append({
        "timestamp": time.time(),
        "error": error_data
    })
    # количество хранимых ошибок
    if len(_error_logs) > 100:
        _error_logs.pop(0)


@router.get("/system/errors")
async def get_error_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_jwt),
):
    """
    Get recent error logs.
    
    """
    check_admin_permission(current_user)
    
    return _error_logs[-limit:] if _error_logs else []


@router.get("/system/logs")
async def get_system_logs(
    limit: int = 50,
    log_type: str = "all",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_jwt),
):
    """
    Get system logs.
    
    """
    check_admin_permission(current_user)
    
    # возвращаем моковые данные для тестирования
    
    # Пример лог-файла сервера (в реальном приложении - чтение файла)
    server_log = [
        {"timestamp": time.time() - 3600, "level": "INFO", "message": "Server started successfully"},
        {"timestamp": time.time() - 3500, "level": "INFO", "message": "Database connection established"},
        {"timestamp": time.time() - 3000, "level": "WARNING", "message": "High CPU usage detected"},
        {"timestamp": time.time() - 2000, "level": "ERROR", "message": "Failed to connect to external API"},
        {"timestamp": time.time() - 1000, "level": "INFO", "message": "Backup completed successfully"},
    ]
    
    # Фильтрация по типу логов
    if log_type != "all":
        log_type = log_type.upper()
        server_log = [log for log in server_log if log["level"] == log_type]
    
    return {
        "logs": server_log[-limit:],
        "total_count": len(server_log)
    }


@router.get("/system/performance")
async def get_system_performance(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_jwt),
):
    """
    Get system performance metrics.
    
    Returns:
        dict: System performance data
    """
    check_admin_permission(current_user)
    
    # В реальном приложении здесь нужно получать метрики из системы мониторинга
    # В данной версии просто возвращаем тестовые данные
    return {
        "cpu_usage": 35.4,
        "memory_usage": 42.7,
        "disk_usage": 61.2,
        "active_connections": 12,
        "average_response_time": 0.187,
        "timestamp": time.time()
    } 