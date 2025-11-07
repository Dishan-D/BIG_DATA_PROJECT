#!/usr/bin/env python3
"""
Check Kafka topic configuration and consumer group status
"""

from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Consumer
import sys

BROKER_IP = "172.24.52.130:9092"

def check_topics():
    """Check if topics exist and their partition count."""
    print("\n" + "="*60)
    print("KAFKA TOPIC CONFIGURATION")
    print("="*60)
    
    try:
        admin_client = AdminClient({'bootstrap.servers': BROKER_IP})
        
        # Get topic metadata
        metadata = admin_client.list_topics(timeout=10)
        
        topics_to_check = ['tasks', 'results', 'heartbeats']
        
        for topic_name in topics_to_check:
            if topic_name in metadata.topics:
                topic = metadata.topics[topic_name]
                partition_count = len(topic.partitions)
                print(f"\n✅ Topic '{topic_name}':")
                print(f"   Partitions: {partition_count}")
                
                if partition_count < 2:
                    print(f"   ⚠️  WARNING: Only {partition_count} partition(s)!")
                    print(f"   ⚠️  For load balancing with 2 workers, you need 2+ partitions")
                    print(f"   ⚠️  Run: kafka-topics.sh --alter --topic {topic_name} --partitions 2")
                else:
                    print(f"   ✓ Good for load balancing")
                
                for partition_id, partition_info in topic.partitions.items():
                    print(f"   Partition {partition_id}: Leader={partition_info.leader}, Replicas={len(partition_info.replicas)}")
            else:
                print(f"\n❌ Topic '{topic_name}' does not exist!")
                print(f"   Create with: kafka-topics.sh --create --topic {topic_name} --partitions 2 --replication-factor 1")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to connect to Kafka: {e}")
        return False


def check_consumer_groups():
    """Check consumer group memberships."""
    print("\n" + "="*60)
    print("CONSUMER GROUP STATUS")
    print("="*60)
    
    try:
        # Create a test consumer to check group
        consumer = Consumer({
            'bootstrap.servers': BROKER_IP,
            'group.id': 'diagnostic-group',
            'auto.offset.reset': 'earliest'
        })
        
        # Get cluster metadata
        metadata = consumer.list_topics(timeout=10)
        
        print(f"\n✅ Connected to Kafka cluster")
        print(f"   Broker: {BROKER_IP}")
        print(f"   Topics available: {len(metadata.topics)}")
        
        # Check worker group
        consumer.close()
        
        # Check if workers are in the group
        worker_consumer = Consumer({
            'bootstrap.servers': BROKER_IP,
            'group.id': 'image-workers',
            'auto.offset.reset': 'earliest'
        })
        
        worker_consumer.subscribe(['tasks'])
        
        print(f"\n📊 Consumer Group: 'image-workers'")
        print(f"   Checking assignments...")
        
        # Get committed offsets
        partitions = worker_consumer.assignment()
        if partitions:
            print(f"   Assigned partitions: {[p.partition for p in partitions]}")
        else:
            print(f"   No partitions assigned yet (workers may not be connected)")
        
        worker_consumer.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error checking consumer groups: {e}")
        return False


def create_topics_with_partitions():
    """Create or modify topics with proper partition count."""
    print("\n" + "="*60)
    print("TOPIC CREATION/MODIFICATION")
    print("="*60)
    
    print("\n⚠️  This requires admin access to Kafka broker.")
    print("Run these commands on your Kafka broker machine:\n")
    
    topics = ['tasks', 'results', 'heartbeats']
    
    for topic in topics:
        print(f"# For {topic} topic:")
        print(f"kafka-topics.sh --bootstrap-server localhost:9092 \\")
        print(f"  --alter --topic {topic} --partitions 2\n")
        print(f"# Or delete and recreate:")
        print(f"kafka-topics.sh --bootstrap-server localhost:9092 \\")
        print(f"  --delete --topic {topic}")
        print(f"kafka-topics.sh --bootstrap-server localhost:9092 \\")
        print(f"  --create --topic {topic} --partitions 2 --replication-factor 1\n")


def test_load_balancing():
    """Test if messages are distributed across partitions."""
    print("\n" + "="*60)
    print("LOAD BALANCING TEST")
    print("="*60)
    
    try:
        from confluent_kafka import Producer
        
        producer = Producer({'bootstrap.servers': BROKER_IP})
        
        print(f"\nSending 10 test messages to 'tasks' topic...")
        
        partition_counts = {}
        
        def delivery_callback(err, msg):
            if not err:
                partition = msg.partition()
                partition_counts[partition] = partition_counts.get(partition, 0) + 1
        
        for i in range(10):
            producer.produce(
                'tasks',
                key=str(i).encode('utf-8'),
                value=f"test_{i}".encode('utf-8'),
                callback=delivery_callback
            )
        
        producer.flush()
        
        print(f"\n📊 Message distribution:")
        for partition, count in sorted(partition_counts.items()):
            bars = "█" * count
            print(f"   Partition {partition}: {bars} ({count} messages)")
        
        if len(partition_counts) > 1:
            print(f"\n✅ Messages distributed across {len(partition_counts)} partitions!")
            print(f"   Load balancing should work correctly.")
        else:
            print(f"\n⚠️  All messages went to 1 partition!")
            print(f"   Check if topic has multiple partitions.")
        
        return len(partition_counts) > 1
        
    except Exception as e:
        print(f"\n❌ Load balancing test failed: {e}")
        return False


def main():
    print("\n" + "🔍"*30)
    print("KAFKA LOAD BALANCING DIAGNOSTICS")
    print("🔍"*30)
    
    results = {
        "Topics": check_topics(),
        "Consumer Groups": check_consumer_groups(),
        "Load Balancing": test_load_balancing()
    }
    
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)
    
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test}")
    
    if not all(results.values()):
        print("\n" + "="*60)
        print("RECOMMENDED ACTIONS")
        print("="*60)
        create_topics_with_partitions()
    
    print("\n" + "="*60)
    print("CURRENT SYSTEM REQUIREMENTS")
    print("="*60)
    print("\n✓ For 2 workers to share load:")
    print("  • 'tasks' topic must have 2+ partitions")
    print("  • Both workers must be in 'image-workers' consumer group")
    print("  • Workers must use round-robin partition assignment")
    print("\n✓ For heartbeat monitoring:")
    print("  • Master must be subscribed to 'heartbeats' topic")
    print("  • Workers must send heartbeats every 5 seconds")
    print("  • Master heartbeat consumer should use 'earliest' offset")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
