# Clock Bucks

A FastAPI app that calculates how much your meetings cost based on participant salaries. Because someone should be keeping track.

## Setup

**Prerequisites:** Python 3.11+, and optionally PostgreSQL (SQLite works for dev).

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn src.main:app --reload
```

Or use the start script:

```bash
# Mac/Linux
chmod +x start.sh && ./start.sh

# Windows
start.bat
```

The API will be at `http://localhost:8000` and docs at `http://localhost:8000/docs`.

### Quick demo

```bash
python dev_test.py
```

Runs sample meeting cost calculations so you can see it working without starting the server.

## Project structure

```
src/
├── main.py              # FastAPI app
├── config.py            # Settings
├── database.py          # DB setup (SQLAlchemy)
├── services/
│   └── calculator.py    # The actual cost calculation logic
├── routes/
│   ├── meetings.py      # Meeting endpoints
│   └── participants.py  # Participant endpoints
├── models/              # Pydantic schemas + SQLAlchemy models
├── repositories/        # Data access layer
└── middleware/
    └── security.py      # Rate limiting, security headers
tests/
├── conftest.py
└── test_api.py
```

## API endpoints

**Meetings:**
- `POST /api/v1/meetings/calculate` - Calculate meeting cost
- `POST /api/v1/meetings/real-time-cost` - Real-time cost tracking
- `GET /api/v1/meetings` - List meetings
- `POST /api/v1/meetings` - Create a meeting
- `GET /api/v1/meetings/{id}` - Get meeting details
- `GET /api/v1/meetings/statistics/overview` - Stats

**Participants:**
- Full CRUD at `/api/v1/participants`

**System:**
- `GET /health` - Health check
- `GET /docs` - Interactive API docs

## Docker

```bash
# Dev
docker-compose up --build

# Prod
docker-compose -f docker-compose.prod.yml up -d
```

There are also Kubernetes manifests in `k8s/` if you're into that.

## Running tests

```bash
pytest tests/ -v --cov=src
```

## Config

Uses env vars. Copy `.env.example` to `.env` for local dev:

```
DEBUG=true
DATABASE_URL=sqlite:///./clockbucks.db
ALLOWED_ORIGINS=http://localhost:3000
RATE_LIMIT_ENABLED=false
```

## Dev commands

```bash
make run          # Start dev server
make test         # Run tests
make format       # Black + isort
make lint         # Flake8 + mypy
make help         # See all commands
```

## License

MIT
