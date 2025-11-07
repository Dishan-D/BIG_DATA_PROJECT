#!/usr/bin/env python3
"""
Clear all data from the database while keeping the schema intact
"""

import sqlite3
import os

DB_PATH = "image_processing.db"

def clear_database():
    """Clear all data from all tables."""
    if not os.path.exists(DB_PATH):
        print(f"⚠️ Database file '{DB_PATH}' does not exist!")
        print("Run 'python database.py' to create it.")
        return
    
    print(f"🗑️ Clearing database: {DB_PATH}")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get counts before deletion
        cursor.execute("SELECT COUNT(*) FROM jobs")
        jobs_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tiles")
        tiles_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM workers")
        workers_count = cursor.fetchone()[0]
        
        print(f"\n📊 Current data:")
        print(f"   Jobs: {jobs_count}")
        print(f"   Tiles: {tiles_count}")
        print(f"   Workers: {workers_count}")
        
        if jobs_count == 0 and tiles_count == 0 and workers_count == 0:
            print("\n✅ Database is already empty!")
            conn.close()
            return
        
        # Delete all data
        print("\n🔄 Clearing data...")
        cursor.execute("DELETE FROM tiles")
        cursor.execute("DELETE FROM jobs")
        cursor.execute("DELETE FROM workers")
        
        # Reset auto-increment counters (SQLite)
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='jobs'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='tiles'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='workers'")
        
        conn.commit()
        
        # Verify deletion
        cursor.execute("SELECT COUNT(*) FROM jobs")
        jobs_after = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tiles")
        tiles_after = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM workers")
        workers_after = cursor.fetchone()[0]
        
        print(f"\n✅ Database cleared successfully!")
        print(f"   Jobs: {jobs_after}")
        print(f"   Tiles: {tiles_after}")
        print(f"   Workers: {workers_after}")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error clearing database: {e}")
        import traceback
        traceback.print_exc()


def reset_database():
    """Delete database file and recreate schema."""
    print(f"🔄 Resetting database: {DB_PATH}")
    
    if os.path.exists(DB_PATH):
        print(f"🗑️ Deleting existing database...")
        os.remove(DB_PATH)
        print("✓ Deleted")
    
    print(f"📝 Creating fresh database...")
    from database import init_db
    init_db()
    print("✅ Database reset complete!")


def view_database():
    """View current database contents."""
    if not os.path.exists(DB_PATH):
        print(f"⚠️ Database file '{DB_PATH}' does not exist!")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("\n" + "="*60)
        print("📊 JOBS")
        print("="*60)
        cursor.execute("""
            SELECT job_id, filename, status, processed_tiles, total_tiles, created_at 
            FROM jobs 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        jobs = cursor.fetchall()
        
        if jobs:
            for job in jobs:
                print(f"Job: {job[0][:20]}... | {job[1]} | {job[2]} | {job[3]}/{job[4]} tiles | {job[5]}")
        else:
            print("No jobs found")
        
        print("\n" + "="*60)
        print("👷 WORKERS")
        print("="*60)
        cursor.execute("""
            SELECT worker_id, status, total_tasks_processed, last_heartbeat 
            FROM workers 
            ORDER BY last_heartbeat DESC
        """)
        workers = cursor.fetchall()
        
        if workers:
            for worker in workers:
                print(f"Worker: {worker[0]} | {worker[1]} | Tasks: {worker[2]} | Last: {worker[3]}")
        else:
            print("No workers found")
        
        print("\n" + "="*60)
        print("📊 STATISTICS")
        print("="*60)
        
        cursor.execute("SELECT COUNT(*) FROM jobs")
        total_jobs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE status='completed'")
        completed_jobs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE status='processing'")
        processing_jobs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tiles")
        total_tiles = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM workers")
        total_workers = cursor.fetchone()[0]
        
        print(f"Total Jobs: {total_jobs}")
        print(f"Completed: {completed_jobs}")
        print(f"Processing: {processing_jobs}")
        print(f"Total Tiles: {total_tiles}")
        print(f"Total Workers: {total_workers}")
        print("="*60 + "\n")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error viewing database: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("\n" + "="*60)
        print("DATABASE MANAGEMENT TOOL")
        print("="*60)
        print("\nUsage:")
        print("  python clear_database.py view      # View database contents")
        print("  python clear_database.py clear     # Clear all data (keep schema)")
        print("  python clear_database.py reset     # Delete and recreate database")
        print("\nExamples:")
        print("  python clear_database.py view")
        print("  python clear_database.py clear")
        print("  python clear_database.py reset")
        print("="*60 + "\n")
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == "view":
        view_database()
    elif command == "clear":
        clear_database()
    elif command == "reset":
        reset_database()
    else:
        print(f"❌ Unknown command: {command}")
        print("Valid commands: view, clear, reset")
        sys.exit(1)
