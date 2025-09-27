# Dockerized Audio Chatbot

Production-ready audio chatbot with streaming capabilities.

## Deployment URLs
- Frontend: `https://domain-name.com/audio-chatbot`
- Backend API: `https://domain-name.com/api`

## Docker Commands

### Build and Run
```bash
# Set your Groq API key
export GROQ_API_KEY="your_groq_api_key_here"

# Build and start services
docker-compose up --build

# Run in background
docker-compose up --build -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Production Deployment

For production deployment behind a reverse proxy (nginx/traefik), map port 80 to your desired port and configure your domain to point to the container.

The application will be accessible at:
- `https://yourdomain.com/audio-chatbot` (frontend)
- `https://yourdomain.com/api` (backend API)
