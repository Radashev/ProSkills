"""
Module for handling course and assignment progress tracking.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from starlette import status
from pydantic import BaseModel

from backend.dependencies.getdb import get_db
from backend.models import Assignment, AssignmentProgress, Course, CourseProgress, Enrollment
from backend.oauth2 import get_current_user_jwt, get_current_user_jwt_required
from backend.schemas.assignment import AssignmentWithProgressResponse
from backend.schemas.progress import (
    AssignmentProgressCreate,
    AssignmentProgressResponse,
    AssignmentProgressUpdate,
    CourseProgressResponse,
)
from backend.models.progress import AssignmentStatus

# Import WebSocket manager
from backend.services.websocket import manager

router = APIRouter(prefix="/progress", tags=["progress"])


def check_enrollment(db: Session, student_id: int, course_id: int) -> bool:
    """
    Check if a student is enrolled in a course.

    Args:
        db: Database session
        student_id: ID of the student
        course_id: ID of the course

    Returns:
        bool: True if student is enrolled, False otherwise
    """
    return (
        db.query(Enrollment)
        .filter(Enrollment.user_id == student_id, Enrollment.course_id == course_id)
        .first()
        is not None
    )


# Helper function to ensure course progress record exists
def get_or_create_course_progress(db: Session, student_id: int, course_id: int):
    progress = (
        db.query(CourseProgress)
        .filter(
            CourseProgress.student_id == student_id,
            CourseProgress.course_id == course_id,
        )
        .first()
    )

    if not progress:
        # Get total assignments for this course
        total_assignments = (
            db.query(Assignment).filter(Assignment.course_id == course_id).count()
        )

        # Create new progress record
        progress = CourseProgress(
            student_id=student_id,
            course_id=course_id,
            total_assignments=total_assignments,
            completed_assignments=0,
            last_activity=datetime.now(),
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)

    return progress


# Helper function to update course progress after assignment completion
def update_course_progress(db: Session, student_id: int, course_id: int):
    course_progress = (
        db.query(CourseProgress)
        .filter(
            CourseProgress.student_id == student_id,
            CourseProgress.course_id == course_id,
        )
        .first()
    )

    if course_progress:
        # Count completed assignments (either COMPLETED or GRADED status)
        completed_count = (
            db.query(AssignmentProgress)
            .join(Assignment, Assignment.id == AssignmentProgress.assignment_id)
            .filter(
                Assignment.course_id == course_id,
                AssignmentProgress.student_id == student_id,
                (AssignmentProgress.status == AssignmentStatus.COMPLETED) | 
                (AssignmentProgress.status == AssignmentStatus.GRADED)
            )
            .count()
        )
        
        print(f"Completed assignments count: {completed_count}")

        # Get total assignments
        total_assignments = (
            db.query(Assignment)
            .filter(Assignment.course_id == course_id)
            .count()
        )
        print(f"Total assignments in course: {total_assignments}")

        # Calculate completion percentage with proper type conversion
        try:
            completion_percentage = float(completed_count) / float(total_assignments) * 100.0 if total_assignments > 0 else 0.0
        except (TypeError, ZeroDivisionError):
            completion_percentage = 0.0
        
        print(f"Raw completion percentage: {completion_percentage}")
        
        # Update course progress with explicit type conversion
        course_progress.completed_assignments = int(completed_count)
        course_progress.total_assignments = int(total_assignments)
        course_progress.last_activity = datetime.now()
        
        db.commit()
        db.refresh(course_progress)
        
        print(f"Updated progress - Completed: {course_progress.completed_assignments}")
        print(f"Total: {course_progress.total_assignments}")
        print(f"Final Percentage: {course_progress.completion_percentage}%")

    return course_progress


@router.post("/assignments/{assignment_id}", response_model=AssignmentProgressResponse)
async def create_or_update_assignment_progress(
    assignment_id: int,
    progress_data: AssignmentProgressCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_jwt_required),
):
    """Create or update progress for an assignment"""
    user_id = current_user.get("user_id")

    # Students can only update their own progress
    if progress_data.student_id != user_id and current_user.get("role") not in [
        "teacher",
        "admin",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update progress for other students",
        )

    # Check if assignment exists
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    # Check if student is enrolled in the course
    if not check_enrollment(db, progress_data.student_id, assignment.course_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student is not enrolled in this course",
        )

    # Check if progress record already exists
    progress = (
        db.query(AssignmentProgress)
        .filter(
            AssignmentProgress.student_id == progress_data.student_id,
            AssignmentProgress.assignment_id == assignment_id,
        )
        .first()
    )

    if progress:
        # Update existing progress
        update_data = progress_data.model_dump(exclude_unset=True)
        update_data.pop("student_id", None)  # Cannot change student ID
        update_data.pop("assignment_id", None)  # Cannot change assignment ID

        for key, value in update_data.items():
            setattr(progress, key, value)

        # Update status based on submission and completion
        if progress_data.submission_file_key and progress.status == AssignmentStatus.NOT_STARTED:
            progress.status = AssignmentStatus.SUBMITTED
            progress.submitted_at = datetime.now()

        # Set timestamps based on status
        if progress.status == AssignmentStatus.COMPLETED or progress.status == AssignmentStatus.GRADED:
            if not progress.completed_at:
                progress.completed_at = datetime.now()

        db.commit()
        db.refresh(progress)
    else:
        # Create new progress record
        progress = AssignmentProgress(
            student_id=progress_data.student_id,
            assignment_id=assignment_id,
            **progress_data.model_dump(exclude={"student_id", "assignment_id"}),
        )

        # Set initial status and timestamps
        if progress.submission_file_key:
            if progress.status == AssignmentStatus.NOT_STARTED:
                progress.status = AssignmentStatus.SUBMITTED
            progress.submitted_at = progress.submitted_at or datetime.now()
        
        if progress.status in [AssignmentStatus.COMPLETED, AssignmentStatus.GRADED]:
            progress.completed_at = progress.completed_at or datetime.now()

        db.add(progress)
        db.commit()
        db.refresh(progress)

    # Update course progress
    update_course_progress(db, progress_data.student_id, assignment.course_id)

    return progress


@router.get(
    "/assignments/{assignment_id}/student/{student_id}",
    response_model=AssignmentProgressResponse,
)
async def get_assignment_progress(
    assignment_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_jwt_required),
):
    """Get progress for an assignment"""
    user_id = current_user.get("user_id")

    # Students can only view their own progress
    if student_id != user_id and current_user.get("role") not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view progress for other students",
        )

    # Check if assignment exists
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    # Get progress
    progress = get_student_assignment_progress(db, student_id, assignment_id)

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found",
        )

    return progress


@router.put("/assignments/{assignment_id}", response_model=AssignmentProgressResponse)
async def update_assignment_progress(
    assignment_id: int,
    progress_data: AssignmentProgressUpdate,
    student_id: int = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_jwt_required),
):
    """Update progress for an assignment"""
    user_id = current_user.get("user_id")

    # If student_id not provided, use current user's ID
    if not student_id:
        student_id = user_id

    # Students can only update their own progress
    if student_id != user_id and current_user.get("role") not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update progress for other students",
        )

    # Check if assignment exists
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    # Check if student is enrolled in the course
    if not check_enrollment(db, student_id, assignment.course_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student is not enrolled in this course",
        )

    # Get progress
    progress = get_student_assignment_progress(db, student_id, assignment_id)

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found",
        )

    # Update progress
    update_data = progress_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(progress, key, value)

    # Automatic status updates based on other field changes

    # If marking as complete or graded, set completed_at
    if progress.status in [AssignmentStatus.COMPLETED, AssignmentStatus.GRADED] and not progress.completed_at:
        progress.completed_at = datetime.now()
            
    # If submitting file, set submitted_at
    if (
        progress_data.submission_file_key and 
        progress_data.submission_file_key != progress.submission_file_key
    ):
        # Update status to SUBMITTED if not already GRADED or COMPLETED
        if progress.status not in [AssignmentStatus.GRADED, AssignmentStatus.COMPLETED]:
            progress.status = AssignmentStatus.SUBMITTED
        
        progress.submitted_at = datetime.now()

    db.commit()
    db.refresh(progress)

    # Update course progress
    update_course_progress(db, student_id, assignment.course_id)

    return progress


@router.get(
    "/courses/{course_id}/student/{student_id}",
    response_model=CourseProgressResponse,
)
async def get_course_progress(
    course_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_jwt_required),
):
    """Get progress for a course"""
    user_id = current_user.get("user_id")

    # Students can only view their own progress
    if student_id != user_id and current_user.get("role") not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view progress for other students",
        )

    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    # Check if student is enrolled in the course
    if not check_enrollment(db, student_id, course_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student is not enrolled in this course",
        )

    # Get or create progress
    progress = get_or_create_course_progress(db, student_id, course_id)

    return progress


@router.get(
    "/courses/{course_id}/assignments",
    response_model=List[AssignmentWithProgressResponse],
)
async def get_assignments_with_progress(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_jwt_required),
):
    """Get all assignments for a course with progress for the current user"""
    from backend.controllers.filesForCourse import BUCKET_NAME, s3
    
    user_id = current_user.get("user_id")

    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    # Check if user is teacher of the course or enrolled
    is_teacher = course.teacher_id == user_id
    is_admin = current_user.get("role") == "admin"

    if not (is_teacher or is_admin):
        # Check if student is enrolled
        if not check_enrollment(db, user_id, course_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this course",
            )

    # Get all assignments for the course
    assignments = db.query(Assignment).filter(Assignment.course_id == course_id).all()

    # Get progress for each assignment with an explicit flush to ensure data is current
    db.flush()
    
    # Refresh the session to ensure we get the latest data
    db.expire_all()
    
    result = []
    for assignment in assignments:
        # Use a fresh query to get the most up-to-date progress
        progress = (
            db.query(AssignmentProgress)
            .filter(
                AssignmentProgress.student_id == user_id,
                AssignmentProgress.assignment_id == assignment.id,
            )
            .first()
        )

        assignment_dict = assignment.to_dict()
        
        # Ensure files field exists
        assignment_dict["files"] = []
        
        # Try to get files from S3 if they exist
        try:
            prefix = f"assignments/{assignment.id}/task/"
            response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)

            if "Contents" in response:
                files = []
                for item in response["Contents"]:
                    files.append(
                        {
                            "key": item["Key"],
                            "size": item["Size"],
                            "last_modified": item["LastModified"],
                            "filename": item["Key"].split("/")[-1],
                        },
                    )
                assignment_dict["files"] = files
        except Exception as e:
            print(f"Error getting files for assignment {assignment.id}: {str(e)}")

        if progress:
            assignment_dict.update(
                {
                    "is_completed": progress.is_completed,
                    "status": progress.status,
                    "submission_file_key": progress.submission_file_key,
                    "score": progress.score,
                    "feedback": progress.feedback,
                },
            )
        else:
            assignment_dict.update(
                {
                    "is_completed": False,
                    "status": AssignmentStatus.NOT_STARTED,
                    "submission_file_key": None,
                    "score": None,
                    "feedback": None,
                },
            )

        result.append(AssignmentWithProgressResponse(**assignment_dict))

    return result


@router.post("/mark-assignment-complete/{assignment_id}", response_model=AssignmentProgressResponse)
async def mark_assignment_complete(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_jwt_required),
):
    """
    Mark an assignment as complete (for assignments that don't require file submission).
    Use this endpoint only for tasks that don't need file uploads.
    For assignments requiring file submission, use /files/assignments/{assignment_id}/submit instead.
    """
    user_id = current_user.get("user_id")

    # Check if assignment exists
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    # Check if student is enrolled in the course
    if not check_enrollment(db, user_id, assignment.course_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not enrolled in this course"
        )

    # Check if progress record already exists with explicit locking for update
    progress = (
        db.query(AssignmentProgress)
        .filter(
            AssignmentProgress.student_id == user_id,
            AssignmentProgress.assignment_id == assignment_id,
        )
        .with_for_update()  # Lock the row to prevent concurrent updates
        .first()
    )

    if progress:
        # Update existing record
        progress.status = AssignmentStatus.COMPLETED
        if not progress.completed_at:
            progress.completed_at = datetime.now()
    else:
        # Create new progress record
        progress = AssignmentProgress(
            student_id=user_id,
            assignment_id=assignment_id,
            status=AssignmentStatus.COMPLETED,
            completed_at=datetime.now()
        )
        db.add(progress)

    # Explicitly flush changes to database before commit
    db.flush()
    db.commit()
    
    # Get a fresh copy of the progress to ensure we have the latest data
    db.refresh(progress)

    # Update course progress
    update_course_progress(db, user_id, assignment.course_id)

    return progress


def get_student_assignment_progress(
    db: Session,
    student_id: int,
    assignment_id: int,
) -> Optional[AssignmentProgress]:
    """
    Get progress for a specific assignment.

    Args:
        db: Database session
        student_id: ID of the student
        assignment_id: ID of the assignment

    Returns:
        Optional[AssignmentProgress]: Progress record if found, None otherwise
    """
    return (
        db.query(AssignmentProgress)
        .filter(
            AssignmentProgress.student_id == student_id,
            AssignmentProgress.assignment_id == assignment_id,
        )
        .first()
    )


# Schema for grading assignments
class AssignmentGradeRequest(BaseModel):
    score: int
    feedback: Optional[str] = None


@router.post(
    "/assignments/{assignment_id}/student/{student_id}/grade",
    response_model=AssignmentProgressResponse,
)
async def grade_assignment(
    assignment_id: int,
    student_id: int,
    grade_data: AssignmentGradeRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_jwt_required),
):
    """
    Grade an assignment by providing a score and optional feedback.
    Only teachers or admins can grade assignments.
    """
    user_id = current_user.get("user_id")
    user_role = current_user.get("role")

    # Check if assignment exists
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    # Get the course
    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Verify permission to grade (teacher of the course or admin)
    is_teacher = course.teacher_id == user_id
    is_admin = user_role == "admin"
    
    if not (is_teacher or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the course teacher or an admin can grade assignments"
        )

    # Check if the student is enrolled in the course
    if not check_enrollment(db, student_id, course.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student is not enrolled in this course"
        )

    # Get the assignment progress record with row-level locking
    progress = (
        db.query(AssignmentProgress)
        .filter(
            AssignmentProgress.student_id == student_id,
            AssignmentProgress.assignment_id == assignment_id
        )
        .with_for_update()
        .first()
    )

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No submission found for this assignment"
        )

    # Update the grade and feedback
    progress.score = grade_data.score
    progress.feedback = grade_data.feedback
    progress.status = AssignmentStatus.GRADED

    # Set completed_at if not already set
    if not progress.completed_at:
        progress.completed_at = datetime.now()

    # Commit changes
    db.flush()
    db.commit()
    db.refresh(progress)
    
    # Update course progress to ensure completed_assignments is updated
    update_course_progress(db, student_id, course.id)

    # Notify the student through WebSocket if they're connected
    try:
        student_room_id = f"user_{student_id}"
        await manager.broadcast_to_room(
            {
                "event": "assignment_graded",
                "assignment_id": assignment_id,
                "course_id": course.id,
                "score": progress.score,
                "feedback": progress.feedback,
                "status": progress.status
            },
            student_room_id
        )
    except Exception as e:
        # Log the error but don't fail the request
        print(f"Error sending WebSocket notification: {str(e)}")

    return progress
