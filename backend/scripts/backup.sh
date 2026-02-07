#!/bin/bash
#
# Database Backup Script for Neon Serverless PostgreSQL
#
# This script creates a backup of all database tables and stores them
# with timestamp-based naming for easy restoration.
#
# Usage:
#   ./backup.sh                    # Create backup with default settings
#   ./backup.sh --output-dir /path # Specify custom output directory
#
# Requirements:
#   - pg_dump (PostgreSQL client tools)
#   - DATABASE_URL environment variable set
#   - Write permissions to backup directory

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_ROOT/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="backup_${TIMESTAMP}.sql"

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
while [[ $# -gt 0 ]]; do
    case $1 in
        --output-dir)
            BACKUP_DIR="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [--output-dir DIR]"
            echo ""
            echo "Options:"
            echo "  --output-dir DIR    Specify backup output directory (default: $BACKUP_DIR)"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

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

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"
log_info "Backup directory: $BACKUP_DIR"

# Create backup
log_info "Starting database backup..."
log_info "Backup file: $BACKUP_FILE"

# Use pg_dump to create backup
# Options:
#   --no-owner: Don't include ownership commands
#   --no-acl: Don't include access privileges
#   --clean: Include DROP commands before CREATE
#   --if-exists: Use IF EXISTS with DROP commands
#   --format=plain: Plain SQL format (human-readable)
if pg_dump "$DATABASE_URL" \
    --no-owner \
    --no-acl \
    --clean \
    --if-exists \
    --format=plain \
    > "$BACKUP_DIR/$BACKUP_FILE"; then

    log_info "Backup completed successfully"

    # Compress backup
    log_info "Compressing backup..."
    gzip "$BACKUP_DIR/$BACKUP_FILE"
    BACKUP_FILE="${BACKUP_FILE}.gz"

    # Get backup size
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
    log_info "Backup size: $BACKUP_SIZE"
    log_info "Backup location: $BACKUP_DIR/$BACKUP_FILE"
else
    log_error "Backup failed"
    exit 1
fi

# Cleanup old backups (keep last N days)
log_info "Cleaning up old backups (keeping last $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
OLD_BACKUP_COUNT=$(find "$BACKUP_DIR" -name "backup_*.sql.gz" -type f | wc -l)
log_info "Remaining backups: $OLD_BACKUP_COUNT"

# Create backup manifest
MANIFEST_FILE="$BACKUP_DIR/backup_manifest.txt"
echo "Backup created: $(date)" >> "$MANIFEST_FILE"
echo "File: $BACKUP_FILE" >> "$MANIFEST_FILE"
echo "Size: $BACKUP_SIZE" >> "$MANIFEST_FILE"
echo "---" >> "$MANIFEST_FILE"

log_info "Backup process completed successfully"
log_info ""
log_info "To restore this backup, run:"
log_info "  ./restore.sh $BACKUP_FILE"

exit 0
