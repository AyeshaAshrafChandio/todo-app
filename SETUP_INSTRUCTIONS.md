# Full-Stack Todo Application - Setup Instructions

## Overview
This is a multi-user Todo application with AI-powered task management through natural language chat.

**Tech Stack:**
- Frontend: Next.js 16+ (App Router), TypeScript, Tailwind CSS
- Backend: FastAPI (Python), SQLModel ORM
- Database: Neon Serverless PostgreSQL (or SQLite for development)
- Authentication: Better Auth with JWT tokens
- AI: OpenAI GPT-4 for natural language task management

---

## Prerequisites

1. **Node.js** (v18 or higher)
2. **Python** (v3.9 or higher)
3. **OpenAI API Key** (required for AI chat features)
   - Get one from: https://platform.openai.com/api-keys
   - Free tier available for testing

---

## Backend Setup

### 1. Navigate to backend directory
```bash
cd backend
```

### 2. Create Python virtual environment
```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Edit `backend/.env` and set:

```env
# REQUIRED: JWT Secret (already configured)
BETTER_AUTH_SECRET=j-cgloynfj_XyhfeROGyecnUbArVlx4RtpoafbXfkz8

# REQUIRED: OpenAI API Key (replace with your actual key)
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Database (SQLite for development, Neon for production)
DATABASE_URL=sqlite:///./todo_dev.db

# Optional: OpenAI Model Configuration
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=4096
```

**IMPORTANT:** Replace `your-openai-api-key-here` with your actual OpenAI API key from https://platform.openai.com/api-keys

### 5. Start backend server
```bash
# From backend directory
python -m uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

---

## Frontend Setup

### 1. Navigate to frontend directory
```bash
cd frontend
```

### 2. Install dependencies
```bash
npm install
```

### 3. Configure environment variables
The `.env.local` file is already configured:

```env
# API Configuration (points to backend)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration (must match backend)
BETTER_AUTH_SECRET=j-cgloynfj_XyhfeROGyecnUbArVlx4RtpoafbXfkz8
BETTER_AUTH_URL=http://localhost:3000
```

### 4. Start frontend development server
```bash
npm run dev
```

Frontend will be available at: http://localhost:3000

---

## Testing the Application

### 1. Register a new account
1. Navigate to http://localhost:3000
2. Click "Register" or go to http://localhost:3000/register
3. Enter email and password
4. You'll be automatically logged in and redirected to the chat interface

### 2. Test AI Chat
1. After logging in, you'll see the chat interface at http://localhost:3000/chat
2. Try these commands:
   - "Add buy groceries to my list"
   - "Show me all my tasks"
   - "Mark buy groceries as complete"
   - "Delete the groceries task"

### 3. Verify Authentication
1. Open browser DevTools → Application → Local Storage
2. You should see a JWT token stored
3. Try logging out and logging back in

---

## Troubleshooting

### Backend Issues

**Error: "OPENAI_API_KEY is not configured"**
- Solution: Add your OpenAI API key to `backend/.env`
- Get key from: https://platform.openai.com/api-keys

**Error: "BETTER_AUTH_SECRET environment variable is required"**
- Solution: The secret is already configured in `.env`
- If missing, generate one: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

**Error: Database connection failed**
- Solution: For development, SQLite is used automatically
- For production, configure Neon PostgreSQL connection string

**Port 8000 already in use**
- Solution: Kill the process using port 8000 or change PORT in `.env`

### Frontend Issues

**Error: "Failed to fetch" or network errors**
- Solution: Ensure backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local` is set to `http://localhost:8000`

**Error: "Unauthorized" or "Invalid token"**
- Solution: JWT secrets must match between frontend and backend
- Check `BETTER_AUTH_SECRET` is identical in both `.env` files

**Chat not working / AI not responding**
- Solution: Ensure OpenAI API key is configured in backend `.env`
- Check backend logs for errors

---

## Architecture Overview

### Authentication Flow
1. User registers/logs in via frontend
2. Backend validates credentials and generates JWT token
3. Frontend stores token in localStorage
4. All API requests include token in `Authorization: Bearer <token>` header
5. Backend verifies token on every request

### Chat Flow
1. User sends message via chat interface
2. Frontend sends POST request to `/api/chat` with JWT token
3. Backend verifies token and extracts user ID
4. Backend forwards message to OpenAI Agent
5. Agent uses MCP tools to perform task operations (create, list, update, delete)
6. Agent generates natural language response
7. Backend returns response to frontend
8. Frontend displays AI response in chat

### Security
- JWT tokens signed with shared secret (BETTER_AUTH_SECRET)
- Passwords hashed with bcrypt (cost factor 12)
- User isolation enforced on all task operations
- CORS configured for frontend origin only

---

## Production Deployment

### Backend (Neon + Vercel/Railway)
1. Create Neon PostgreSQL database
2. Update `DATABASE_URL` in production environment
3. Set `OPENAI_API_KEY` in production environment
4. Deploy to Vercel, Railway, or similar platform

### Frontend (Vercel)
1. Update `NEXT_PUBLIC_API_URL` to production backend URL
2. Deploy to Vercel
3. Configure environment variables in Vercel dashboard

---

## API Documentation

Once backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

---

## Support

For issues or questions:
1. Check backend logs for errors
2. Check browser console for frontend errors
3. Verify environment variables are configured correctly
4. Ensure both backend and frontend are running

---

## License

This project is part of a hackathon submission.
