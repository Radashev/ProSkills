from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.websockets import WebSocket, WebSocketDisconnect
import traceback
import time

from backend.controllers import (
    admin_stats,
    assignments,
    auth,
    courses,
    filesForCourse,
    progress,
    reviews,
    sections,
    students,
)
from backend.database import Base, engine
from backend.dependencies.getdb import get_db
from backend.middlewares.cors import setup_cors
from backend.services.websocket import manager
from backend.utils import create_admin_user
from backend.controllers.admin_stats import log_error

app = FastAPI()

setup_cors(app)
Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(students.router)
app.include_router(assignments.router)
app.include_router(filesForCourse.router)
app.include_router(sections.router)
app.include_router(progress.router)
app.include_router(admin_stats.router)
app.include_router(reviews.router)


@app.on_event("startup")
async def startup_event():
    """Initialize application data on startup"""
    db = next(get_db())
    try:
        # Create admin user if it doesn't exist
        create_admin_user(db)
    finally:
        db.close()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Основной WebSocket-эндпоинт для всех соединений"""
    # Принимаем соединение
    await manager.connect(websocket)
    
    try:
        while True:
            # Ожидаем сообщение от клиента
            data = await websocket.receive_json()
            
            # Обрабатываем различные команды от клиента
            if data.get("command") == "join_room":
                room_id = data.get("room_id")
                if room_id:
                    manager.join_room(websocket, room_id)
                    
                    # Отправляем подтверждение
                    await manager.send_personal_message(
                        {"event": "joined_room", "room_id": room_id},
                        websocket
                    )
            
            elif data.get("command") == "leave_room":
                room_id = data.get("room_id")
                if room_id:
                    manager.leave_room(websocket, room_id)
                    
                    # Отправляем подтверждение
                    await manager.send_personal_message(
                        {"event": "left_room", "room_id": room_id},
                        websocket
                    )
            
            elif data.get("command") == "join_user_room":
                user_id = data.get("user_id")
                if user_id:
                    user_room_id = f"user_{user_id}"
                    manager.join_room(websocket, user_room_id)
                    
                    # Отправляем подтверждение
                    await manager.send_personal_message(
                        {"event": "joined_user_room", "user_id": user_id},
                        websocket
                    )
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    
    except Exception as e:
        print(f"Error in WebSocket connection: {e}")
        manager.disconnect(websocket)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to log all unhandled exceptions
    """
    # Generate error details
    error_detail = {
        "url": str(request.url),
        "method": request.method,
        "exception_type": str(type(exc).__name__),
        "exception_msg": str(exc),
        "traceback": traceback.format_exc(),
        "timestamp": time.time()
    }
    
    # Log error for admin panel
    log_error(error_detail)
    
    # Print to console for debugging
    print(f"Unhandled exception: {exc}")
    print(traceback.format_exc())
    
    # Return error response to client
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error_type": str(type(exc).__name__)}
    )