# worker_heartbeat.py

import time
import json
from confluent_kafka import Producer

# ================== CONFIG ==================
WORKER_ID = "worker-2"             # Change for each worker
BROKER_IP = "172.24.52.130:9092"
HEARTBEAT_TOPIC = "heartbeats"
HEARTBEAT_INTERVAL = 5             # seconds
# ============================================


def create_producer():
    """Create Kafka producer for heartbeats."""
    try:
        producer = Producer({'bootstrap.servers': BROKER_IP})
        print(f"🟢 Connected to Kafka broker at {BROKER_IP}")
        return producer
    except Exception as e:
        print(f"❌ Failed to connect to Kafka broker: {e}")
        exit(1)


def send_heartbeat(producer, worker_id):
    """Send a heartbeat message to the heartbeats topic."""
    msg = {
        "worker_id": worker_id,
        "timestamp": time.time(),
        "status": "alive"
    }
    producer.produce(HEARTBEAT_TOPIC, value=json.dumps(msg).encode('utf-8'))
    producer.poll(0)
    print(f"💓 Sent heartbeat from {worker_id} at {time.ctime(msg['timestamp'])}")


def main():
    producer = create_producer()
    print(f"🚀 Heartbeat process started for {WORKER_ID}")

    try:
        while True:
            send_heartbeat(producer, WORKER_ID)
            time.sleep(HEARTBEAT_INTERVAL)
    except KeyboardInterrupt:
        print(f"🛑 Heartbeat process for {WORKER_ID} stopped.")
    finally:
        producer.flush()


if __name__ == "__main__":
    main()


