# database.py
import sqlite3
import json
from datetime import datetime
import threading

# Thread-local storage for database connections
thread_local = threading.local()

DB_PATH = "image_processing.db"


def get_db():
    """Get thread-local database connection."""
    if not hasattr(thread_local, "connection"):
        thread_local.connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        thread_local.connection.row_factory = sqlite3.Row
    return thread_local.connection


def init_db():
    """Initialize database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Jobs table - tracks each image processing job
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            original_path TEXT,
            processed_path TEXT,
            total_tiles INTEGER NOT NULL,
            processed_tiles INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            image_width INTEGER,
            image_height INTEGER
        )
    ''')
    
    # Tiles table - tracks individual tile processing
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tiles (
            tile_id TEXT PRIMARY KEY,
            job_id TEXT NOT NULL,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            processed_at TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs(job_id)
        )
    ''')
    
    # Workers table - tracks worker heartbeats and status
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workers (
            worker_id TEXT PRIMARY KEY,
            last_heartbeat TIMESTAMP,
            status TEXT DEFAULT 'active',
            total_tasks_processed INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")


# ==================== JOB MANAGEMENT ====================

def create_job(job_id, filename, total_tiles, image_width, image_height):
    """Create a new processing job."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO jobs (job_id, filename, total_tiles, image_width, image_height, status)
        VALUES (?, ?, ?, ?, ?, 'processing')
    ''', (job_id, filename, total_tiles, image_width, image_height))
    conn.commit()


def update_job_status(job_id, status, processed_path=None):
    """Update job status and optionally set processed path."""
    conn = get_db()
    cursor = conn.cursor()
    if processed_path:
        cursor.execute('''
            UPDATE jobs 
            SET status = ?, processed_path = ?, completed_at = CURRENT_TIMESTAMP
            WHERE job_id = ?
        ''', (status, processed_path, job_id))
    else:
        cursor.execute('''
            UPDATE jobs SET status = ? WHERE job_id = ?
        ''', (status, job_id))
    conn.commit()


def increment_processed_tiles(job_id):
    """Increment the count of processed tiles for a job."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE jobs 
        SET processed_tiles = processed_tiles + 1 
        WHERE job_id = ?
    ''', (job_id,))
    conn.commit()


def get_job(job_id):
    """Get job details by ID."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs WHERE job_id = ?', (job_id,))
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None


def get_all_jobs():
    """Get all jobs ordered by creation time."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs ORDER BY created_at DESC')
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def get_job_progress(job_id):
    """Get processing progress for a job."""
    job = get_job(job_id)
    if not job:
        return None
    
    return {
        "job_id": job_id,
        "filename": job["filename"],
        "total_tiles": job["total_tiles"],
        "processed_tiles": job["processed_tiles"],
        "progress_percent": (job["processed_tiles"] / job["total_tiles"] * 100) if job["total_tiles"] > 0 else 0,
        "status": job["status"]
    }


# ==================== TILE MANAGEMENT ====================

def create_tiles(job_id, tile_positions):
    """Create tile records for a job."""
    conn = get_db()
    cursor = conn.cursor()
    tiles = [(f"{job_id}_tile_{i}", job_id, x, y, 'pending') 
             for i, (x, y) in enumerate(tile_positions)]
    cursor.executemany('''
        INSERT INTO tiles (tile_id, job_id, x, y, status)
        VALUES (?, ?, ?, ?, ?)
    ''', tiles)
    conn.commit()


def update_tile_status(tile_id, status):
    """Update tile processing status."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE tiles 
        SET status = ?, processed_at = CURRENT_TIMESTAMP
        WHERE tile_id = ?
    ''', (status, tile_id))
    conn.commit()


# ==================== WORKER MANAGEMENT ====================

def update_worker_heartbeat(worker_id):
    """Update or create worker heartbeat."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO workers (worker_id, last_heartbeat, status)
        VALUES (?, CURRENT_TIMESTAMP, 'active')
        ON CONFLICT(worker_id) DO UPDATE SET
            last_heartbeat = CURRENT_TIMESTAMP,
            status = 'active'
    ''', (worker_id,))
    conn.commit()


def increment_worker_tasks(worker_id):
    """Increment task count for a worker."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE workers 
        SET total_tasks_processed = total_tasks_processed + 1
        WHERE worker_id = ?
    ''', (worker_id,))
    conn.commit()


def get_active_workers():
    """Get list of active workers (heartbeat within last 15 seconds)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT worker_id, last_heartbeat, total_tasks_processed
        FROM workers
        WHERE datetime(last_heartbeat) > datetime('now', '-15 seconds')
        AND status = 'active'
    ''')
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def get_all_workers():
    """Get all workers with their status."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            worker_id, 
            last_heartbeat, 
            status,
            total_tasks_processed,
            CASE 
                WHEN datetime(last_heartbeat) > datetime('now', '-15 seconds') 
                THEN 'active' 
                ELSE 'inactive' 
            END as current_status
        FROM workers
        ORDER BY last_heartbeat DESC
    ''')
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def mark_inactive_workers():
    """Mark workers as inactive if no heartbeat in last 15 seconds."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE workers 
        SET status = 'inactive'
        WHERE datetime(last_heartbeat) < datetime('now', '-15 seconds')
    ''')
    conn.commit()


# ==================== STATISTICS ====================

def get_system_stats():
    """Get overall system statistics."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Total jobs
    cursor.execute('SELECT COUNT(*) as total FROM jobs')
    total_jobs = cursor.fetchone()['total']
    
    # Completed jobs
    cursor.execute("SELECT COUNT(*) as total FROM jobs WHERE status = 'completed'")
    completed_jobs = cursor.fetchone()['total']
    
    # Processing jobs
    cursor.execute("SELECT COUNT(*) as total FROM jobs WHERE status = 'processing'")
    processing_jobs = cursor.fetchone()['total']
    
    # Active workers
    active_workers = len(get_active_workers())
    
    return {
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "processing_jobs": processing_jobs,
        "active_workers": active_workers
    }


if __name__ == "__main__":
    init_db()
    print("Database setup complete!")
