#!/bin/bash
# Migration Execution Guide for Phase 3: Teams, RBAC, and Task Sharing
# Run this after verifying all Phase 1 & 2 tasks are complete

echo "=========================================="
echo "Phase 3 Migration Execution Guide"
echo "=========================================="
echo ""

# Step 1: Verify environment variables
echo "Step 1: Verify environment variables"
echo "-------------------------------------"
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL is not set"
    echo "   Set it with: export DATABASE_URL='your-neon-connection-string'"
    exit 1
else
    echo "✅ DATABASE_URL is set"
fi

if [ -z "$BETTER_AUTH_SECRET" ]; then
    echo "⚠️  WARNING: BETTER_AUTH_SECRET is not set"
    echo "   Migration will use temporary secret"
else
    echo "✅ BETTER_AUTH_SECRET is set"
fi

echo ""

# Step 2: Test on Neon branch (RECOMMENDED)
echo "Step 2: Test on Neon branch (RECOMMENDED)"
echo "------------------------------------------"
echo "Before running on production:"
echo "1. Create a Neon branch: neon branches create --name migration-test"
echo "2. Get branch connection string"
echo "3. Set DATABASE_URL to branch connection string"
echo "4. Run migration on branch first"
echo "5. Verify schema changes"
echo "6. Test rollback if needed"
echo ""
read -p "Have you tested on a Neon branch? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "⚠️  Please test on a Neon branch first!"
    exit 1
fi

echo ""

# Step 3: Backup check
echo "Step 3: Backup verification"
echo "----------------------------"
echo "Neon automatically backs up your data, but verify:"
echo "1. You can create a branch from current state"
echo "2. You have the rollback script ready"
echo ""
read -p "Ready to proceed? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Migration cancelled"
    exit 1
fi

echo ""

# Step 4: Run migration
echo "Step 4: Running migration"
echo "-------------------------"
cd "$(dirname "$0")/.."
python backend/migrations/003_add_teams_rbac_sharing.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Migration completed successfully!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Verify tables created: teams, team_members, task_shares"
    echo "2. Verify tasks.team_id column added"
    echo "3. Test existing functionality (personal tasks)"
    echo "4. Begin User Story implementation"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ Migration failed!"
    echo "=========================================="
    echo ""
    echo "Troubleshooting:"
    echo "1. Check DATABASE_URL is correct"
    echo "2. Verify Phase 2 migration is complete"
    echo "3. Check database connection"
    echo "4. Review error messages above"
    echo ""
    exit 1
fi
