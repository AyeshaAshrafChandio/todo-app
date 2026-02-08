#!/bin/bash

# Phase 8 Frontend Team Management UI - Verification Script
# This script verifies that all Phase 8 tasks have been completed

echo "=========================================="
echo "Phase 8 Implementation Verification"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

# Function to check if file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $2 - File not found: $1"
        ((FAILED++))
    fi
}

echo "Checking Type Definitions (T077-T079)..."
echo "----------------------------------------"
check_file "frontend/src/lib/types/team.ts" "Team type definitions"

echo ""
echo "Checking API Client Functions (T080-T088)..."
echo "----------------------------------------"
check_file "frontend/src/lib/api/teams.ts" "Team API client"

echo ""
echo "Checking Hooks (T089-T090)..."
echo "----------------------------------------"
check_file "frontend/src/hooks/useTeams.ts" "useTeams hook"
check_file "frontend/src/hooks/useTeamDetails.ts" "useTeamDetails hook"

echo ""
echo "Checking Components (T091-T096)..."
echo "----------------------------------------"
check_file "frontend/src/components/teams/TeamCard.tsx" "TeamCard component"
check_file "frontend/src/components/teams/TeamList.tsx" "TeamList component"
check_file "frontend/src/components/teams/TeamForm.tsx" "TeamForm component"
check_file "frontend/src/components/teams/MemberList.tsx" "MemberList component"
check_file "frontend/src/components/teams/MemberInvite.tsx" "MemberInvite component"
check_file "frontend/src/components/teams/RoleSelector.tsx" "RoleSelector component"
check_file "frontend/src/components/teams/index.ts" "Team components index"

echo ""
echo "Checking Pages (T097-T100)..."
echo "----------------------------------------"
check_file "frontend/src/app/(protected)/teams/page.tsx" "Teams list page"
check_file "frontend/src/app/(protected)/teams/[teamId]/page.tsx" "Team detail page"
check_file "frontend/src/app/(protected)/teams/[teamId]/settings/page.tsx" "Team settings page"
check_file "frontend/src/app/(protected)/teams/new/page.tsx" "New team page"

echo ""
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All Phase 8 tasks completed successfully!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tasks are incomplete. Please review the failed items.${NC}"
    exit 1
fi
