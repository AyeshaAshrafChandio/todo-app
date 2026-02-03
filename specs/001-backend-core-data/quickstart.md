# Quickstart Guide: Todo Backend API

**Feature**: 001-backend-core-data
**Created**: 2026-01-20
**Status**: Development Guide

## Overview

This guide will help you set up and run the Todo Backend API locally. The backend is built with FastAPI, uses SQLModel for database operations, and connects to Neon Serverless PostgreSQL for data persistence.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** - Python package installer (included with Python)
- **Git** - Version control system
- **Neon PostgreSQL Account** - [Sign up at Neon](https://neon.tech/)

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd <repository-name>
```

## Step 2: Set Up Python Virtual Environment

Create and activate a virtual environment to isolate project dependencies:

### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt, indicating the virtual environment is active.

## Step 3: Install Dependencies

Install all required Python packages:

```bash
cd backend
pip install -r requirements.txt
```

**Expected dependencies:**
- `fastapi` - Web framework
- `sqlmodel` - ORM for database operations
- `uvicorn[standard]` - ASGI server
- `python-dotenv` - Environment variable management
- `psycopg2-binary` - PostgreSQL adapter
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `httpx` - HTTP client for testing

## Step 4: Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
cp .env.example .env
```

Edit the `.env` file with your Neon PostgreSQL credentials:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@host.neon.tech:5432/dbname?sslmode=require
DATABASE_POOL_SIZE=5
DATABASE_POOL_RECYCLE=3600
DATABASE_ECHO=false

# Application Configuration
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
```

### Getting Your Neon Database URL

1. Log in to your [Neon Console](https://console.neon.tech/)
2. Create a new project or select an existing one
3. Navigate to the "Connection Details" section
4. Copy the connection string (it should look like: `postgresql://user:pass@host.neon.tech:5432/dbname`)
5. Paste it into your `.env` file as the `DATABASE_URL` value

**Important**: Ensure `?sslmode=require` is appended to the connection string for secure connections.

## Step 5: Initialize the Database

Create the database tables by running the initialization script:

```bash
python -m app.database.init_db
```

This will:
- Connect to your Neon PostgreSQL database
- Create the `tasks` table with all required fields and indexes
- Set up database triggers for automatic timestamp management

**Expected output:**
```
Connecting to database...
Creating tables...
✓ Table 'tasks' created successfully
✓ Indexes created
✓ Triggers configured
Database initialization complete!
```

## Step 6: Start the Development Server

Run the FastAPI application using Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Command breakdown:**
- `app.main:app` - Module path to the FastAPI application instance
- `--reload` - Auto-reload on code changes (development only)
- `--host 0.0.0.0` - Listen on all network interfaces
- `--port 8000` - Run on port 8000

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Step 7: Verify the API is Running

Open your browser and navigate to:

### Interactive API Documentation (Swagger UI)
```
http://localhost:8000/docs
```

This provides an interactive interface to test all API endpoints.

### Alternative API Documentation (ReDoc)
```
http://localhost:8000/redoc
```

This provides a clean, readable API reference.

### Health Check Endpoint
```
http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

## Step 8: Test the API

### Using the Interactive Docs (Recommended for Beginners)

1. Go to `http://localhost:8000/docs`
2. Click on any endpoint (e.g., "POST /api/{user_id}/tasks")
3. Click "Try it out"
4. Fill in the parameters and request body
5. Click "Execute"
6. View the response

### Using cURL (Command Line)

**Create a task:**
```bash
curl -X POST "http://localhost:8000/api/user123/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'
```

**List all tasks:**
```bash
curl -X GET "http://localhost:8000/api/user123/tasks"
```

**Get a specific task:**
```bash
curl -X GET "http://localhost:8000/api/user123/tasks/1"
```

**Update a task:**
```bash
curl -X PUT "http://localhost:8000/api/user123/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries and supplies",
    "description": "Milk, eggs, bread, cheese",
    "completed": false
  }'
```

**Toggle task completion:**
```bash
curl -X PATCH "http://localhost:8000/api/user123/tasks/1/complete"
```

**Delete a task:**
```bash
curl -X DELETE "http://localhost:8000/api/user123/tasks/1"
```

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"
USER_ID = "user123"

# Create a task
response = requests.post(
    f"{BASE_URL}/api/{USER_ID}/tasks",
    json={
        "title": "Buy groceries",
        "description": "Milk, eggs, bread"
    }
)
print(f"Created task: {response.json()}")

# List all tasks
response = requests.get(f"{BASE_URL}/api/{USER_ID}/tasks")
print(f"All tasks: {response.json()}")
```

## Step 9: Run Tests

Execute the test suite to verify everything is working correctly:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=app --cov-report=html

# Run specific test file
pytest tests/test_tasks_api.py -v
```

**Expected output:**
```
tests/test_tasks_api.py::test_create_task PASSED
tests/test_tasks_api.py::test_list_tasks PASSED
tests/test_tasks_api.py::test_get_task PASSED
tests/test_tasks_api.py::test_update_task PASSED
tests/test_tasks_api.py::test_delete_task PASSED
tests/test_tasks_api.py::test_toggle_completion PASSED
tests/test_tasks_api.py::test_task_not_found PASSED
tests/test_tasks_api.py::test_invalid_task_data PASSED

======================== 8 passed in 2.34s ========================
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── models/              # SQLModel database models
│   │   ├── __init__.py
│   │   └── task.py          # Task model
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   └── task.py          # Task schemas
│   ├── routes/              # API route handlers
│   │   ├── __init__.py
│   │   └── tasks.py         # Task endpoints
│   ├── services/            # Business logic layer
│   │   ├── __init__.py
│   │   └── task_service.py  # Task operations
│   └── database/            # Database connection
│       ├── __init__.py
│       ├── connection.py    # Engine and session
│       └── init_db.py       # Database initialization
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── test_tasks_api.py    # API endpoint tests
│   └── test_task_service.py # Service layer tests
├── .env                     # Environment variables (not in git)
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

## Common Issues and Solutions

### Issue: "ModuleNotFoundError: No module named 'app'"

**Solution**: Ensure you're in the `backend/` directory and the virtual environment is activated.

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### Issue: "Connection refused" or "Database connection failed"

**Solution**: Verify your `DATABASE_URL` in `.env` is correct and your Neon database is accessible.

1. Check the connection string format
2. Ensure `?sslmode=require` is appended
3. Verify your Neon project is active
4. Test the connection using `psql` or a database client

### Issue: "Port 8000 is already in use"

**Solution**: Either stop the process using port 8000 or use a different port:

```bash
uvicorn app.main:app --reload --port 8001
```

### Issue: Tests failing with "Table 'tasks' does not exist"

**Solution**: Run the database initialization script:

```bash
python -m app.database.init_db
```

### Issue: "SSL connection required"

**Solution**: Ensure your `DATABASE_URL` includes `?sslmode=require`:

```
postgresql://user:pass@host.neon.tech:5432/dbname?sslmode=require
```

## Development Workflow

### Making Changes

1. **Modify code** in the `app/` directory
2. **Save the file** - Uvicorn will auto-reload (if `--reload` flag is used)
3. **Test your changes** using the interactive docs or cURL
4. **Run tests** to ensure nothing broke: `pytest tests/ -v`

### Adding New Endpoints

1. Define the route in `app/routes/tasks.py`
2. Add business logic in `app/services/task_service.py`
3. Create request/response schemas in `app/schemas/task.py` if needed
4. Write tests in `tests/test_tasks_api.py`
5. Update the OpenAPI documentation (auto-generated by FastAPI)

### Database Changes

1. Modify the model in `app/models/task.py`
2. Create a migration script (manual for now, Alembic in future)
3. Run the migration against your database
4. Update tests to reflect schema changes

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/{user_id}/tasks` | List all tasks for a user |
| POST | `/api/{user_id}/tasks` | Create a new task |
| GET | `/api/{user_id}/tasks/{id}` | Get a specific task |
| PUT | `/api/{user_id}/tasks/{id}` | Update a task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete a task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle task completion |

## Next Steps

- **Explore the API**: Use the interactive docs at `/docs` to test all endpoints
- **Read the specification**: Review `specs/001-backend-core-data/spec.md` for detailed requirements
- **Review the plan**: Check `specs/001-backend-core-data/plan.md` for architectural decisions
- **Run the test suite**: Ensure all tests pass with `pytest tests/ -v`
- **Prepare for Spec-2**: The next phase will add authentication and user isolation

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Neon Documentation](https://neon.tech/docs/introduction)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Pytest Documentation](https://docs.pytest.org/)

## Support

If you encounter issues not covered in this guide:

1. Check the [project specification](./spec.md) for requirements
2. Review the [implementation plan](./plan.md) for architectural details
3. Examine the [data model documentation](./data-model.md) for schema details
4. Consult the [OpenAPI specification](./contracts/openapi.yaml) for API contracts

---

**Status**: ✅ Ready for Development - Follow this guide to set up your local environment
