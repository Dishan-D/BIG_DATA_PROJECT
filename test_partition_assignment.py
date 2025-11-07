#!/usr/bin/env python3
"""
Test script to verify Kafka partition assignment for multiple workers.
This simulates what happens when 2 workers join the same consumer group.
"""

import time
from confluent_kafka import Consumer
from confluent_kafka.admin import AdminClient

BROKER_IP = "172.24.52.130:9092"
TASK_TOPIC = "tasks"
GROUP_ID = "test-partition-check"

def check_topic_partitions():
    """Check how many partitions the tasks topic has."""
    admin = AdminClient({'bootstrap.servers': BROKER_IP})
    metadata = admin.list_topics(timeout=10)
    
    if TASK_TOPIC in metadata.topics:
        partitions = metadata.topics[TASK_TOPIC].partitions
        print(f"✅ Topic '{TASK_TOPIC}' has {len(partitions)} partition(s)")
        for partition_id in partitions:
            print(f"   - Partition {partition_id}: {len(partitions[partition_id].replicas)} replica(s)")
        return len(partitions)
    else:
        print(f"❌ Topic '{TASK_TOPIC}' not found!")
        return 0

def create_test_consumer(consumer_id):
    """Create a test consumer and check partition assignment."""
    consumer = Consumer({
        'bootstrap.servers': BROKER_IP,
        'group.id': GROUP_ID,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False,
        'partition.assignment.strategy': 'range',
        'session.timeout.ms': 45000,
        'heartbeat.interval.ms': 3000,
        'client.id': f'test-consumer-{consumer_id}'
    })
    
    consumer.subscribe([TASK_TOPIC])
    print(f"\n[Consumer {consumer_id}] Subscribed to '{TASK_TOPIC}'")
    print(f"[Consumer {consumer_id}] Waiting for partition assignment...")
    
    # Poll to trigger partition assignment
    for i in range(10):
        msg = consumer.poll(timeout=1.0)
        assignment = consumer.assignment()
        if assignment:
            partition_list = [tp.partition for tp in assignment]
            print(f"[Consumer {consumer_id}] ✅ Assigned to partition(s): {partition_list}")
            return consumer, partition_list
    
    print(f"[Consumer {consumer_id}] ⚠️ No partition assignment after 10 seconds")
    return consumer, []

def main():
    print("=" * 60)
    print("Kafka Partition Assignment Test")
    print("=" * 60)
    
    # Check topic configuration
    print("\n📋 Step 1: Check topic partition count")
    partition_count = check_topic_partitions()
    
    if partition_count < 2:
        print(f"\n⚠️ WARNING: Topic has only {partition_count} partition(s).")
        print("   For load balancing with 2 workers, you need 2 partitions.")
        print("\n   Run this on the Kafka broker to add partitions:")
        print(f"   kafka-topics.sh --bootstrap-server localhost:9092 \\")
        print(f"                   --alter --topic {TASK_TOPIC} --partitions 2")
        return
    
    # Create first consumer
    print(f"\n📋 Step 2: Create first consumer")
    consumer1, partitions1 = create_test_consumer(1)
    
    # Create second consumer
    print(f"\n📋 Step 3: Create second consumer")
    print("   (Kafka should now rebalance partitions...)")
    time.sleep(2)
    consumer2, partitions2 = create_test_consumer(2)
    
    # Wait for rebalance to complete
    print(f"\n⏳ Waiting 5 seconds for rebalance to stabilize...")
    time.sleep(5)
    
    # Check final assignments
    print(f"\n📊 Final Partition Assignments:")
    print("=" * 60)
    
    assignment1 = consumer1.assignment()
    assignment2 = consumer2.assignment()
    
    partitions1 = sorted([tp.partition for tp in assignment1]) if assignment1 else []
    partitions2 = sorted([tp.partition for tp in assignment2]) if assignment2 else []
    
    print(f"Consumer 1: partition(s) {partitions1}")
    print(f"Consumer 2: partition(s) {partitions2}")
    
    # Verify load balancing
    print("\n📈 Analysis:")
    if len(partitions1) > 0 and len(partitions2) > 0:
        print("✅ GOOD: Both consumers have partitions assigned!")
        print("   Load balancing should work correctly.")
    elif len(partitions1) == 0 and len(partitions2) == 0:
        print("❌ BAD: No consumers have partitions assigned!")
        print("   Check if topic exists and has partitions.")
    else:
        print("⚠️ WARNING: Only one consumer has partitions!")
        print("   This means all messages will go to one worker.")
        print("   Possible causes:")
        print("   - Consumer group is still rebalancing (wait longer)")
        print("   - Only 1 partition exists (need 2 for 2 workers)")
        print("   - Workers not in same consumer group")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    consumer1.close()
    consumer2.close()
    print("✅ Test complete!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
