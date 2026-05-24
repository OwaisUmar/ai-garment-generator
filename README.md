# AI Garment Generator

A full-stack AI-powered application that generates photorealistic garment images using:

- FastAPI (backend API)
- NiceGUI (frontend UI)
- Celery (async background processing)
- Redis (queue broker)
- PostgreSQL (database)
- OpenAI GPT-Image model (image generation)

## Features

- Upload garment / color / fabric as image or text
- AI-powered image generation using OpenAI
- Async processing with Celery workers
- Real-time job polling and status updates
- Feedback system with rating and comments
- Download generated images
- Responsive UI built with NiceGUI

## Architecture

```
Browser (NiceGUI UI)
↓
FastAPI (API Server)
↓
Celery Worker (background jobs)
↓
Redis (queue)
↓
PostgreSQL (job storage)
↓
OpenAI (image generation)
```

## Project Structure

```
ai-garment-generator/
│
├── api/                  # FastAPI routes
├── models/               # SQLAlchemy models
├── services/             # Generation service logic
├── tasks/                # Celery tasks
├── ui/                   # NiceGUI frontend
│   ├── screens/
│   ├── polling.py
│   ├── gui.py
│
├── config/
├── exceptions/
├── static/
│   ├── outputs/
│   └── uploads/
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy 2.0 (async)
- Celery
- Redis
- PostgreSQL
- NiceGUI
- OpenAI API (`gpt-image-1`)

## Environment Variables

Create a `.env` file with the following values:

```env
# Database
DATABASE_URL=postgresql+asyncpg://devuser:dev_pass@postgres:5432/ai_garment_generator

# Redis
REDIS_URL=redis://redis:6379/0

# OpenAI
OPENAI_API_KEY=your_openai_key

# API
API_URL=http://api:8000
PUBLIC_API_URL=http://localhost:8000
```

> Note: Adjust `DATABASE_URL`, `API_URL`, and `PUBLIC_API_URL` if you run services outside Docker or use different hostnames.

## Docker Setup

1. Build & start everything:

```bash
docker compose up --build
```

2. Run in background:

```bash
docker compose up -d
```

3. Stop services:

```bash
docker compose down
```

## Services in Docker

- `api` — FastAPI backend logic, serves `/generate`, `/jobs/{id}`, and static content
- `gui` — NiceGUI frontend UI on port `8080`
- `celery-worker` — Celery worker processing image generation jobs
- `redis` — Queue broker
- `postgres` — Job and feedback storage

## Getting Started

1. Create `.env` from the template above.
2. Start the stack with Docker Compose.
3. Open the UI at `http://localhost:8080`.
4. Upload a garment, color, or fabric input and start a generation job.
5. View status updates and download the generated images.

## Notes

- `static/outputs` and `static/uploads` are used to store generated and uploaded files.
- The backend and worker share the `static` volume so generated assets are available to the UI.
- Replace `OPENAI_API_KEY` with your own OpenAI key.
