# Clock Bucks - Meeting Cost Calculator

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready FastAPI backend service that estimates the cost of meetings based on participant salaries. Perfect for remote teams to understand the financial impact of their meetings and optimize time allocation.

## 🚀 Features

### Core Functionality
- **💰 Meeting Cost Calculation**: Accurate cost estimation based on participant hourly rates and duration
- **⏱️ Real-time Tracking**: Monitor costs during ongoing meetings
- **📊 Analytics & Statistics**: Detailed cost breakdowns and historical analysis
- **👥 Participant Management**: Complete CRUD operations for team members
- **📅 Meeting Management**: Track meeting history and patterns

### Production Features
- **🔐 Security**: Rate limiting, security headers, input validation
- **📝 Comprehensive Logging**: Structured logging with request tracking
- **🐘 Database Integration**: PostgreSQL with SQLAlchemy ORM
- **🧪 Full Test Coverage**: Unit and integration tests with pytest
- **🔄 Database Migrations**: Alembic for schema management
- **📈 Health Checks**: Kubernetes-ready health endpoints
- **🎯 Error Handling**: Comprehensive exception handling with custom error types
- **🏗️ Repository Pattern**: Clean architecture with dependency injection

## 📋 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (for production) or SQLite (for development)
- Docker (optional)

### Local Development

1. **Clone and setup environment**:
```bash
git clone <repository-url>
cd clock-bucks
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

# 1. Install dependencies
pip install -r requirements.txt

# 2. Run migrations
alembic upgrade head

# 3. Start development server
make run
# OR: uvicorn src.main:app --reload

# 4. Run tests
make test

# 5. Format code
make format

# 6. Run all quality checks
make check
```

6. **Access the application**:
- API: http://127.0.0.1:8000
- Documentation: http://127.0.0.1:8000/docs
- Health Check: http://127.0.0.1:8000/health

### Quick Test Run

To quickly test the calculator logic with sample data:

```bash
python dev_test.py
```

This will run a comprehensive test of the meeting cost calculator with realistic sample data, showing:
- 📅 Sample meetings with different durations and participant counts
- 💰 Cost calculations for each meeting
- 📊 Individual participant cost breakdowns
- 📈 Overall statistics across all meetings
- ⏰ Real-time cost calculation example

**Example output:**
```
🕒 Clock Bucks - Meeting Cost Calculator Test
==================================================

📅 Meeting 1: Sprint Planning
⏱️  Duration: 90 minutes
👥 Participants: 4
💰 Total Cost: $487.50
💸 Cost per minute: $5.42

📊 Participant Breakdown:
  • Alice Johnson (Senior Product Manager): $142.50
  • Bob Smith (Senior Developer): $127.50
  • Carol Davis (UX Designer): $112.50
  • David Wilson (QA Engineer): $105.00
```

> 💡 **See [docs/DEV_TEST_README.md](docs/DEV_TEST_README.md) for detailed information about customizing and extending the development test script.**

## 🏗️ Project Structure

```
clock-bucks/
├── src/                          # Application source code
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                 # Configuration management
│   ├── database.py               # Database connection and session management
│   ├── exceptions.py             # Custom exception definitions
│   ├── logging_config.py         # Logging configuration
│   ├── models/                   # Pydantic models
│   │   ├── participant.py        # Participant schemas
│   │   ├── meeting.py           # Meeting schemas
│   │   └── db/                  # SQLAlchemy database models
│   │       ├── participant.py
│   │       └── meeting.py
│   ├── repositories/            # Data access layer
│   │   ├── base.py             # Base repository pattern
│   │   └── participant.py      # Participant repository
│   ├── routes/                 # API route handlers
│   │   ├── meetings.py         # Meeting endpoints
│   │   └── participants.py     # Participant endpoints
│   ├── services/               # Business logic layer
│   │   └── calculator.py       # Meeting cost calculation logic
│   └── middleware/             # Custom middleware
│       └── security.py         # Security and logging middleware
├── tests/                      # Test suite
│   ├── conftest.py            # Test configuration
│   └── test_api.py            # API tests
├── alembic/                   # Database migrations
├── k8s/                      # Kubernetes manifests
├── requirements.txt          # Python dependencies
├── Dockerfile               # Development Docker image
├── Dockerfile.prod         # Production Docker image
├── docker-compose.yml      # Development Docker Compose
├── docker-compose.prod.yml # Production Docker Compose
├── Makefile               # Development commands
├── pyproject.toml        # Python project configuration
└── README.md            # This file
```

## 🔧 Development Commands

Using Make (recommended):
```bash
make help              # Show all available commands
make dev-install       # Install development dependencies
make test              # Run tests with coverage
make lint              # Run code linting
make format            # Format code with black and isort
make run               # Start development server
make docker-run        # Run with Docker Compose
```

Manual commands:
```bash
# Quick functionality test
python dev_test.py     # Test calculator with sample data

# Testing
pytest tests/ -v --cov=src

# Code formatting
black src tests
isort src tests

# Linting
flake8 src tests
mypy src

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## 🐳 Docker Deployment

### Development
```bash
# Using Docker Compose
docker-compose up --build

# Manual Docker build
docker build -t clockbucks-api:latest .
docker run -p 8000:8000 clockbucks-api:latest
```

### Production
```bash
# Production Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Or with Make
make docker-run-prod
```

## ☸️ Kubernetes Deployment

### Quick Deploy
```bash
# Linux/Mac
./deploy-k8s.sh

# Windows
deploy-k8s.bat

# With Ingress
./deploy-k8s.sh --with-ingress
```

### Manual Deployment
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml  # Optional
```

## 📊 API Documentation

### Core Endpoints

#### Meetings
- `POST /api/v1/meetings/calculate` - Calculate meeting cost
- `POST /api/v1/meetings/real-time-cost` - Real-time cost tracking
- `GET /api/v1/meetings` - List all meetings
- `POST /api/v1/meetings` - Create new meeting
- `GET /api/v1/meetings/{id}` - Get meeting details
- `GET /api/v1/meetings/statistics/overview` - Cost statistics

#### Participants
- `GET /api/v1/participants` - List all participants
- `POST /api/v1/participants` - Create new participant
- `GET /api/v1/participants/{id}` - Get participant details
- `PUT /api/v1/participants/{id}` - Update participant
- `DELETE /api/v1/participants/{id}` - Delete participant

#### System
- `GET /health` - Health check
- `GET /metrics` - Application metrics
- `GET /docs` - Interactive API documentation

### Example API Usage

**Calculate Meeting Cost:**
```bash
curl -X POST "http://localhost:8000/api/v1/meetings/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sprint Planning",
    "duration_minutes": 90,
    "participants": [
      {
        "name": "Alice Johnson",
        "hourly_rate": 95.0,
        "role": "Product Manager"
      },
      {
        "name": "Bob Smith", 
        "hourly_rate": 85.0,
        "role": "Senior Developer"
      }
    ]
  }'
```

**Create Participant:**
```bash
curl -X POST "http://localhost:8000/api/v1/participants" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@company.com",
    "hourly_rate": 75.0,
    "role": "Developer",
    "department": "Engineering"
  }'
```

## 🔧 Configuration

### Environment Variables

**Development** (`.env`):
```bash
DEBUG=true
DATABASE_URL=sqlite:///./clockbucks.db
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
RATE_LIMIT_ENABLED=false
```

**Production** (`.env.production`):
```bash
DEBUG=false
DATABASE_URL=postgresql://user:password@postgres:5432/clockbucks
ALLOWED_ORIGINS=https://yourdomain.com
SECRET_KEY=your-super-secret-key
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
```

## 🧪 Testing

### Run Tests
```bash
# All tests with coverage
make test

# Quick test run
pytest tests/ -v

# Specific test file
pytest tests/test_api.py -v

# Test with coverage report
pytest tests/ --cov=src --cov-report=html
```

### Test Categories
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test API endpoints and database interactions
- **Validation Tests**: Test input validation and error handling

## 📈 Monitoring & Observability

### Health Checks
- **Health Endpoint**: `/health` - Basic service health
- **Kubernetes Probes**: Liveness, readiness, and startup probes configured

### Logging
- **Structured Logging**: JSON format with request IDs
- **Log Levels**: Configurable via `LOG_LEVEL` environment variable
- **Request Tracking**: Every request gets a unique ID
- **Error Tracking**: Comprehensive error logging with stack traces

### Metrics
- **Basic Metrics**: Available at `/metrics` endpoint
- **Prometheus Ready**: Easy integration with Prometheus/Grafana
- **Custom Metrics**: Extensible metrics collection

## 🔒 Security Features

- **Rate Limiting**: Configurable request rate limiting per IP
- **Security Headers**: OWASP recommended security headers
- **Input Validation**: Comprehensive Pydantic validation
- **SQL Injection Protection**: SQLAlchemy ORM protection
- **CORS Configuration**: Proper cross-origin resource sharing
- **Request ID Tracking**: All requests tracked with unique IDs

## 🚀 Production Deployment

### Cloud Platforms

**AWS EKS:**
```bash
eksctl create cluster --name clockbucks --region us-west-2
./deploy-k8s.sh --with-ingress
```

**Google GKE:**
```bash
gcloud container clusters create clockbucks --zone us-central1-a
./deploy-k8s.sh --with-ingress
```

**Azure AKS:**
```bash
az aks create --resource-group rg --name clockbucks
./deploy-k8s.sh --with-ingress
```

### Performance Considerations
- **Database Connection Pooling**: Configured for optimal performance
- **Async/Await**: Full async support for concurrent requests
- **Resource Limits**: Kubernetes resource limits configured
- **Horizontal Scaling**: HPA configured for auto-scaling

## 🛠️ Development Workflow

1. **Feature Development**:
   - Create feature branch
   - Write tests first (TDD)
   - Implement feature
   - Run quality checks: `make check`

2. **Database Changes**:
   - Create migration: `alembic revision --autogenerate -m "description"`
   - Review migration file
   - Apply migration: `alembic upgrade head`

3. **Code Quality**:
   - Format code: `make format`
   - Run linting: `make lint`
   - Run tests: `make test`

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite and quality checks
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Documentation

### Project Documentation
- **[Main README](README.md)** - This file, comprehensive project overview
- **[Deployment Guide](DEPLOYMENT.md)** - Detailed deployment instructions for all platforms
- **[Development Test Script](docs/DEV_TEST_README.md)** - Guide for using the development testing tool

### API Documentation
- **Interactive Docs**: Available at `/docs` when running the server
- **OpenAPI Schema**: Available at `/openapi.json`
- **Health Check**: Available at `/health`

### Code Documentation
- **Inline Comments**: Comprehensive code documentation
- **Type Hints**: Full type annotations throughout the codebase
- **Docstrings**: Detailed function and class documentation

## 🆘 Support

- **Documentation**: Check the `/docs` endpoint when running the API
- **Issues**: Report issues on the project's issue tracker
- **Health Checks**: Monitor the `/health` endpoint
- **Logs**: Check application logs for debugging information

## 🔮 Roadmap

- [ ] **Authentication & Authorization**: JWT-based user authentication
- [ ] **Team Management**: Multi-team support with role-based access
- [ ] **Calendar Integration**: Integration with Google Calendar, Outlook
- [ ] **Slack/Teams Integration**: Bot for meeting cost notifications
- [ ] **Advanced Analytics**: Machine learning insights and recommendations
- [ ] **Cost Budgets**: Meeting budget tracking and alerts
- [ ] **Multi-currency Support**: Support for different currencies
- [ ] **Webhook Support**: Real-time integrations with external systems
