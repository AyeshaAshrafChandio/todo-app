#!/bin/bash
# Full-Stack Integration Verification Script

echo "=================================="
echo "Full-Stack Todo App Verification"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is running
echo "1. Checking Backend (Port 8000)..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${RED}✗ Backend is NOT running${NC}"
    echo "  Start with: cd backend && python -m uvicorn app.main:app --reload --port 8000"
fi
echo ""

# Check if frontend is running
echo "2. Checking Frontend (Port 3000)..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${RED}✗ Frontend is NOT running${NC}"
    echo "  Start with: cd frontend && npm run dev"
fi
echo ""

# Check backend configuration
echo "3. Checking Backend Configuration..."
cd backend
if python -c "from app.config import settings; print(f'Port: {settings.PORT}'); print(f'CORS: {settings.CORS_ORIGINS}')" 2>&1 | grep -q "Port: 8000"; then
    echo -e "${GREEN}✓ Backend configured correctly (Port 8000)${NC}"
else
    echo -e "${RED}✗ Backend configuration issue${NC}"
fi

if python -c "from app.config import settings; exit(0 if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != 'your-openai-api-key-here' else 1)" 2>/dev/null; then
    echo -e "${GREEN}✓ OpenAI API key configured${NC}"
else
    echo -e "${YELLOW}⚠ OpenAI API key NOT configured (AI chat will not work)${NC}"
    echo "  Add your key to backend/.env: OPENAI_API_KEY=sk-..."
fi
cd ..
echo ""

# Check frontend configuration
echo "4. Checking Frontend Configuration..."
if grep -q "NEXT_PUBLIC_API_URL=http://localhost:8000" frontend/.env.local; then
    echo -e "${GREEN}✓ Frontend API URL configured correctly${NC}"
else
    echo -e "${RED}✗ Frontend API URL misconfigured${NC}"
fi

BACKEND_SECRET=$(grep "BETTER_AUTH_SECRET=" backend/.env | cut -d'=' -f2)
FRONTEND_SECRET=$(grep "BETTER_AUTH_SECRET=" frontend/.env.local | cut -d'=' -f2)

if [ "$BACKEND_SECRET" = "$FRONTEND_SECRET" ]; then
    echo -e "${GREEN}✓ JWT secrets match${NC}"
else
    echo -e "${RED}✗ JWT secrets DO NOT match${NC}"
    echo "  Backend: $BACKEND_SECRET"
    echo "  Frontend: $FRONTEND_SECRET"
fi
echo ""

# Test API endpoints
echo "5. Testing API Endpoints..."
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo -e "${GREEN}✓ Health endpoint working${NC}"
else
    echo -e "${RED}✗ Health endpoint failed${NC}"
fi

if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API docs accessible at http://localhost:8000/docs${NC}"
else
    echo -e "${RED}✗ API docs not accessible${NC}"
fi
echo ""

# Summary
echo "=================================="
echo "Verification Summary"
echo "=================================="
echo ""
echo "Next Steps:"
echo "1. Start backend: cd backend && python -m uvicorn app.main:app --reload --port 8000"
echo "2. Start frontend: cd frontend && npm run dev"
echo "3. Open browser: http://localhost:3000"
echo "4. Register account and test chat interface"
echo ""
echo "For AI chat to work, configure OpenAI API key in backend/.env"
echo "Get key from: https://platform.openai.com/api-keys"
echo ""
