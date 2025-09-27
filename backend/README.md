# Audio Chatbot Backend

FastAPI backend that processes questions via LLM (Groq) and streams audio responses via WebSocket.

## Setup

1. **Get Groq API Key** (FREE):
   - Go to https://console.groq.com/
   - Sign up for free account
   - Get your API key from the dashboard

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure API Key**:
   - Open `main.py`
   - Replace `YOUR_GROQ_API_KEY_HERE` with your actual Groq API key

4. **Run the server**:
```bash
python main.py
```

Server will start on http://localhost:8000

## API Endpoints

- `POST /ask` - Submit question, returns session_id
- `WebSocket /ws/voice/{session_id}` - Stream audio response

## Features

- **Free LLM**: Uses Groq's free Llama3 model
- **Free TTS**: Uses Google Text-to-Speech (gTTS)
- **CORS Enabled**: Configured for frontend on localhost:4200
- **WebSocket Streaming**: Real-time audio chunk delivery
- **Session Management**: Unique session IDs for each request

## API Key Location

**IMPORTANT**: Replace the API key in `main.py` line 13:
```python
GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"  # PUT YOUR ACTUAL KEY HERE
```
