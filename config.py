# config.py
"""
Centralized configuration for the Distributed Image Processing Pipeline
Update these settings according to your environment
"""

# ========================= KAFKA CONFIGURATION =========================
BROKER_IP = "172.24.52.130:9092"  # Update with your Kafka broker IP
TASK_TOPIC = "tasks"              # Topic for distributing image tiles
RESULT_TOPIC = "results"          # Topic for collecting processed tiles
HEARTBEAT_TOPIC = "heartbeats"    # Topic for worker health monitoring

# ========================= IMAGE PROCESSING =========================
TILE_SIZE = 512                   # Size of image tiles (512x512 pixels)
MIN_IMAGE_SIZE = 1024             # Minimum image dimension (1024x1024)
MAX_FILE_SIZE = 50 * 1024 * 1024  # Max upload size (50MB)

# ========================= PROCESSING TIMEOUTS =========================
WAIT_TIMEOUT = 120                # Seconds to wait for all results
HEARTBEAT_INTERVAL = 5            # Seconds between worker heartbeats
WORKER_TIMEOUT = 15               # Seconds before marking worker inactive

# ========================= DATABASE =========================
DB_PATH = "image_processing.db"   # SQLite database file path

# ========================= WEB APPLICATION =========================
FLASK_HOST = "0.0.0.0"            # Flask server host
FLASK_PORT = 5000                 # Flask server port
FLASK_DEBUG = True                # Enable debug mode
UPLOAD_FOLDER = "uploads"         # Directory for uploaded images
OUTPUT_FOLDER = "outputs"         # Directory for processed images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

# ========================= WORKER CONFIGURATION =========================
# Update this for each worker instance
DEFAULT_WORKER_ID = "worker-1"    # Default worker identifier
PROCESSING_DELAY = 0.3            # Simulated processing delay (seconds)

# ========================= IMAGE PROCESSING MODE =========================
# Options: 'blur', 'grayscale', 'edge_detection', 'sharpen'
PROCESSING_MODE = 'blur'

# ========================= KAFKA CONSUMER GROUPS =========================
MASTER_RESULTS_GROUP = "master-results-group"
MASTER_HEARTBEAT_GROUP = "master-heartbeat-group"
WORKER_GROUP = "image-workers"

# ========================= KAFKA ADVANCED SETTINGS =========================
KAFKA_AUTO_OFFSET_RESET = 'latest'  # 'earliest' or 'latest'
KAFKA_ENABLE_AUTO_COMMIT = True
KAFKA_SESSION_TIMEOUT_MS = 10000
KAFKA_MAX_POLL_INTERVAL_MS = 300000


def get_kafka_producer_config():
    """Get Kafka producer configuration."""
    return {
        'bootstrap.servers': BROKER_IP,
        'client.id': 'image-processor-producer'
    }


def get_kafka_consumer_config(group_id):
    """Get Kafka consumer configuration."""
    return {
        'bootstrap.servers': BROKER_IP,
        'group.id': group_id,
        'auto.offset.reset': KAFKA_AUTO_OFFSET_RESET,
        'enable.auto.commit': KAFKA_ENABLE_AUTO_COMMIT,
        'session.timeout.ms': KAFKA_SESSION_TIMEOUT_MS,
        'max.poll.interval.ms': KAFKA_MAX_POLL_INTERVAL_MS
    }


def print_config():
    """Print current configuration (for debugging)."""
    print("=" * 60)
    print("DISTRIBUTED IMAGE PROCESSING - CONFIGURATION")
    print("=" * 60)
    print(f"Kafka Broker:        {BROKER_IP}")
    print(f"Task Topic:          {TASK_TOPIC}")
    print(f"Result Topic:        {RESULT_TOPIC}")
    print(f"Heartbeat Topic:     {HEARTBEAT_TOPIC}")
    print(f"Tile Size:           {TILE_SIZE}x{TILE_SIZE}")
    print(f"Min Image Size:      {MIN_IMAGE_SIZE}x{MIN_IMAGE_SIZE}")
    print(f"Processing Mode:     {PROCESSING_MODE}")
    print(f"Flask Port:          {FLASK_PORT}")
    print(f"Worker Timeout:      {WORKER_TIMEOUT}s")
    print(f"Heartbeat Interval:  {HEARTBEAT_INTERVAL}s")
    print("=" * 60)


if __name__ == "__main__":
    print_config()
