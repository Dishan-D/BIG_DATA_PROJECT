#!/usr/bin/env python3
"""
Initialize Kafka Topics
Creates the required topics if they don't exist
"""

from confluent_kafka.admin import AdminClient, NewTopic
import sys

# Configuration
BROKER_IP = "172.24.52.130:9092"
TOPICS = ["tasks", "results", "heartbeats"]
NUM_PARTITIONS = 2
REPLICATION_FACTOR = 1


def create_topics():
    """Create Kafka topics if they don't exist."""
    
    # Create admin client
    admin_client = AdminClient({'bootstrap.servers': BROKER_IP})
    
    print(f"🔌 Connecting to Kafka broker at {BROKER_IP}...")
    
    # Get existing topics
    try:
        metadata = admin_client.list_topics(timeout=10)
        existing_topics = set(metadata.topics.keys())
        print(f"📋 Existing topics: {existing_topics}")
    except Exception as e:
        print(f"❌ Failed to connect to Kafka broker: {e}")
        print(f"⚠️  Make sure Kafka is running at {BROKER_IP}")
        sys.exit(1)
    
    # Prepare topics to create
    topics_to_create = []
    for topic_name in TOPICS:
        if topic_name not in existing_topics:
            topics_to_create.append(
                NewTopic(
                    topic_name,
                    num_partitions=NUM_PARTITIONS,
                    replication_factor=REPLICATION_FACTOR
                )
            )
            print(f"➕ Will create topic: {topic_name}")
        else:
            print(f"✅ Topic already exists: {topic_name}")
    
    # Create topics if needed
    if topics_to_create:
        print(f"\n🚀 Creating {len(topics_to_create)} topics...")
        
        # Create topics
        fs = admin_client.create_topics(topics_to_create)
        
        # Wait for operations to finish
        for topic, f in fs.items():
            try:
                f.result()  # The result itself is None
                print(f"✅ Topic created successfully: {topic}")
            except Exception as e:
                print(f"❌ Failed to create topic {topic}: {e}")
    else:
        print("\n✅ All required topics already exist!")
    
    # Verify final state
    print("\n📊 Final topic list:")
    metadata = admin_client.list_topics(timeout=10)
    for topic_name in TOPICS:
        if topic_name in metadata.topics:
            topic_metadata = metadata.topics[topic_name]
            print(f"  ✅ {topic_name}: {len(topic_metadata.partitions)} partitions")
        else:
            print(f"  ❌ {topic_name}: NOT FOUND")
    
    print("\n✨ Kafka topics are ready!")


if __name__ == "__main__":
    try:
        create_topics()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
