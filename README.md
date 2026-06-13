# Acme Logistics — Inbound Carrier Sales

An automated inbound carrier sales assistant that qualifies freight carriers via phone and books loads.

## Setup

### Backend (local development)

**Prerequisites:** Python 3.11+

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment — copy the example and fill in real values
cp ../.env.example ../.env
```

Edit `.env` at the repo root with your actual `API_KEY` and other values (see `.env.example` for descriptions).

```bash
# Run the dev server (auto-reload on file changes)
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## Deployment

_TODO_

## Architecture

_TODO_
