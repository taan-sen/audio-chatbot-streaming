# Audio Chatbot Frontend

A minimal Angular frontend for the audio chatbot that allows users to ask questions and receive audio responses via WebSocket streaming.

## Features

- Clean, minimal UI for asking questions
- Real-time audio streaming via WebSocket
- Configurable API endpoints
- Live audio playback in browser

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

The app will open at http://localhost:4200

## Configuration

API endpoints can be modified in `src/config/api.config.ts`:

```typescript
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000',
  WEBSOCKET_URL: 'ws://localhost:8000/ws/voice'
};
```

## Usage

1. Type your question in the textarea
2. Click "Ask" to send the question to the backend
3. The app will connect to the WebSocket and stream audio response
4. Audio will play automatically when received

## Build for Production

```bash
ng build --configuration production
```

Built files will be in the `dist/` directory.
