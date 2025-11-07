# consumer.py
from confluent_kafka import Consumer
import json

BROKER_IP = "172.24.52.130:9092"
TASK_TOPIC = "tasks"

def create_consumer(group_id="image-workers"):
    """Create and configure Kafka consumer with proper load balancing settings."""
    consumer = Consumer({
        'bootstrap.servers': BROKER_IP,
        'group.id': group_id,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
        'partition.assignment.strategy': 'range',  # Changed to 'range' for more deterministic assignment
        'session.timeout.ms': 45000,
        'heartbeat.interval.ms': 3000,
        'max.poll.interval.ms': 300000,
        'client.id': None  # Let Kafka auto-generate unique client IDs
    })
    consumer.subscribe([TASK_TOPIC])
    print(f"🟢 Worker subscribed to topic '{TASK_TOPIC}' with range strategy")
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
    
    # Try JSON format first (new format from master_api.py)
    try:
        data = json.loads(value)
        return {
            "job_id": data.get("job_id"),
            "tile_idx": data.get("tile_idx"),
            "x": int(data["x"]),
            "y": int(data["y"]),
            "b64_tile": data["b64_tile"],
            "tile_id": msg.key().decode('utf-8') if msg.key() else str(data.get("tile_idx", 0))
        }
    except json.JSONDecodeError:
        # Not JSON, try old CSV format: "x,y,base64_data"
        try:
            x, y, b64_tile = value.split(",", 2)
            return {
                "job_id": None,
                "tile_idx": None,
                "x": int(x),
                "y": int(y),
                "b64_tile": b64_tile,
                "tile_id": msg.key().decode('utf-8') if msg.key() else "unknown"
            }
        except Exception as e:
            print(f"⚠️ Error decoding CSV format: {e}")
            return None
    except (KeyError, ValueError, TypeError) as e:
        print(f"⚠️ Error parsing message data: {e}")
        print(f"   Message value (first 200 chars): {value[:200]}")
        return None
