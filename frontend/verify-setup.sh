#!/bin/bash

# Frontend Setup Verification Script
# This script verifies that the Next.js frontend is properly set up

echo "=========================================="
echo "Frontend Setup Verification"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check counter
CHECKS_PASSED=0
CHECKS_FAILED=0

# Function to check if file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}✗${NC} $2 (Missing: $1)"
        ((CHECKS_FAILED++))
    fi
}

# Function to check if directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}✗${NC} $2 (Missing: $1)"
        ((CHECKS_FAILED++))
    fi
}

echo "1. Checking Configuration Files..."
echo "-----------------------------------"
check_file "package.json" "package.json exists"
check_file "tsconfig.json" "TypeScript configuration exists"
check_file "next.config.js" "Next.js configuration exists"
check_file "tailwind.config.js" "Tailwind CSS configuration exists"
check_file "postcss.config.js" "PostCSS configuration exists"
check_file ".env.local.example" "Environment variables template exists"
check_file ".gitignore" "Git ignore file exists"
check_file ".eslintrc.json" "ESLint configuration exists"
echo ""

echo "2. Checking Directory Structure..."
echo "-----------------------------------"
check_dir "src" "src directory exists"
check_dir "src/app" "app directory exists"
check_dir "src/components" "components directory exists"
check_dir "src/lib" "lib directory exists"
check_dir "src/hooks" "hooks directory exists"
check_dir "public" "public directory exists"
echo ""

echo "3. Checking App Router Structure..."
echo "-----------------------------------"
check_dir "src/app/(auth)" "Auth route group exists"
check_dir "src/app/(protected)" "Protected route group exists"
check_file "src/app/layout.tsx" "Root layout exists"
check_file "src/app/page.tsx" "Home page exists"
check_file "src/app/globals.css" "Global styles exist"
echo ""

echo "4. Checking Authentication Pages..."
echo "-----------------------------------"
check_file "src/app/(auth)/login/page.tsx" "Login page exists"
check_file "src/app/(auth)/register/page.tsx" "Register page exists"
check_file "src/app/(auth)/loading.tsx" "Auth loading state exists"
echo ""

echo "5. Checking Protected Pages..."
echo "-----------------------------------"
check_file "src/app/(protected)/layout.tsx" "Protected layout exists"
check_file "src/app/(protected)/dashboard/page.tsx" "Dashboard page exists"
check_file "src/app/(protected)/tasks/page.tsx" "Tasks page exists"
check_file "src/app/(protected)/teams/page.tsx" "Teams page exists"
check_file "src/app/(protected)/error.tsx" "Error boundary exists"
echo ""

echo "6. Checking UI Components..."
echo "-----------------------------------"
check_file "src/components/ui/Button.tsx" "Button component exists"
check_file "src/components/ui/Input.tsx" "Input component exists"
check_file "src/components/ui/Card.tsx" "Card component exists"
check_file "src/components/ui/Badge.tsx" "Badge component exists"
check_file "src/components/ui/Spinner.tsx" "Spinner component exists"
check_file "src/components/ui/Alert.tsx" "Alert component exists"
echo ""

echo "7. Checking API Clients..."
echo "-----------------------------------"
check_file "src/lib/api/client.ts" "Base API client exists"
check_file "src/lib/api/auth.ts" "Auth API client exists"
check_file "src/lib/api/tasks.ts" "Tasks API client exists"
check_file "src/lib/api/teams.ts" "Teams API client exists"
echo ""

echo "8. Checking Type Definitions..."
echo "-----------------------------------"
check_file "src/lib/types/auth.ts" "Auth types exist"
check_file "src/lib/types/task.ts" "Task types exist"
check_file "src/lib/types/team.ts" "Team types exist"
echo ""

echo "9. Checking Custom Hooks..."
echo "-----------------------------------"
check_file "src/hooks/useAuth.ts" "useAuth hook exists"
check_file "src/hooks/useTasks.ts" "useTasks hook exists"
check_file "src/hooks/useTeams.ts" "useTeams hook exists"
echo ""

echo "10. Checking Documentation..."
echo "-----------------------------------"
check_file "README.md" "README exists"
check_file "QUICK_START.md" "Quick start guide exists"
check_file "DIRECTORY_TREE.txt" "Directory tree exists"
echo ""

echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo -e "${GREEN}Checks Passed: $CHECKS_PASSED${NC}"
echo -e "${RED}Checks Failed: $CHECKS_FAILED${NC}"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Frontend setup is complete.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Run 'npm install' to install dependencies"
    echo "2. Copy .env.local.example to .env.local and configure"
    echo "3. Run 'npm run dev' to start development server"
    echo "4. Open http://localhost:3000 in your browser"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please review the missing files/directories.${NC}"
    exit 1
fi
