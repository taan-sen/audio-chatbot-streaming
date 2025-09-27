import asyncio
import uuid
import io
import os
from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from gtts import gTTS

# Get API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is required")

app = FastAPI()

# CORS middleware - allow all origins for flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Store active sessions
active_sessions: Dict[str, dict] = {}

class QuestionRequest(BaseModel):
    question: str

@app.post("/api/ask")
async def ask_question(request: QuestionRequest):
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {
        "question": request.question,
        "status": "pending"
    }
    return {"session_id": session_id}

@app.websocket("/api/ws/voice/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    if session_id not in active_sessions:
        await websocket.close(code=4004, reason="Session not found")
        return
    
    try:
        session = active_sessions[session_id]
        question = session["question"]
        
        # Get streaming LLM response from Groq
        stream = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a voice assistant that will be spoken aloud. Keep answers conversational and concise for audio playback. Do NOT output code blocks, tables, or long preformatted text. Keep replies natural, short sentences. Aim for 30–80 words for normal answers. If user asks for steps, enumerate them briefly (1., 2., ...), each as a short sentence. Do not include internal metadata or special tokens. Output plain text only."},
                {"role": "user", "content": question}
            ],
            model="llama-3.1-8b-instant",
            max_tokens=1000,
            temperature=0.7,
            stream=True
        )
        
        text_buffer = ""
        chunk_size = 50  # Process text in chunks of ~50 characters
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                text_buffer += chunk.choices[0].delta.content
                
                # Process complete sentences or when buffer is large enough
                while len(text_buffer) >= chunk_size or '.' in text_buffer or '!' in text_buffer or '?' in text_buffer:
                    if '.' in text_buffer or '!' in text_buffer or '?' in text_buffer:
                        # Find the last sentence ending
                        for punct in ['.', '!', '?']:
                            if punct in text_buffer:
                                idx = text_buffer.rfind(punct)
                                if idx != -1:
                                    text_chunk = text_buffer[:idx+1].strip()
                                    text_buffer = text_buffer[idx+1:].strip()
                                    break
                    else:
                        # Take chunk_size characters
                        text_chunk = text_buffer[:chunk_size].strip()
                        text_buffer = text_buffer[chunk_size:].strip()
                    
                    if text_chunk and text_chunk.strip():
                        # Convert text chunk to audio
                        try:
                            tts = gTTS(text=text_chunk, lang='en', slow=False)
                            audio_buffer = io.BytesIO()
                            tts.write_to_fp(audio_buffer)
                            audio_data = audio_buffer.getvalue()
                            
                            # Send audio chunk
                            await websocket.send_bytes(audio_data)
                            await asyncio.sleep(0.1)  # Small delay between chunks
                        except Exception as tts_error:
                            print(f"TTS error for chunk '{text_chunk}': {tts_error}")
                            continue
        
        # Process any remaining text
        if text_buffer.strip():
            try:
                tts = gTTS(text=text_buffer.strip(), lang='en', slow=False)
                audio_buffer = io.BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_data = audio_buffer.getvalue()
                await websocket.send_bytes(audio_data)
            except Exception as tts_error:
                print(f"TTS error for remaining text '{text_buffer.strip()}': {tts_error}")
        
        # Send end signal
        await websocket.send_text("END")
        await websocket.close()
        
        # Clean up session
        del active_sessions[session_id]
        
    except WebSocketDisconnect:
        if session_id in active_sessions:
            del active_sessions[session_id]
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")
        await websocket.close()

@app.get("/api/health")
async def health():
    return {"message": "Audio Chatbot Backend Running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
