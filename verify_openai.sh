#!/bin/bash
# Quick verification script for OpenAI integration

echo "============================================================"
echo "OpenAI Integration Verification"
echo "============================================================"
echo ""

# Step 1: Check backend is running
echo "Step 1: Checking backend server..."
curl -s http://localhost:8001/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "[OK] Backend is running on port 8001"
else
    echo "[FAIL] Backend is not running. Start it with:"
    echo "  cd backend && uvicorn app.main:app --reload --port 8001"
    exit 1
fi

# Step 2: Check OpenAI configuration
echo ""
echo "Step 2: Checking OpenAI configuration..."
cd backend
python -c "
from app.config import settings
import sys

if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == 'your-openai-api-key-here':
    print('[FAIL] OPENAI_API_KEY not configured')
    sys.exit(1)

print(f'[OK] API Key configured (length: {len(settings.OPENAI_API_KEY)})')
print(f'[OK] Model: {settings.OPENAI_MODEL}')
print(f'[OK] Max Tokens: {settings.OPENAI_MAX_TOKENS}')
"

if [ $? -ne 0 ]; then
    exit 1
fi

# Step 3: Test chat endpoint
echo ""
echo "Step 3: Testing /api/chat endpoint..."
echo "Note: This requires a valid JWT token and sufficient API quota"
echo ""
echo "To test manually:"
echo "1. Login to get JWT token:"
echo "   curl -X POST http://localhost:8001/api/auth/signin \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"email\":\"test@example.com\",\"password\":\"TestPass123\"}'"
echo ""
echo "2. Send chat message:"
echo "   curl -X POST http://localhost:8001/api/chat \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -H 'Authorization: Bearer YOUR_JWT_TOKEN' \\"
echo "     -d '{\"conversation_id\":null,\"message\":\"List my tasks\"}'"

echo ""
echo "============================================================"
echo "Verification complete!"
echo "============================================================"
