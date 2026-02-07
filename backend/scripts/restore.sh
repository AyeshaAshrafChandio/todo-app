#!/bin/bash
#
# Database Restore Script for Neon Serverless PostgreSQL
#
# This script restores a database backup created by backup.sh
#
# Usage:
#   ./restore.sh backup_20260207_120000.sql.gz
#   ./restore.sh --file backup_20260207_120000.sql.gz
#
# Requirements:
#   - psql (PostgreSQL client tools)
#   - DATABASE_URL environment variable set
#   - Backup file created by backup.sh

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_ROOT/backups}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse command line arguments
BACKUP_FILE=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --file)
            BACKUP_FILE="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [--file BACKUP_FILE] or $0 BACKUP_FILE"
            echo ""
            echo "Options:"
            echo "  --file FILE    Specify backup file to restore"
            echo "  --help         Show this help message"
            echo ""
            echo "Example:"
            echo "  $0 backup_20260207_120000.sql.gz"
            exit 0
            ;;
        *)
            if [ -z "$BACKUP_FILE" ]; then
                BACKUP_FILE="$1"
                shift
            else
                log_error "Unknown option: $1"
                exit 1
            fi
            ;;
    esac
done

# Check if backup file is specified
if [ -z "$BACKUP_FILE" ]; then
    log_error "No backup file specified"
    echo ""
    echo "Usage: $0 BACKUP_FILE"
    echo ""
    echo "Available backups:"
    ls -lh "$BACKUP_DIR"/backup_*.sql.gz 2>/dev/null || echo "  No backups found"
    exit 1
fi

# Check if backup file exists (try both absolute and relative to backup dir)
if [ ! -f "$BACKUP_FILE" ]; then
    if [ -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
        BACKUP_FILE="$BACKUP_DIR/$BACKUP_FILE"
    else
        log_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi
fi

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    log_info "Loading environment variables from .env"
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
else
    log_warn ".env file not found, using system environment variables"
fi

# Check if DATABASE_URL is set
if [ -z "${DATABASE_URL:-}" ]; then
    log_error "DATABASE_URL environment variable is not set"
    log_error "Please set DATABASE_URL in .env file or environment"
    exit 1
fi

# Confirm restore operation
log_warn "WARNING: This will restore the database from backup"
log_warn "All current data will be replaced with backup data"
log_warn "Backup file: $BACKUP_FILE"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    log_info "Restore cancelled"
    exit 0
fi

# Create a safety backup before restore
log_info "Creating safety backup of current database..."
SAFETY_BACKUP="$BACKUP_DIR/pre_restore_backup_$(date +"%Y%m%d_%H%M%S").sql"
if pg_dump "$DATABASE_URL" \
    --no-owner \
    --no-acl \
    --clean \
    --if-exists \
    --format=plain \
    > "$SAFETY_BACKUP"; then

    gzip "$SAFETY_BACKUP"
    log_info "Safety backup created: ${SAFETY_BACKUP}.gz"
else
    log_error "Failed to create safety backup"
    exit 1
fi

# Decompress backup if needed
TEMP_FILE=""
if [[ "$BACKUP_FILE" == *.gz ]]; then
    log_info "Decompressing backup..."
    TEMP_FILE="/tmp/restore_$(date +%s).sql"
    gunzip -c "$BACKUP_FILE" > "$TEMP_FILE"
    RESTORE_FILE="$TEMP_FILE"
else
    RESTORE_FILE="$BACKUP_FILE"
fi

# Restore database
log_info "Starting database restore..."
log_info "This may take a few minutes..."

if psql "$DATABASE_URL" < "$RESTORE_FILE"; then
    log_info "Database restored successfully"
else
    log_error "Restore failed"
    log_error "Your database may be in an inconsistent state"
    log_error "You can restore from safety backup: ${SAFETY_BACKUP}.gz"

    # Cleanup temp file
    [ -n "$TEMP_FILE" ] && rm -f "$TEMP_FILE"
    exit 1
fi

# Cleanup temp file
[ -n "$TEMP_FILE" ] && rm -f "$TEMP_FILE"

# Verify restore
log_info "Verifying restore..."
TABLE_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
log_info "Tables in database: $TABLE_COUNT"

log_info "Restore completed successfully"
log_info ""
log_info "Safety backup location: ${SAFETY_BACKUP}.gz"
log_info "You can delete the safety backup if everything looks good"

exit 0
