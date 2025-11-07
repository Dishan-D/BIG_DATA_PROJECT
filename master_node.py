from confluent_kafka import Producer, Consumer
import cv2
import base64
import json
import numpy as np
from io import BytesIO
from PIL import Image
import time
import sys

# ========================= CONFIG =========================
BROKER_IP = "172.24.52.130:9092"   # Kafka broker ZeroTier IP
TASK_TOPIC = "tasks"
RESULT_TOPIC = "results"
IMG_PATH = "input_image.jpg"      # Path to your local image
OUTPUT_PATH = "processed_output.jpg"
TILE_SIZE = 512
WAIT_TIMEOUT = 120  # seconds before giving up waiting for results
# ===========================================================


# ------------ Kafka Setup ------------
def create_producer():
    """Create Kafka producer."""
    try:
        producer = Producer({'bootstrap.servers': BROKER_IP})
        print(f"🟢 Connected to Kafka broker at {BROKER_IP}")
        return producer
    except Exception as e:
        print(f"❌ Failed to connect to Kafka broker: {e}")
        sys.exit(1)


def create_consumer(group_id="master-results-group"):
    """Create Kafka consumer subscribed to results topic."""
    try:
        consumer = Consumer({
            'bootstrap.servers': BROKER_IP,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        })
        consumer.subscribe([RESULT_TOPIC])
        print(f"🟢 Subscribed to topic '{RESULT_TOPIC}' as group '{group_id}'")
        return consumer
    except Exception as e:
        print(f"❌ Failed to create consumer: {e}")
        sys.exit(1)


# ------------ Image Utils ------------
def split_image(image, tile_size=512):
    """Split image into tiles (handles non-divisible dimensions safely)."""
    h, w, _ = image.shape
    tiles = []
    for y in range(0, h, tile_size):
        for x in range(0, w, tile_size):
            # clip the edges safely
            tile = image[y:min(y+tile_size, h), x:min(x+tile_size, w)]
            tiles.append(((x, y), tile))
    return tiles, (w, h)


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


# ------------ Master Logic ------------
def send_tiles(producer, tiles):
    """Send all tiles to Kafka 'tasks' topic."""
    for idx, ((x, y), tile) in enumerate(tiles):
        try:
            _, buf = cv2.imencode(".jpg", tile)
            b64_tile = base64.b64encode(buf).decode('utf-8')
            data = f"{x},{y},{b64_tile}"

            producer.produce(TASK_TOPIC, key=str(idx), value=data.encode('utf-8'))
            print(f"📤 Sent tile {idx} ({x},{y}) to Kafka")

            # Poll periodically to allow Kafka callbacks to run
            if idx % 5 == 0:
                producer.poll(0)
        except Exception as e:
            print(f"⚠️ Error sending tile {idx}: {e}")

    producer.flush()
    print("✅ All tiles sent to Kafka successfully.")


def collect_results(consumer, total_tiles, image_size):
    """Collect processed tiles from 'results' topic and reconstruct image."""
    received_tiles = {}
    w, h = image_size
    start_time = time.time()

    print("\n📡 Waiting for processed tiles from workers...\n")

    while len(received_tiles) < total_tiles:
        if time.time() - start_time > WAIT_TIMEOUT:
            print("⏰ Timeout waiting for worker results.")
            break

        msg = consumer.poll(timeout=1.0)
        if not msg:
            continue
        if msg.error():
            print("❌ Kafka error:", msg.error())
            continue

        try:
            data = json.loads(msg.value().decode('utf-8'))
            tile_id = data["tile_id"]
            x, y = data["x"], data["y"]
            b64_processed = data["b64_processed"]

            img_tile = decode_tile(b64_processed)
            if img_tile is None:
                continue

            received_tiles[tile_id] = (x, y, img_tile)
            print(f"✅ Received processed tile {tile_id} ({len(received_tiles)}/{total_tiles})")

        except Exception as e:
            print(f"⚠️ Error processing Kafka message: {e}")

    if len(received_tiles) < total_tiles:
        print(f"⚠️ Only received {len(received_tiles)}/{total_tiles} tiles. Partial image will be saved.")

    # Merge all available tiles
    print("\n🧩 Reconstructing final image...")
    final_img = np.zeros((h, w, 3), dtype=np.uint8)
    for _, (x, y, tile) in received_tiles.items():
        final_img[y:y + tile.shape[0], x:x + tile.shape[1]] = tile

    cv2.imwrite(OUTPUT_PATH, final_img)
    print(f"🎯 Final image saved at '{OUTPUT_PATH}'")


# ------------ Main Run ------------
if __name__ == "__main__":
    start = time.time()

    # Step 1: Load image
    img = cv2.imread(IMG_PATH)
    if img is None:
        print(f"⚠️ Error: Image not found or unreadable at '{IMG_PATH}'")
        sys.exit(1)

    tiles, img_size = split_image(img, TILE_SIZE)
    print(f"🖼️ Loaded image: {IMG_PATH}, size={img.shape}, tiles={len(tiles)}")

    # Step 2: Connect to Kafka
    producer = create_producer()
    consumer = create_consumer()

    # Step 3: Send tiles → then wait for results
    send_tiles(producer, tiles)
    collect_results(consumer, total_tiles=len(tiles), image_size=img_size)

    print(f"\n⏱️ Total time: {time.time() - start:.2f}s")