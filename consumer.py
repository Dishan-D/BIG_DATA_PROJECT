# consumer.py
from confluent_kafka import Consumer
import json

BROKER_IP = "172.24.52.130:9092"
TASK_TOPIC = "tasks"

def create_consumer(group_id="image-workers"):
    """Create and configure Kafka consumer."""
    consumer = Consumer({
        'bootstrap.servers': BROKER_IP,
        'group.id': group_id,
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe([TASK_TOPIC])
    print(f"🟢 Worker subscribed to topic '{TASK_TOPIC}'")
    return consumer

def consume_tile(consumer):
    """Poll Kafka for a new image tile."""
    msg = consumer.poll(1.0)
    if msg is None:
        return None
    if msg.error():
        print("❌ Kafka error:", msg.error())
        return None

    value = msg.value().decode('utf-8')
    try:
        # Try JSON format first (new format)
        try:
            data = json.loads(value)
            return {
                "job_id": data.get("job_id"),
                "tile_idx": data.get("tile_idx"),
                "x": int(data["x"]),
                "y": int(data["y"]),
                "b64_tile": data["b64_tile"],
                "tile_id": msg.key().decode('utf-8')
            }
        except (json.JSONDecodeError, KeyError):
            # Fallback to old CSV format
            x, y, b64_tile = value.split(",", 2)
            return {
                "job_id": None,
                "tile_idx": None,
                "x": int(x),
                "y": int(y),
                "b64_tile": b64_tile,
                "tile_id": msg.key().decode('utf-8')
            }
    except Exception as e:
        print("⚠️ Error decoding message:", e)
        return None
