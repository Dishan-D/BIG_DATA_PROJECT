# producer.py
from confluent_kafka import Producer, KafkaException
import json
import logging

BROKER_IP = "172.24.52.130:9092"
RESULT_TOPIC = "results"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_producer():
    """Create and configure Kafka producer with error handling."""
    try:
        config = {
            'bootstrap.servers': BROKER_IP,
            'client.id': 'worker-producer',
            'enable.idempotence': True,  # Prevent duplicates
            'max.in.flight.requests.per.connection': 5,
            'retries': 5,
            'request.timeout.ms': 30000,
        }
        
        producer = Producer(config)
        logger.info(f"✅ Producer created successfully (broker: {BROKER_IP})")
        return producer
    except Exception as e:
        logger.error(f"❌ Failed to create producer: {e}")
        raise


def delivery_report(err, msg):
    """Callback to confirm delivery with detailed logging."""
    if err is not None:
        logger.error(f"❌ Delivery failed for tile {msg.key().decode() if msg.key() else 'unknown'}: {err}")
        logger.error(f"   Error type: {type(err).__name__}")
        logger.error(f"   Topic: {msg.topic()}")
    else:
        tile_key = msg.key().decode() if msg.key() else 'unknown'
        logger.info(f"✅ Tile {tile_key} delivered to {msg.topic()} partition {msg.partition()} offset {msg.offset()}")


def send_result(producer, tile_id, x, y, b64_processed, job_id=None):
    """
    Send processed tile to Kafka results topic with comprehensive error handling.
    
    Args:
        producer: Kafka producer instance
        tile_id: Unique tile identifier
        x: X coordinate of tile
        y: Y coordinate of tile
        b64_processed: Base64 encoded processed image
        job_id: Job identifier (optional)
        
    Raises:
        ValueError: If required parameters are invalid
        KafkaException: If Kafka operation fails
    """
    try:
        # Validate inputs
        if not tile_id:
            raise ValueError("tile_id cannot be empty")
        
        if not b64_processed:
            raise ValueError("b64_processed cannot be empty")
        
        if not isinstance(x, int) or not isinstance(y, int):
            raise ValueError(f"x and y must be integers, got x={type(x)}, y={type(y)}")
        
        # Prepare message
        message = {
            "tile_id": str(tile_id),
            "x": int(x),
            "y": int(y),
            "b64_processed": b64_processed,
            "job_id": job_id
        }
        
        # Serialize message
        try:
            message_json = json.dumps(message)
            message_bytes = message_json.encode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to serialize message: {e}")
        
        logger.debug(f"📤 Sending tile {tile_id} to {RESULT_TOPIC} (size: {len(message_bytes)} bytes)")
        
        # Send to Kafka
        try:
            producer.produce(
                RESULT_TOPIC,
                key=str(tile_id).encode('utf-8'),
                value=message_bytes,
                callback=delivery_report
            )
            
            # Trigger callbacks
            producer.poll(0)
            
        except BufferError as be:
            logger.error(f"❌ Producer queue full for tile {tile_id}, waiting...")
            producer.flush()  # Wait for queue to clear
            raise
        except KafkaException as ke:
            logger.error(f"❌ Kafka error sending tile {tile_id}: {ke}")
            raise
        
    except ValueError as ve:
        logger.error(f"❌ Validation error: {ve}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error sending result for tile {tile_id}: {e}")
        logger.debug(f"   tile_id={tile_id}, x={x}, y={y}, job_id={job_id}")
        logger.debug(f"   b64_processed length: {len(b64_processed) if b64_processed else 0}")
        raise
