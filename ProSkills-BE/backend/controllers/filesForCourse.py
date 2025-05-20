from typing import List, Optional, Tuple
from uuid import uuid4
from datetime import datetime
import os

import boto3
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Query, status
from fastapi.responses import FileResponse, Response, StreamingResponse
from sqlalchemy.orm import Session

from backend.dependencies.getdb import get_db
from backend.models import Assignment, AssignmentProgress, Course, Enrollment, OurUsers
from backend.models.progress import AssignmentStatus
from backend.oauth2 import get_current_user_jwt
from backend.config import get_settings
from backend.schemas.file import (
    FileDeleteResponse,
    FileResponseSchema,
    FileUploadResponse,
    SubmissionResponseSchema,
)

# Get AWS credentials from settings
settings = get_settings()
BUCKET_NAME = settings.BUCKET_NAME

# Initialize S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.ACCESS_KEY_ID,
    aws_secret_access_key=settings.SECRET_ACCESS_KEY,
    region_name="us-east-1",  # Specify your region
)

router = APIRouter(prefix="/file-storage", tags=["file-storage"])

TEMP_DOWNLOAD_DIR = "temp_downloads"

os.makedirs(TEMP_DOWNLOAD_DIR, exist_ok=True)

# File size limits (in bytes)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_CONTENT_TYPES = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/zip",
    "text/plain",
    "text/csv",
    "image/jpeg",
    "image/png",
    "image/gif",
    "application/x-python-code",
    "text/x-python",
    "application/json",
    "application/xml",
    "text/markdown",
]


# Helper function to check file type and size
async def validate_file(file: Optional[UploadFile] = None):
    # If no file provided, return None to indicate optional file
    if not file or not file.filename:
        return None

    # Check content type
    content_type = file.content_type
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {content_type} not allowed",
        )

    # Check file size
    try:
        # Read first chunk to check size without loading entire file
        first_chunk = await file.read(MAX_FILE_SIZE + 1)
        if len(first_chunk) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024 * 1024)} MB",
            )

        # Reset file position for later reading
        await file.seek(0)
        return first_chunk
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating file: {str(e)}",
        )


# Helper function to check course enrollment
def check_enrollment(db: Session, user_id: int, course_id: int) -> bool:
    return (
        db.query(Enrollment)
        .filter(Enrollment.user_id == user_id, Enrollment.course_id == course_id)
        .first()
        is not None
    )


# Helper function to check course ownership
def check_course_ownership(db: Session, user_id: int, course_id: int) -> bool:
    return (
        db.query(Course)
        .filter(Course.id == course_id, Course.teacher_id == user_id)
        .first()
        is not None
    )


@router.get("", response_model=List[FileResponseSchema])
async def get_all_files(
    course_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user_jwt),
    db: Session = Depends(get_db),
):
    """
    Get all files or files for a specific course
    """
    try:
        user_id = current_user.get("user_id")
        user_role = current_user.get("role")

        # If course_id provided, verify course exists and user has access
        if course_id:
            course = db.query(Course).filter(Course.id == course_id).first()
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Course not found",
                )

            # Verify user has permission to view course files
            if (
                user_role not in ["teacher", "admin"]
                and not check_course_ownership(db, user_id, course_id)
                and not check_enrollment(db, user_id, course_id)
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view files for this course",
                )

            # Filter by course prefix in S3
            prefix = f"course_{course_id}/"
            response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
        else:
            # For non-admin/teacher users, only show files from their courses
            if user_role not in ["teacher", "admin"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view all files",
                )

            # Get all files
            response = s3.list_objects_v2(Bucket=BUCKET_NAME)

        if "Contents" not in response:
            return []

        files = []
        for item in response.get("Contents", []):
            files.append(
                FileResponseSchema(
                    filename=item["Key"].split("/")[-1],
                    file_key=item["Key"],
                    file_size=item["Size"],
                    content_type=s3.head_object(Bucket=BUCKET_NAME, Key=item["Key"]).get("ContentType", "application/octet-stream"),
                    upload_time=item["LastModified"],
                ),
            )
        return files

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving files: {str(e)}",
        )


@router.post("", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    course_id: Optional[int] = Form(None),
    current_user: dict = Depends(get_current_user_jwt),
    db: Session = Depends(get_db),
):
    """
    Upload a file to S3
    """
    try:
        # Validate file
        file_content = await validate_file(file)

        user_id = current_user.get("user_id")
        user_role = current_user.get("role")

        # If course_id provided, verify course exists and user has permissions
        if course_id:
            course = db.query(Course).filter(Course.id == course_id).first()
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Course not found",
                )

            # Verify user has permission to upload to this course
            if user_role not in ["teacher", "admin"] and not check_course_ownership(
                db,
                user_id,
                course_id,
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to upload to this course",
                )

            # Create a prefix for this course
            key = f"course_{course_id}/{uuid4().hex}_{file.filename}"
        else:
            # Only admins and teachers can upload general files
            if user_role not in ["teacher", "admin"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to upload general files",
                )

            # Generate a unique filename with a folder structure to avoid collisions
            timestamp = datetime.now().strftime("%Y%m%d")
            unique_filename = f"{uuid4().hex}_{file.filename}"
            key = f"general/{timestamp}/{unique_filename}"

        # Upload directly from memory to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=file_content,
            ContentType=file.content_type,
        )

        return FileUploadResponse(message="File uploaded successfully", file_key=key)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}",
        )


@router.post("/assignments/{assignment_id}/submit", response_model=FileResponseSchema)
async def submit_assignment(
    assignment_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_jwt),
):
    """
    Submit an assignment with a file upload.
    
    This endpoint:
    1. Uploads the submission file
    2. Automatically marks the assignment as submitted (but not completed)
    3. Updates the course progress
    
    Note: For assignments that don't require a file submission,
    use /progress/mark-assignment-complete/{assignment_id} instead.
    """
    from backend.controllers.progress import update_course_progress
    
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

    try:
        # 1. Upload the file
        file_key = f"assignments/{assignment_id}/student_{user_id}/{file.filename}"
        file_content = await validate_file(file)
        
        # Upload to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_key,
            Body=file_content,
            ContentType=file.content_type,
        )

        # 2. Create or update assignment progress with row locking to prevent concurrent modifications
        progress = (
            db.query(AssignmentProgress)
            .filter(
                AssignmentProgress.student_id == user_id,
                AssignmentProgress.assignment_id == assignment_id
            )
            .with_for_update()  # Lock the row to prevent concurrent updates
            .first()
        )

        if not progress:
            progress = AssignmentProgress(
                student_id=user_id,
                assignment_id=assignment_id,
                submission_file_key=file_key,
                status=AssignmentStatus.SUBMITTED,
                submitted_at=datetime.now()
            )
            db.add(progress)
        else:
            progress.submission_file_key = file_key
            progress.status = AssignmentStatus.SUBMITTED
            progress.submitted_at = datetime.now()

        # Explicitly flush changes to database before commit
        db.flush()
        db.commit()
        
        # Get a fresh copy of the progress object to ensure we have the latest data
        db.refresh(progress)

        # 3. Update course progress
        update_course_progress(db, user_id, assignment.course_id)

        return FileResponseSchema(
            filename=file.filename,
            file_key=file_key,
            file_size=file.size,
            content_type=file.content_type,
            upload_time=datetime.now(),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit assignment: {str(e)}"
        )


@router.get(
    "/assignments/{assignment_id}/task",
    response_model=List[FileResponseSchema],
)
async def get_assignment_files(
    assignment_id: int,
    current_user: dict = Depends(get_current_user_jwt),
    db: Session = Depends(get_db),
):
    """
    Get all files for a specific assignment
    """
    try:
        user_id = current_user.get("user_id")
        user_role = current_user.get("role")

        # Check if assignment exists
        assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found",
            )

        # Get the associated course
        course = db.query(Course).filter(Course.id == assignment.course_id).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )

        # Verify access permissions
        if (
            user_role not in ["teacher", "admin"]
            and course.teacher_id != user_id
            and not check_enrollment(db, user_id, course.id)
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view assignment files",
            )

        # Filter by assignment prefix in S3
        prefix = f"assignments/{assignment_id}/task/"
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)

        if "Contents" not in response:
            return []

        files = []
        for item in response.get("Contents", []):
            files.append(
                FileResponseSchema(
                    filename=item["Key"].split("/")[-1],
                    file_key=item["Key"],
                    file_size=item["Size"],
                    content_type=s3.head_object(Bucket=BUCKET_NAME, Key=item["Key"]).get("ContentType", "application/octet-stream"),
                    upload_time=item["LastModified"],
                ),
            )
        return files

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving assignment files: {str(e)}",
        )


@router.get(
    "/assignments/{assignment_id}/submissions",
    response_model=List[FileResponseSchema],
)
async def get_assignment_submissions(
    assignment_id: int,
    student_id: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user_jwt),
    db: Session = Depends(get_db),
):
    """
    Get all submissions for a specific assignment
    """
    try:
        user_id = current_user.get("user_id")
        user_role = current_user.get("role")

        # Check if assignment exists
        assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found",
            )

        # Get the associated course
        course = db.query(Course).filter(Course.id == assignment.course_id).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )

        # Teachers and admins can see all submissions, students can only see their own
        if user_role in ["teacher", "admin"] or course.teacher_id == user_id:
            # Teacher can see all submissions or filter by student
            prefix = f"assignments/{assignment_id}/"
            if student_id:
                prefix = f"assignments/{assignment_id}/student_{student_id}/"
        elif user_role == "student":
            # Students can only see their own submissions
            if student_id and student_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view other student submissions",
                )

            # Check if student is enrolled in the course
            if not check_enrollment(db, user_id, course.id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not enrolled in this course",
                )

            prefix = f"assignments/{assignment_id}/student_{user_id}/"
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view submissions",
            )

        # Get submissions from S3
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)

        if "Contents" not in response:
            return []

        files = []
        for item in response.get("Contents", []):
            files.append(
                FileResponseSchema(
                    filename=item["Key"].split("/")[-1],
                    file_key=item["Key"],
                    file_size=item["Size"],
                    content_type=s3.head_object(Bucket=BUCKET_NAME, Key=item["Key"]).get("ContentType", "application/octet-stream"),
                    upload_time=item["LastModified"],
                ),
            )
        return files

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving assignment submissions: {str(e)}",
        )


@router.get(
    "/course/{course_id}/submissions",
    response_model=List[SubmissionResponseSchema],
)
async def get_course_submissions(
    course_id: int,
    student_id: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user_jwt),
    db: Session = Depends(get_db),
):
    """
    Get all submissions for all assignments in a course that haven't been checked/graded yet,
    optionally filtered by student_id.
    Teachers can see all pending submissions or filter by student.
    Students can only see their own pending submissions.
    """
    try:
        user_id = current_user.get("user_id")
        user_role = current_user.get("role")

        # Check if course exists
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )

        # Get all assignments for this course
        assignments = db.query(Assignment).filter(Assignment.course_id == course_id).all()
        if not assignments:
            return []  # No assignments in this course

        # Создаем словарь для быстрого поиска названий заданий по ID
        assignment_titles = {a.id: a.title for a in assignments}

        # Set access control based on user role
        is_teacher = course.teacher_id == user_id
        is_admin = user_role in ["teacher", "admin"]
        
        # Teachers and admins can see all submissions, students can only see their own
        if is_teacher or is_admin:
            # Teacher/admin can filter by student if provided
            target_student_id = student_id if student_id else None
        elif user_role == "student":
            # Students can only see their own submissions
            if student_id and student_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view other student submissions",
                )

            # Check if student is enrolled in the course
            if not check_enrollment(db, user_id, course_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not enrolled in this course",
                )
            
            # Force student_id to be current user
            target_student_id = user_id
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view submissions",
            )

        # Если запрашиваются конкретные студенты, получаем информацию о них
        students_info = {}
        if target_student_id:
            student = db.query(OurUsers).filter(OurUsers.id == target_student_id).first()
            if student:
                students_info[student.id] = f"{student.first_name} {student.last_name}"
        
        # Collect all files across assignments
        all_files = []
        
        for assignment in assignments:
            # Get assignment progress records to filter out already graded/completed submissions
            if target_student_id:
                # For specific student, get their progress
                progress_records = (
                    db.query(AssignmentProgress)
                    .filter(
                        AssignmentProgress.assignment_id == assignment.id,
                        AssignmentProgress.student_id == target_student_id,
                        AssignmentProgress.status.in_([AssignmentStatus.SUBMITTED])  # Only get SUBMITTED status
                    )
                    .all()
                )
                # Skip if this student's submission is already graded or not submitted
                if not progress_records:
                    continue
                
                # Build the S3 prefix for this student
                prefix = f"assignments/{assignment.id}/student_{target_student_id}/"
            else:
                # For all students, get progress records with SUBMITTED status
                progress_records = (
                    db.query(AssignmentProgress)
                    .filter(
                        AssignmentProgress.assignment_id == assignment.id,
                        AssignmentProgress.status.in_([AssignmentStatus.SUBMITTED])  # Only get SUBMITTED status
                    )
                    .all()
                )
                
                # Skip if no submissions or all submissions are already graded
                if not progress_records:
                    continue
                
                # Get student IDs with ungraded submissions
                student_ids = [record.student_id for record in progress_records]
                
                # Get student info for all these students
                students = db.query(OurUsers).filter(OurUsers.id.in_(student_ids)).all()
                for student in students:
                    students_info[student.id] = f"{student.first_name} {student.last_name}"
                
                # Get all submissions for this assignment (teacher/admin only)
                prefix = f"assignments/{assignment.id}/student_"
            
            # Query S3 for files
            response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
            
            if "Contents" in response:
                for item in response.get("Contents", []):
                    # Извлекаем ID студента из ключа файла, если возможно
                    file_key_parts = item["Key"].split("/")
                    file_student_id = None
                    if len(file_key_parts) >= 3 and file_key_parts[2].startswith("student_"):
                        try:
                            file_student_id = int(file_key_parts[2].split("_")[1])
                            
                            # Skip if this student's submission has already been graded
                            # (when we're fetching all students' submissions)
                            if not target_student_id:
                                # Check if this student's submission appears in our ungraded list
                                if file_student_id not in student_ids:
                                    continue
                            
                            # Если этого студента нет в нашем кэше, получаем его имя
                            if file_student_id not in students_info:
                                student = db.query(OurUsers).filter(OurUsers.id == file_student_id).first()
                                if student:
                                    students_info[file_student_id] = f"{student.first_name} {student.last_name}"
                        except (IndexError, ValueError):
                            pass

                    # Create file response object with assignment information
                    file_info = SubmissionResponseSchema(
                        filename=item["Key"].split("/")[-1],
                        file_key=item["Key"],
                        file_size=item["Size"],
                        content_type=s3.head_object(Bucket=BUCKET_NAME, Key=item["Key"]).get(
                            "ContentType", "application/octet-stream"
                        ),
                        upload_time=item["LastModified"],
                        assignment_id=assignment.id,
                        assignment_title=assignment_titles.get(assignment.id, ""),
                        student_id=file_student_id,
                        student_name=students_info.get(file_student_id, "")
                    )
                    all_files.append(file_info)
        
        return all_files

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving course submissions: {str(e)}",
        )


def validate_file_access(
    db: Session,
    file_key: str,
    current_user: dict,
) -> tuple[Course, bool]:
    """
    Validate user's access to a file.

    Args:
        db: Database session
        file_key: Key of the file in S3
        current_user: Current authenticated user

    Returns:
        tuple[Course, bool]: Course object and boolean indicating if user has access

    Raises:
        HTTPException: If file access is not allowed
    """
    # Extract course_id from file key
    try:
        course_id = int(file_key.split("/")[1].split("_")[1])
    except (IndexError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file key format",
        )

    # Get course
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    # Check access
    user_id = current_user.get("user_id")
    is_teacher = course.teacher_id == user_id
    is_admin = current_user.get("role") == "admin"
    is_enrolled = check_enrollment(db, user_id, course_id)

    if not (is_teacher or is_admin or is_enrolled):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this file",
        )

    return course, is_teacher or is_admin


def get_file_from_s3(file_key: str) -> Tuple[StreamingResponse, str]:
    """
    Get a file from S3 by its key and return it as a StreamingResponse
    """
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=file_key)
        content_type = response["ContentType"]
        filename = file_key.split("/")[-1]

        def iterfile():
            yield from response["Body"]

        return (
            StreamingResponse(
                iterfile(),
                media_type=content_type,
                headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            ),
            filename,
        )
    except s3.exceptions.NoSuchKey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"S3 service error: {str(e)}",
        )


@router.get("/download/{file_key:path}")
async def download_file(
    file_key: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_jwt),
) -> StreamingResponse:
    """
    Download a file from S3.

    Args:
        file_key: Key of the file in S3
        db: Database session
        current_user: Current authenticated user

    Returns:
        StreamingResponse: File streaming response

    Raises:
        HTTPException: If file access not allowed or file not found
    """
    try:
        # Get file from S3
        response = s3.get_object(Bucket=BUCKET_NAME, Key=file_key)
        content_type = response["ContentType"]
        filename = file_key.split("/")[-1]

        def iterfile():
            yield from response["Body"]

        return StreamingResponse(
            iterfile(),
            media_type=content_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except s3.exceptions.NoSuchKey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"S3 service error: {str(e)}",
        )


@router.delete(
    "/{file_key:path}",
    response_model=FileDeleteResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_file(
    file_key: str,
    current_user: dict = Depends(get_current_user_jwt),
    db: Session = Depends(get_db),
):
    """
    Delete a file from S3
    """
    try:
        # Check if file exists
        try:
            s3.head_object(Bucket=BUCKET_NAME, Key=file_key)
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {str(error)}",
            )

        user_id = current_user.get("user_id")
        user_role = current_user.get("role")

        # Only teachers and admins can delete files
        if user_role not in ["teacher", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete files",
            )

        # Additional checks for assignment/course-specific files
        if file_key.startswith("assignments/"):
            match = re.match(r"assignments/(\d+)/", file_key)
            if match:
                assignment_id = int(match.group(1))

                # Verify assignment exists and user has rights to it
                assignment = (
                    db.query(Assignment).filter(Assignment.id == assignment_id).first()
                )
                if assignment:
                    course = (
                        db.query(Course)
                        .filter(Course.id == assignment.course_id)
                        .first()
                    )

                    # If not admin, verify teacher owns the course
                    if user_role != "admin" and course and course.teacher_id != user_id:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to delete files for this assignment",
                        )

        elif file_key.startswith("course_"):
            match = re.match(r"course_(\d+)/", file_key)
            if match:
                course_id = int(match.group(1))

                # If not admin, verify teacher owns the course
                if user_role != "admin" and not check_course_ownership(
                    db,
                    user_id,
                    course_id,
                ):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Not authorized to delete files for this course",
                    )

        # Delete the file
        try:
            s3.delete_object(Bucket=BUCKET_NAME, Key=file_key)
        except boto3.exceptions.Boto3Error as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"S3 service error: {str(error)}",
            )

        return FileDeleteResponse(message="File deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting file: {str(e)}",
        )
