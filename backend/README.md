# Todo Backend API

Production-ready FastAPI backend for Todo application with persistent PostgreSQL storage using Neon Serverless PostgreSQL.

## Features

- **RESTful API**: 6 endpoints for complete CRUD operations on tasks
- **Database Persistence**: SQLModel ORM with Neon Serverless PostgreSQL
- **Connection Pooling**: Optimized for serverless environments (pool size: 5)
- **Automatic Timestamps**: Auto-managed created_at and updated_at fields
- **Input Validation**: Pydantic-based request/response validation
- **API Documentation**: Auto-generated Swagger UI and ReDoc
- **Error Handling**: Comprehensive error responses with proper HTTP status codes
- **CORS Support**: Configured for frontend integration

## Technology Stack

- **Framework**: FastAPI (latest stable)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: Neon Serverless PostgreSQL
- **Server**: Uvicorn (ASGI)
- **Python**: 3.10+

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and environment variables
│   ├── models/              # SQLModel database models
│   │   ├── __init__.py
│   │   └── task.py          # Task model definition
│   ├── schemas/             # Pydantic request/response schemas
│   │   └── __init__.py
│   ├── routes/              # API route handlers
│   │   └── __init__.py
│   ├── database/            # Database connection and session management
│   │   ├── __init__.py
│   │   └── connection.py    # Database engine and session factory
│   └── services/            # Business logic layer
│       └── __init__.py
├── tests/
│   └── __init__.py
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- Neon PostgreSQL account and database
- pip or poetry for package management

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   cd backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and update the `DATABASE_URL` with your Neon PostgreSQL connection string:
   ```
   DATABASE_URL=postgresql://user:password@host.neon.tech:5432/dbname?sslmode=require
   ```

6. **Initialize the database**:
   The database tables will be created automatically on application startup.

### Running the Application

#### Development Mode (with auto-reload)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Using Python directly

```bash
python -m app.main
```

### Accessing the API

- **API Base URL**: http://localhost:8000
- **Swagger UI (Interactive Docs)**: http://localhost:8000/docs
- **ReDoc (Alternative Docs)**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Health Check
- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint

### Task Management (Coming in next phase)
- `POST /api/{user_id}/tasks` - Create a new task
- `GET /api/{user_id}/tasks` - List all tasks for a user
- `GET /api/{user_id}/tasks/{id}` - Get a specific task
- `PUT /api/{user_id}/tasks/{id}` - Update a task
- `DELETE /api/{user_id}/tasks/{id}` - Delete a task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle task completion

## Database Schema

### Task Table

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique identifier |
| title | String(200) | Required, min_length=1 | Task title |
| description | String(1000) | Optional, Nullable | Detailed description |
| completed | Boolean | Default=False | Completion status |
| created_at | DateTime | Auto-generated, UTC | Creation timestamp |
| updated_at | DateTime | Auto-updated, UTC | Last update timestamp |
| user_id | String(100) | Required, Indexed | User identifier |

### Indexes
- Primary key on `id`
- Index on `user_id` for efficient filtering
- Composite index on `(user_id, created_at)` for efficient listing

## Configuration

All configuration is managed through environment variables in the `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | (required) | PostgreSQL connection string |
| DATABASE_POOL_SIZE | 5 | Connection pool size |
| DATABASE_POOL_RECYCLE | 3600 | Connection recycle time (seconds) |
| DATABASE_ECHO | false | Log SQL statements |
| APP_NAME | Todo Backend API | Application name |
| APP_VERSION | 0.1.0 | Application version |
| DEBUG | false | Debug mode |
| HOST | 0.0.0.0 | Server host |
| PORT | 8000 | Server port |
| CORS_ORIGINS | localhost:3000 | Allowed CORS origins |

## Testing

Run tests with pytest:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=app --cov-report=html

# Run specific test file
pytest tests/test_tasks_api.py -v
```

## Development Workflow

1. **Make changes** to the code
2. **Run tests** to ensure nothing breaks
3. **Check code quality**:
   ```bash
   # Format code
   black app/

   # Check linting
   flake8 app/

   # Type checking
   mypy app/
   ```
4. **Commit changes** following the project's git workflow

## Database Migrations

Currently, the application uses SQLModel's `create_all()` method to create tables on startup. This is suitable for development but not recommended for production.

For production deployments, consider using Alembic for database migrations:
```bash
pip install alembic
alembic init migrations
```

## Troubleshooting

### Database Connection Issues

If you encounter database connection errors:

1. Verify your `DATABASE_URL` is correct in `.env`
2. Ensure your Neon database is active (not suspended)
3. Check that SSL mode is set to `require` in the connection string
4. Verify network connectivity to Neon servers

### Import Errors

If you get import errors:
```bash
# Ensure you're in the backend directory
cd backend

# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use

If port 8000 is already in use:
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

## Security Notes

- **Authentication**: Not implemented in this phase (Spec-1). Will be added in Spec-2.
- **SQL Injection**: Protected by SQLModel's parameterized queries
- **Input Validation**: All inputs validated by Pydantic models
- **CORS**: Configure `CORS_ORIGINS` appropriately for production

## Performance Considerations

- **Connection Pooling**: Configured with pool_size=5 for serverless environments
- **Connection Recycling**: Connections recycled every hour to prevent stale connections
- **Pre-ping**: Connections verified before use to handle Neon's auto-suspend feature
- **Response Time**: Target <500ms for single operations

## Next Steps (Spec-2)

- Implement Better Auth for user authentication
- Add JWT token verification to all endpoints
- Implement user isolation (filter tasks by authenticated user)
- Add user signup/signin endpoints
- Implement password hashing and validation

## License

This project is part of the Todo Full-Stack Web Application (Phase II).

## Support

For issues or questions, please refer to the project documentation in `specs/001-backend-core-data/`.
