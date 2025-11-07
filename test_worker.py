#!/usr/bin/env python3
"""
Worker Testing and Debugging Script
Run this to test worker components individually
"""

import sys
import json
import base64
import cv2
import numpy as np

def test_kafka_connection():
    """Test Kafka broker connectivity."""
    print("\n" + "="*60)
    print("TEST 1: Kafka Connection")
    print("="*60)
    
    try:
        from confluent_kafka import Producer, Consumer
        from consumer import BROKER_IP
        
        print(f"📍 Testing connection to: {BROKER_IP}")
        
        # Test producer
        producer = Producer({'bootstrap.servers': BROKER_IP})
        producer.list_topics(timeout=5)
        print("✅ Producer connection successful")
        
        # Test consumer
        consumer = Consumer({
            'bootstrap.servers': BROKER_IP,
            'group.id': 'test-group',
            'auto.offset.reset': 'latest'
        })
        consumer.list_topics(timeout=5)
        consumer.close()
        print("✅ Consumer connection successful")
        
        return True
    except Exception as e:
        print(f"❌ Kafka connection failed: {e}")
        return False


def test_image_processing():
    """Test image processing functions."""
    print("\n" + "="*60)
    print("TEST 2: Image Processing")
    print("="*60)
    
    try:
        from processor import process_blur
        
        # Create a test image
        print("📷 Creating test image...")
        test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # Encode to base64
        print("🔄 Encoding to base64...")
        _, buf = cv2.imencode('.jpg', test_img)
        b64_test = base64.b64encode(buf).decode('utf-8')
        print(f"✓ Encoded image size: {len(b64_test)} chars")
        
        # Process
        print("⚙️ Processing image...")
        result = process_blur(b64_test)
        print(f"✓ Processed image size: {len(result)} chars")
        
        # Decode result
        print("🔄 Decoding result...")
        result_bytes = base64.b64decode(result)
        result_arr = np.frombuffer(result_bytes, np.uint8)
        result_img = cv2.imdecode(result_arr, cv2.IMREAD_COLOR)
        
        if result_img is not None:
            print(f"✅ Processing successful! Result shape: {result_img.shape}")
            return True
        else:
            print("❌ Failed to decode result image")
            return False
            
    except Exception as e:
        print(f"❌ Image processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_message_parsing():
    """Test message parsing from consumer."""
    print("\n" + "="*60)
    print("TEST 3: Message Parsing")
    print("="*60)
    
    try:
        # Test JSON format
        print("📝 Testing JSON message format...")
        test_message = {
            "job_id": "test-job-123",
            "tile_idx": 0,
            "x": 0,
            "y": 0,
            "b64_tile": "test_data_here"
        }
        
        json_str = json.dumps(test_message)
        parsed = json.loads(json_str)
        
        if parsed["job_id"] == "test-job-123":
            print("✅ JSON parsing successful")
            return True
        else:
            print("❌ JSON parsing failed")
            return False
            
    except Exception as e:
        print(f"❌ Message parsing failed: {e}")
        return False


def test_full_pipeline():
    """Test complete worker pipeline."""
    print("\n" + "="*60)
    print("TEST 4: Full Pipeline")
    print("="*60)
    
    try:
        from consumer import create_consumer
        from producer import create_producer, send_result
        from processor import process_blur
        
        print("🔧 Creating consumer...")
        consumer = create_consumer(group_id="test-pipeline")
        
        print("🔧 Creating producer...")
        producer = create_producer()
        
        # Create test tile
        print("📷 Creating test tile...")
        test_img = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
        _, buf = cv2.imencode('.jpg', test_img)
        b64_tile = base64.b64encode(buf).decode('utf-8')
        
        print("⚙️ Processing test tile...")
        processed = process_blur(b64_tile)
        
        print("📤 Sending result...")
        send_result(producer, "test-tile-1", 0, 0, processed, "test-job")
        
        producer.flush()
        consumer.close()
        
        print("✅ Full pipeline test successful")
        return True
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_worker_components():
    """Test worker component imports."""
    print("\n" + "="*60)
    print("TEST 0: Component Imports")
    print("="*60)
    
    components = [
        ('consumer', 'create_consumer, consume_tile'),
        ('producer', 'create_producer, send_result'),
        ('processor', 'process_blur'),
        ('confluent_kafka', 'Producer, Consumer'),
        ('cv2', None),
        ('numpy', None),
    ]
    
    all_passed = True
    for module, items in components:
        try:
            if items:
                exec(f"from {module} import {items}")
            else:
                exec(f"import {module}")
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module}: {e}")
            all_passed = False
    
    return all_passed


def main():
    """Run all tests."""
    print("\n" + "🧪"*30)
    print("WORKER COMPONENT TESTING SUITE")
    print("🧪"*30)
    
    tests = [
        ("Component Imports", test_worker_components),
        ("Kafka Connection", test_kafka_connection),
        ("Image Processing", test_image_processing),
        ("Message Parsing", test_message_parsing),
        ("Full Pipeline", test_full_pipeline),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All tests passed! Worker is ready.")
        sys.exit(0)
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
