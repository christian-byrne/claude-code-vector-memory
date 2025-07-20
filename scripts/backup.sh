#!/bin/bash
# Backup and restore utilities for the semantic memory system

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Functions
backup_database() {
    echo "📦 Creating database backup..."
    
    mkdir -p "$BACKUP_DIR"
    
    if [ -d "chroma_db" ]; then
        tar -czf "$BACKUP_DIR/chroma_db_$TIMESTAMP.tar.gz" chroma_db/
        echo "✅ Database backed up to: $BACKUP_DIR/chroma_db_$TIMESTAMP.tar.gz"
        
        # Keep only the 5 most recent backups
        ls -t "$BACKUP_DIR"/chroma_db_*.tar.gz | tail -n +6 | xargs -r rm
        echo "🧹 Cleaned up old backups (keeping 5 most recent)"
    else
        echo "⚠️  No database found to backup"
    fi
}

restore_database() {
    if [ -z "$1" ]; then
        echo "❌ Please specify backup file to restore"
        echo "Usage: ./scripts/backup.sh restore <backup_file>"
        echo "Available backups:"
        ls -la "$BACKUP_DIR"/chroma_db_*.tar.gz 2>/dev/null || echo "  No backups found"
        exit 1
    fi
    
    BACKUP_FILE="$1"
    
    if [ ! -f "$BACKUP_FILE" ]; then
        # Try looking in backups directory
        BACKUP_FILE="$BACKUP_DIR/$1"
        if [ ! -f "$BACKUP_FILE" ]; then
            echo "❌ Backup file not found: $1"
            exit 1
        fi
    fi
    
    echo "🔄 Restoring database from: $BACKUP_FILE"
    
    # Backup current database if it exists
    if [ -d "chroma_db" ]; then
        echo "📦 Backing up current database..."
        mv chroma_db "chroma_db_backup_$TIMESTAMP"
    fi
    
    # Restore from backup
    tar -xzf "$BACKUP_FILE"
    echo "✅ Database restored successfully"
    
    # Test the restored database
    echo "🧪 Testing restored database..."
    if python scripts/health_check.py > /dev/null 2>&1; then
        echo "✅ Database test passed"
    else
        echo "⚠️  Database test failed - you may need to rebuild"
    fi
}

list_backups() {
    echo "📋 Available backups:"
    if [ -d "$BACKUP_DIR" ]; then
        ls -lah "$BACKUP_DIR"/chroma_db_*.tar.gz 2>/dev/null || echo "  No backups found"
    else
        echo "  No backup directory found"
    fi
}

show_usage() {
    echo "Usage: ./scripts/backup.sh [command]"
    echo ""
    echo "Commands:"
    echo "  backup           Create a new database backup"
    echo "  restore <file>   Restore database from backup file"
    echo "  list             List available backups"
    echo "  help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./scripts/backup.sh backup"
    echo "  ./scripts/backup.sh restore chroma_db_20231201_143022.tar.gz"
    echo "  ./scripts/backup.sh list"
}

# Main script logic
case "${1:-backup}" in
    "backup")
        backup_database
        ;;
    "restore")
        restore_database "$2"
        ;;
    "list")
        list_backups
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        echo "❌ Unknown command: $1"
        show_usage
        exit 1
        ;;
esac