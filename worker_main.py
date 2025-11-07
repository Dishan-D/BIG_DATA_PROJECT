# worker_main.py
import time
import json
import threading
import logging
import sys
import traceback
from consumer import create_consumer, consume_tile
from producer import create_producer, send_result
from processor import process_blur

# ================= CONFIG =================
WORKER_ID = "worker-2"                # Change for each worker
BROKER_IP = "172.24.52.130:9092"
HEARTBEAT_TOPIC = "heartbeats"
HEARTBEAT_INTERVAL = 5                # seconds
DEBUG_MODE = True                     # Enable detailed logging
# ==========================================

# Setup logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format=f'[{WORKER_ID}] %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# ------------ HEARTBEAT THREAD ------------
def send_heartbeat_continuously(producer, worker_id):
    """Continuously send heartbeat messages in the background."""
    consecutive_failures = 0
    max_failures = 5
    
    while True:
        try:
            msg = {
                "worker_id": worker_id,
                "timestamp": time.time(),
                "status": "alive"
            }
            producer.produce(HEARTBEAT_TOPIC, value=json.dumps(msg).encode('utf-8'))
            producer.poll(0)
            
            # Reset failure counter on success
            if consecutive_failures > 0:
                logging.info(f"💓 Heartbeat recovered after {consecutive_failures} failures")
                consecutive_failures = 0
                
        except Exception as e:
            consecutive_failures += 1
            logging.error(f"❌ Heartbeat failed ({consecutive_failures}/{max_failures}): {e}")
            
            if consecutive_failures >= max_failures:
                logging.critical(f"🚨 Heartbeat failed {max_failures} times! Check Kafka connection!")
                consecutive_failures = 0  # Reset to avoid log spam
            
        time.sleep(HEARTBEAT_INTERVAL)


# ------------ MAIN WORKER LOGIC ------------
def main():
    """Main worker process with comprehensive error handling."""
    tiles_processed = 0
    errors_encountered = 0
    
    try:
        logging.info(f"🔧 Initializing {WORKER_ID}...")
        logging.info(f"📍 Kafka Broker: {BROKER_IP}")
        logging.info(f"💓 Heartbeat Interval: {HEARTBEAT_INTERVAL}s")
        logging.info(f"🐛 Debug Mode: {'ON' if DEBUG_MODE else 'OFF'}")
        
        # Initialize consumer
        logging.info("📥 Creating Kafka consumer...")
        consumer = create_consumer(group_id="image-workers")
        
        # Initialize producer
        logging.info("📤 Creating Kafka producer...")
        producer = create_producer()
        
        logging.info(f"✅ {WORKER_ID} initialized successfully!")
        logging.info(f"🚀 {WORKER_ID} started (BLUR mode) and waiting for tiles...")
        
        # Start background heartbeat thread
        logging.info("💓 Starting heartbeat thread...")
        heartbeat_thread = threading.Thread(
            target=send_heartbeat_continuously,
            args=(producer, WORKER_ID),
            daemon=True
        )
        heartbeat_thread.start()
        logging.info("✅ Heartbeat thread started")
        
        # Main processing loop
        while True:
            try:
                # Poll for new message
                msg = consume_tile(consumer)
                
                if msg is None:
                    # No message available, continue polling
                    continue
                
                # Extract message data
                tile_id = msg.get("tile_id", "unknown")
                x = msg.get("x", 0)
                y = msg.get("y", 0)
                b64_tile = msg.get("b64_tile")
                job_id = msg.get("job_id", "unknown")
                
                # Validate message data
                if not b64_tile:
                    logging.error(f"⚠️ Received message without tile data: {msg}")
                    errors_encountered += 1
                    continue
                
                logging.info(f"🧩 Processing tile {tile_id} from job {job_id} at ({x},{y})")
                
                # Process the tile
                try:
                    processed_tile = process_blur(b64_tile)
                    logging.debug(f"✓ Tile {tile_id} processed successfully")
                except Exception as proc_error:
                    logging.error(f"❌ Processing error for tile {tile_id}: {proc_error}")
                    logging.debug(f"Traceback: {traceback.format_exc()}")
                    errors_encountered += 1
                    continue
                
                # Send result
                try:
                    send_result(producer, tile_id, x, y, processed_tile, job_id)
                    tiles_processed += 1
                    logging.info(f"✅ Tile {tile_id} sent to results (Total: {tiles_processed}, Errors: {errors_encountered})")
                except Exception as send_error:
                    logging.error(f"❌ Failed to send result for tile {tile_id}: {send_error}")
                    logging.debug(f"Traceback: {traceback.format_exc()}")
                    errors_encountered += 1
                    continue
                
                # Simulate processing delay
                time.sleep(0.3)
                
            except Exception as loop_error:
                logging.error(f"❌ Error in processing loop: {loop_error}")
                logging.debug(f"Traceback: {traceback.format_exc()}")
                errors_encountered += 1
                time.sleep(1)  # Prevent rapid error loop
                
    except KeyboardInterrupt:
        logging.info(f"🛑 {WORKER_ID} received shutdown signal (Ctrl+C)")
        logging.info(f"📊 Final Stats: Processed={tiles_processed}, Errors={errors_encountered}")
    except Exception as fatal_error:
        logging.critical(f"💥 FATAL ERROR in {WORKER_ID}: {fatal_error}")
        logging.critical(f"Traceback:\n{traceback.format_exc()}")
        sys.exit(1)
    finally:
        logging.info(f"🔄 Cleaning up {WORKER_ID}...")
        try:
            consumer.close()
            logging.info("✓ Consumer closed")
        except Exception as e:
            logging.error(f"Error closing consumer: {e}")
        
        try:
            producer.flush()
            logging.info("✓ Producer flushed")
        except Exception as e:
            logging.error(f"Error flushing producer: {e}")
        
        logging.info(f"👋 {WORKER_ID} stopped. Processed {tiles_processed} tiles with {errors_encountered} errors.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical(f"💥 Failed to start {WORKER_ID}: {e}")
        logging.critical(f"Traceback:\n{traceback.format_exc()}")
        sys.exit(1)
