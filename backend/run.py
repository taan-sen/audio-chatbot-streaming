#!/usr/bin/env python3
import uvicorn
from main import app

if __name__ == "__main__":
    print("Starting Audio Chatbot Backend...")
    print("Server will be available at: http://localhost:8000")
    print("WebSocket endpoint: ws://localhost:8000/ws/voice/{session_id}")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
