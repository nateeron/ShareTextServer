"""
Real-time Collaborative Text Editor - Server
============================================

This server provides WebSocket and REST API endpoints for real-time
collaborative text editing. It handles:
- WebSocket connections for real-time updates
- REST API for getting/updating text content
- Broadcasting updates to all connected clients
- Simple conflict resolution
"""

import json
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import configuration
from config import Config

# Data models
class TextUpdate(BaseModel):
    content: str
    user_id: Optional[str] = "anonymous"
    timestamp: Optional[datetime] = None

class TextResponse(BaseModel):
    content: str
    last_updated: datetime
    user_count: int

# Global state
connected_clients: List[WebSocket] = []
current_text: str = ""
last_updated: datetime = datetime.now()
user_count: int = 0

# File for persistence
TEXT_FILE = Config.TEXT_FILE

# Load existing text if file exists
if os.path.exists(TEXT_FILE):
    with open(TEXT_FILE, 'r', encoding='utf-8') as f:
        current_text = f.read()

app = FastAPI(title="Collaborative Text Editor API")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Collaborative Text Editor API",
        "endpoints": {
            "GET /text": "Get current text content",
            "POST /text": "Update text content",
            "GET /status": "Get server status",
            "WebSocket /ws": "Real-time updates"
        }
    }

@app.get("/text", response_model=TextResponse)
async def get_text():
    """Get current text content"""
    return TextResponse(
        content=current_text,
        last_updated=last_updated,
        user_count=len(connected_clients)
    )

@app.post("/text")
async def update_text(update: TextUpdate):
    """Update text content via REST API"""
    global current_text, last_updated
    
    if update.timestamp is None:
        update.timestamp = datetime.now()
    
    current_text = update.content
    last_updated = update.timestamp
    
    # Save to file
    with open(TEXT_FILE, 'w', encoding='utf-8') as f:
        f.write(current_text)
    
    # Broadcast to all connected clients
    await broadcast_update(update)
    
    return {"message": "Text updated successfully", "timestamp": update.timestamp}

@app.get("/status")
async def get_status():
    """Get server status"""
    return {
        "connected_clients": len(connected_clients),
        "text_length": len(current_text),
        "last_updated": last_updated,
        "file_path": TEXT_FILE
    }

async def broadcast_update(update: TextUpdate):
    """Broadcast text update to all connected WebSocket clients"""
    if connected_clients:
        message = {
            "type": "text_update",
            "content": update.content,
            "user_id": update.user_id,
            "timestamp": update.timestamp.isoformat() if update.timestamp else None
        }
        
        # Send to all connected clients
        await asyncio.gather(
            *[client.send_text(json.dumps(message)) for client in connected_clients],
            return_exceptions=True
        )

async def send_initial_state(websocket: WebSocket):
    """Send current state to a newly connected client"""
    message = {
        "type": "initial_state",
        "content": current_text,
        "last_updated": last_updated.isoformat(),
        "user_count": len(connected_clients)
    }
    await websocket.send_text(json.dumps(message))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    global user_count
    
    await websocket.accept()
    connected_clients.append(websocket)
    user_count = len(connected_clients)
    
    print(f"Client connected. Total clients: {user_count}")
    
    # Send current state to new client
    await send_initial_state(websocket)
    
    # Broadcast user count update
    await broadcast_user_count()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "text_update":
                # Handle text update from client
                update = TextUpdate(
                    content=message["content"],
                    user_id=message.get("user_id", "anonymous"),
                    timestamp=datetime.now()
                )
                
                # Update global state
                global current_text, last_updated
                current_text = update.content
                last_updated = update.timestamp
                
                # Save to file
                with open(TEXT_FILE, 'w', encoding='utf-8') as f:
                    f.write(current_text)
                
                # Broadcast to all other clients
                await broadcast_update(update)
                
                print(f"Text updated by {update.user_id}")
    
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        user_count = len(connected_clients)
        print(f"Client disconnected. Total clients: {user_count}")
        
        # Broadcast updated user count
        await broadcast_user_count()
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in connected_clients:
            connected_clients.remove(websocket)
            user_count = len(connected_clients)
            await broadcast_user_count()

async def broadcast_user_count():
    """Broadcast updated user count to all clients"""
    if connected_clients:
        message = {
            "type": "user_count_update",
            "user_count": user_count
        }
        
        await asyncio.gather(
            *[client.send_text(json.dumps(message)) for client in connected_clients],
            return_exceptions=True
        )

if __name__ == "__main__":
    print("Starting Collaborative Text Editor Server...")
    print(f"API Documentation: {Config.get_api_docs_url()}")
    print(f"WebSocket endpoint: {Config.get_websocket_url()}")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "server:app",
        host=Config.SERVER_HOST,
        port=Config.SERVER_PORT,
        reload=True,
        log_level=Config.LOG_LEVEL
    )
