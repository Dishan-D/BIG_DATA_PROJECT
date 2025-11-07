# producer.py
from confluent_kafka import Producer
import json

BROKER_IP = "172.24.52.130:9092"
RESULT_TOPIC = "results"

def create_producer():
    """Create and configure Kafka producer."""
    return Producer({'bootstrap.servers': BROKER_IP})

def delivery_report(err, msg):
    """Callback to confirm delivery."""
    if err is not None:
        print(f"❌ Delivery failed for tile {msg.key().decode()}: {err}")
    else:
        print(f"✅ Processed tile {msg.key().decode()} sent to partition {msg.partition()}")

def send_result(producer, tile_id, x, y, b64_processed, job_id=None):
    """Send processed tile to Kafka results topic."""
    message = {
        "tile_id": tile_id,
        "x": x,
        "y": y,
        "b64_processed": b64_processed,
        "job_id": job_id  # Include job_id for tracking
    }

    producer.produce(
        RESULT_TOPIC,
        key=str(tile_id),
        value=json.dumps(message).encode('utf-8'),
        callback=delivery_report
    )
    producer.poll(0)
