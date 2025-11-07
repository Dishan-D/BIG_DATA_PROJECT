# master_api.py
"""
API layer for master node - handles image processing orchestration
Integrates with database for job tracking and Kafka for task distribution
"""

import cv2
import base64
import json
import numpy as np
from io import BytesIO
from PIL import Image
import time
import threading
from confluent_kafka import Producer, Consumer
from database import (
    create_job, update_job_status, increment_processed_tiles,
    get_job, create_tiles, update_worker_heartbeat
)

# ========================= CONFIG =========================
BROKER_IP = "172.24.52.130:9092"
TASK_TOPIC = "tasks"
RESULT_TOPIC = "results"
HEARTBEAT_TOPIC = "heartbeats"
TILE_SIZE = 512
WAIT_TIMEOUT = 120  # seconds
# ===========================================================

# Global consumers (initialized once)
_result_consumer = None
_heartbeat_consumer = None
_consumers_lock = threading.Lock()


def get_result_consumer():
    """Get or create result consumer (singleton)."""
    global _result_consumer
    with _consumers_lock:
        if _result_consumer is None:
            _result_consumer = Consumer({
                'bootstrap.servers': BROKER_IP,
                'group.id': 'master-results-group',
                'auto.offset.reset': 'latest',
                'enable.auto.commit': True,
                'session.timeout.ms': 60000,  # 60 seconds before considering consumer dead
                'heartbeat.interval.ms': 3000,  # Send heartbeat every 3 seconds
                'max.poll.interval.ms': 300000  # 5 minutes max time between polls
            })
            _result_consumer.subscribe([RESULT_TOPIC])
            print(f"🟢 Result consumer initialized")
    return _result_consumer


def get_heartbeat_consumer():
    """Get or create heartbeat consumer (singleton)."""
    global _heartbeat_consumer
    with _consumers_lock:
        if _heartbeat_consumer is None:
            _heartbeat_consumer = Consumer({
                'bootstrap.servers': BROKER_IP,
                'group.id': 'master-heartbeat-group',
                'auto.offset.reset': 'earliest',  # Changed from 'latest' to catch all heartbeats
                'enable.auto.commit': True,
                'session.timeout.ms': 60000,  # 60 seconds
                'heartbeat.interval.ms': 3000,  # 3 seconds
                'max.poll.interval.ms': 300000  # 5 minutes
            })
            _heartbeat_consumer.subscribe([HEARTBEAT_TOPIC])
            print(f"🟢 Heartbeat consumer initialized")
            # Start heartbeat monitoring thread
            thread = threading.Thread(target=monitor_heartbeats, daemon=True)
            thread.start()
    return _heartbeat_consumer


def create_producer():
    """Create Kafka producer."""
    try:
        producer = Producer({'bootstrap.servers': BROKER_IP})
        return producer
    except Exception as e:
        print(f"❌ Failed to connect to Kafka broker: {e}")
        return None


# ------------ Image Processing Utils ------------

def split_image(image, tile_size=512):
    """Split image into tiles."""
    h, w, _ = image.shape
    tiles = []
    positions = []
    
    for y in range(0, h, tile_size):
        for x in range(0, w, tile_size):
            tile = image[y:min(y+tile_size, h), x:min(x+tile_size, w)]
            tiles.append(((x, y), tile))
            positions.append((x, y))
    
    return tiles, (w, h), positions


def decode_tile(b64_tile):
    """Convert base64-encoded image back to OpenCV array."""
    try:
        img_bytes = base64.b64decode(b64_tile)
        pil_img = Image.open(BytesIO(img_bytes)).convert("RGB")
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        return img
    except Exception as e:
        print(f"⚠️ Error decoding tile: {e}")
        return None


# ------------ Task Distribution ------------

def send_tiles(producer, job_id, tiles):
    """Send all tiles to Kafka tasks topic with proper partitioning for load balancing."""
    for idx, ((x, y), tile) in enumerate(tiles):
        try:
            _, buf = cv2.imencode(".jpg", tile)
            b64_tile = base64.b64encode(buf).decode('utf-8')
            
            # Create task message with job_id
            task_data = {
                "job_id": job_id,
                "tile_idx": idx,
                "x": x,
                "y": y,
                "b64_tile": b64_tile
            }
            
            # Send as JSON - use tile index as key for round-robin partitioning
            # This ensures tiles are distributed across partitions (and thus workers)
            producer.produce(
                TASK_TOPIC,
                key=str(idx).encode('utf-8'),  # Use simple integer key for better distribution
                value=json.dumps(task_data).encode('utf-8'),
                partition=-1  # Let Kafka decide partition based on key hash
            )
            
            if idx % 5 == 0:
                producer.poll(0)
                
        except Exception as e:
            print(f"⚠️ Error sending tile {idx}: {e}")
    
    producer.flush()
    print(f"✅ All {len(tiles)} tiles sent for job {job_id}")


# ------------ Result Collection ------------

def collect_results(job_id, total_tiles, image_size):
    """Collect processed tiles and reconstruct image."""
    consumer = get_result_consumer()
    received_tiles = {}
    w, h = image_size
    start_time = time.time()
    
    print(f"\n📡 Collecting results for job {job_id}...")
    
    while len(received_tiles) < total_tiles:
        if time.time() - start_time > WAIT_TIMEOUT:
            print(f"⏰ Timeout for job {job_id}")
            update_job_status(job_id, 'timeout')
            break
        
        msg = consumer.poll(timeout=1.0)
        if not msg or msg.error():
            continue
        
        try:
            data = json.loads(msg.value().decode('utf-8'))
            
            # Check if this result belongs to our job
            if data.get("job_id") != job_id:
                continue
            
            tile_id = data["tile_id"]
            x, y = data["x"], data["y"]
            b64_processed = data["b64_processed"]
            
            img_tile = decode_tile(b64_processed)
            if img_tile is None:
                continue
            
            received_tiles[tile_id] = (x, y, img_tile)
            increment_processed_tiles(job_id)
            
            print(f"✅ Job {job_id}: Received tile {len(received_tiles)}/{total_tiles}")
            
        except Exception as e:
            print(f"⚠️ Error processing result: {e}")
    
    # Reconstruct image
    print(f"\n🧩 Reconstructing image for job {job_id}...")
    final_img = np.zeros((h, w, 3), dtype=np.uint8)
    
    for _, (x, y, tile) in received_tiles.items():
        final_img[y:y + tile.shape[0], x:x + tile.shape[1]] = tile
    
    return final_img, len(received_tiles) == total_tiles


# ------------ Heartbeat Monitoring ------------

def monitor_heartbeats():
    """Background thread to monitor worker heartbeats."""
    consumer = get_heartbeat_consumer()
    print("💓 Heartbeat monitoring started")
    
    while True:
        try:
            msg = consumer.poll(timeout=0.5)
            if not msg:
                continue
            
            if msg.error():
                print(f"⚠️ Heartbeat consumer error: {msg.error()}")
                continue
            
            try:
                data = json.loads(msg.value().decode('utf-8'))
                worker_id = data.get("worker_id")
                
                if worker_id:
                    update_worker_heartbeat(worker_id)
                    print(f"💓 Heartbeat received from {worker_id}")
            except json.JSONDecodeError as e:
                print(f"⚠️ Failed to parse heartbeat message: {e}")
            except Exception as e:
                print(f"⚠️ Error processing heartbeat: {e}")
                
        except Exception as e:
            print(f"⚠️ Heartbeat monitoring error: {e}")
            time.sleep(1)


# ------------ Main Processing Function ------------

def process_image_async(job_id, input_path, output_path, filename):
    """
    Process image asynchronously - called from Flask in background thread.
    """
    try:
        start_time = time.time()
        
        # Load image
        img = cv2.imread(input_path)
        if img is None:
            update_job_status(job_id, 'failed')
            print(f"❌ Failed to load image: {input_path}")
            return
        
        h, w = img.shape[:2]
        
        # Validate minimum size
        if w < 1024 or h < 1024:
            update_job_status(job_id, 'failed')
            print(f"❌ Image too small. Minimum size: 1024x1024")
            return
        
        # Split into tiles
        tiles, img_size, positions = split_image(img, TILE_SIZE)
        print(f"🖼️ Job {job_id}: Image size={img.shape}, tiles={len(tiles)}")
        
        # Create job in database
        create_job(job_id, filename, len(tiles), w, h)
        create_tiles(job_id, positions)
        
        # Send tiles to Kafka
        producer = create_producer()
        if not producer:
            update_job_status(job_id, 'failed')
            return
        
        send_tiles(producer, job_id, tiles)
        
        # Collect results
        final_img, complete = collect_results(job_id, len(tiles), img_size)
        
        # Save output
        cv2.imwrite(output_path, final_img)
        
        # Update job status
        if complete:
            update_job_status(job_id, 'completed', output_path)
            print(f"✅ Job {job_id} completed in {time.time() - start_time:.2f}s")
        else:
            update_job_status(job_id, 'partial', output_path)
            print(f"⚠️ Job {job_id} partially completed")
            
    except Exception as e:
        print(f"❌ Error processing job {job_id}: {e}")
        update_job_status(job_id, 'failed')


def get_processing_status(job_id):
    """Get current processing status for a job."""
    return get_job(job_id)


# Initialize consumers when module loads
def init_consumers():
    """Initialize Kafka consumers."""
    get_result_consumer()
    get_heartbeat_consumer()


if __name__ == "__main__":
    init_consumers()
    print("Master API initialized")
