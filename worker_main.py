# worker_main.py
import time
import json
import threading
from consumer import create_consumer, consume_tile
from producer import create_producer, send_result
from processor import process_blur

# ================= CONFIG =================
WORKER_ID = "worker-2"                # Change for each worker
BROKER_IP = "172.24.52.130:9092"
HEARTBEAT_TOPIC = "heartbeats"
HEARTBEAT_INTERVAL = 5                # seconds
# ==========================================


# ------------ HEARTBEAT THREAD ------------
def send_heartbeat_continuously(producer, worker_id):
    """Continuously send heartbeat messages in the background."""
    while True:
        try:
            msg = {
                "worker_id": worker_id,
                "timestamp": time.time(),
                "status": "alive"
            }
            producer.produce(HEARTBEAT_TOPIC, value=json.dumps(msg).encode('utf-8'))
            producer.poll(0)
        except Exception as e:
            # Don’t print in production; just retry silently
            time.sleep(HEARTBEAT_INTERVAL)
            continue

        time.sleep(HEARTBEAT_INTERVAL)  # wait before next heartbeat


# ------------ MAIN WORKER LOGIC ------------
def main():
    consumer = create_consumer(group_id="image-workers")
    producer = create_producer()
    print(f"🚀 {WORKER_ID} started (BLUR mode) and waiting for tiles...")

    # Start background heartbeat thread
    heartbeat_thread = threading.Thread(
        target=send_heartbeat_continuously,
        args=(producer, WORKER_ID),
        daemon=True
    )
    heartbeat_thread.start()

    try:
        while True:
            msg = consume_tile(consumer)
            if msg is None:
                continue

            tile_id = msg["tile_id"]
            x, y = msg["x"], msg["y"]
            b64_tile = msg["b64_tile"]
            job_id = msg.get("job_id")  # Get job_id if available

            print(f"🧩 {WORKER_ID} processing tile {tile_id} at ({x},{y})...")

            processed_tile = process_blur(b64_tile)
            send_result(producer, tile_id, x, y, processed_tile, job_id)

            time.sleep(0.3)  # simulate processing delay

    except KeyboardInterrupt:
        print(f"🛑 {WORKER_ID} stopped manually.")
    finally:
        consumer.close()
        producer.flush()


if __name__ == "__main__":
    main()
