# TESTING_GUIDE.md

# 🧪 Testing Guide - Distributed Image Processing Pipeline

## Pre-Testing Checklist

- [ ] Kafka broker is running and accessible
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Database initialized (`python database.py`)
- [ ] BROKER_IP configured correctly in all files
- [ ] `uploads/` and `outputs/` directories exist

## Test Scenarios

### 1. Basic Functionality Test

#### Step 1: Start the Web Application
```bash
python app.py
```

**Expected Output:**
```
✅ Database initialized successfully
🚀 Starting Flask Web UI...
📍 Upload images at: http://localhost:5000
📊 Dashboard at: http://localhost:5000/dashboard
```

#### Step 2: Start Worker 1
```bash
python worker_main.py
```

**Expected Output:**
```
🟢 Worker subscribed to topic 'tasks'
🚀 worker-1 started (BLUR mode) and waiting for tiles...
💓 Heartbeat monitoring started
```

#### Step 3: Upload Test Image
1. Open browser: http://localhost:5000
2. Upload an image (min 1024x1024)
3. Click "Process Image"

**Expected Behavior:**
- Image preview appears
- Upload success message shows
- Job appears in "Recent Jobs" section
- Progress bar updates in real-time

#### Step 4: Verify Dashboard
1. Open: http://localhost:5000/dashboard
2. Check statistics update
3. Verify worker shows as "ACTIVE"
4. Watch activity log update

**Expected Metrics:**
- Active Workers: 1
- Processing Jobs: 1
- Worker heartbeat: < 10s ago

---

### 2. Multi-Worker Test

#### Start Multiple Workers

**Terminal 1:**
```bash
python worker_main.py
```

**Terminal 2:** (Edit WORKER_ID first)
```python
# In worker_main.py, line 7:
WORKER_ID = "worker-2"
```
```bash
python worker_main.py
```

**Expected Dashboard:**
- Active Workers: 2
- Both workers visible with green "ACTIVE" status
- Tasks distributed between workers

---

### 3. Load Test

#### Upload Multiple Images Simultaneously

1. Open multiple browser tabs
2. Upload different images in each tab
3. Monitor dashboard for:
   - Multiple processing jobs
   - Worker task distribution
   - Progress tracking

**Expected:**
- All jobs process concurrently
- Workers share the load
- Each job completes successfully

---

### 4. Fault Tolerance Test

#### Test Worker Failure

1. Start 2 workers
2. Upload large image
3. Stop one worker (Ctrl+C) mid-processing
4. Observe behavior

**Expected:**
- Remaining worker continues processing
- Failed worker shows "INACTIVE" on dashboard
- Job may complete with remaining worker
- Partial completion marked if timeout occurs

#### Test Worker Recovery

1. Restart stopped worker
2. Upload new image
3. Verify worker rejoins processing

**Expected:**
- Worker shows "ACTIVE" again
- Processes new tasks normally
- Heartbeat resumes

---

### 5. Database Integrity Test

#### Verify Job Tracking

```bash
sqlite3 image_processing.db
```

```sql
-- Check jobs
SELECT job_id, filename, status, processed_tiles, total_tiles FROM jobs;

-- Check workers
SELECT worker_id, status, total_tasks_processed, last_heartbeat FROM workers;

-- Check tiles
SELECT COUNT(*) FROM tiles WHERE status = 'pending';
```

**Expected:**
- Jobs recorded correctly
- Tile counts accurate
- Worker statistics updated

---

### 6. API Endpoint Tests

#### Using curl

```bash
# Get all jobs
curl http://localhost:5000/api/jobs

# Get job status
curl http://localhost:5000/api/jobs/<job_id>/status

# Get active workers
curl http://localhost:5000/api/workers/active

# Get system stats
curl http://localhost:5000/api/stats

# Download result
curl http://localhost:5000/api/jobs/<job_id>/result -o output.jpg
```

---

### 7. Edge Cases

#### Test 1: Small Image (< 1024x1024)
- Upload 800x600 image
- **Expected:** Error message or rejection

#### Test 2: Very Large Image
- Upload 4096x4096 image
- **Expected:** 
  - Many tiles created
  - All workers participate
  - Successful completion

#### Test 3: Invalid File Type
- Upload .txt or .pdf file
- **Expected:** "Invalid file type" error

#### Test 4: No Workers Running
- Stop all workers
- Upload image
- **Expected:** 
  - Job created
  - Status: "processing"
  - Timeout after 120s
  - Status: "timeout"

#### Test 5: Network Interruption
- Start processing
- Disconnect from Kafka broker temporarily
- Reconnect

**Expected:**
- Error messages in console
- Workers retry connection
- Processing resumes when connected

---

## Performance Benchmarks

### Metrics to Collect

| Metric | 1 Worker | 2 Workers | 4 Workers |
|--------|----------|-----------|-----------|
| Time for 1024x1024 | _____s | _____s | _____s |
| Time for 2048x2048 | _____s | _____s | _____s |
| Time for 4096x4096 | _____s | _____s | _____s |
| Tiles/second | _____ | _____ | _____ |

### How to Measure

```python
# Check job start and completion times
job = get_job(job_id)
start = datetime.fromisoformat(job['created_at'])
end = datetime.fromisoformat(job['completed_at'])
duration = (end - start).total_seconds()
```

---

## Common Issues & Solutions

### Issue 1: "Failed to connect to Kafka broker"
**Solution:**
- Verify Kafka is running: `telnet <KAFKA_IP> 9092`
- Check BROKER_IP configuration
- Verify network connectivity (ZeroTier)

### Issue 2: Workers not processing
**Solution:**
- Check Kafka topics exist
- Verify consumer group configuration
- Check for errors in worker console

### Issue 3: Image not reconstructing properly
**Solution:**
- Verify all tiles received (check processed_tiles count)
- Check for tile decoding errors
- Verify tile coordinates are correct

### Issue 4: Database locked
**Solution:**
- Close all connections
- Delete `image_processing.db` and reinitialize
- Ensure only one Flask instance running

### Issue 5: High memory usage
**Solution:**
- Reduce TILE_SIZE
- Process smaller batches
- Add memory limits to workers

---

## Debugging Tips

### Enable Verbose Logging

Add to worker_main.py:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Monitor Kafka Topics

```bash
# Consumer test
kafka-console-consumer --bootstrap-server <BROKER_IP>:9092 --topic results --from-beginning

# Producer test
kafka-console-producer --bootstrap-server <BROKER_IP>:9092 --topic tasks
```

### Check Database Live

```bash
watch -n 1 'sqlite3 image_processing.db "SELECT * FROM jobs"'
```

### Monitor System Resources

```bash
# CPU and Memory
htop

# Network
iftop

# Disk I/O
iotop
```

---

## Test Report Template

```markdown
## Test Session: [Date]

### Environment
- Python Version: 
- Kafka Version: 
- Number of Workers: 
- Image Sizes Tested: 

### Test Results

| Test Case | Status | Notes |
|-----------|--------|-------|
| Basic Upload | ✅/❌ | |
| Multi-worker | ✅/❌ | |
| Load Test | ✅/❌ | |
| Fault Tolerance | ✅/❌ | |
| API Endpoints | ✅/❌ | |
| Edge Cases | ✅/❌ | |

### Performance
- Average processing time: _____ seconds
- Throughput: _____ tiles/second
- Success rate: _____ %

### Issues Found
1. 
2. 
3. 

### Recommendations
1. 
2. 
3. 
```

---

## Automated Testing Script

```bash
#!/bin/bash
# test.sh - Automated test runner

echo "🧪 Running automated tests..."

# Test 1: Database initialization
python database.py
if [ $? -eq 0 ]; then
    echo "✅ Database test passed"
else
    echo "❌ Database test failed"
fi

# Test 2: Configuration loading
python config.py
if [ $? -eq 0 ]; then
    echo "✅ Configuration test passed"
else
    echo "❌ Configuration test failed"
fi

# Test 3: Import checks
python -c "import app; import master_api; import database"
if [ $? -eq 0 ]; then
    echo "✅ Import test passed"
else
    echo "❌ Import test failed"
fi

echo "Tests complete!"
```

---

## Success Criteria

Your system passes testing if:

- ✅ All components start without errors
- ✅ Images upload successfully via web UI
- ✅ Workers process tiles and send results
- ✅ Progress updates in real-time
- ✅ Dashboard shows accurate metrics
- ✅ Processed images download correctly
- ✅ Multiple workers share load effectively
- ✅ System handles worker failures gracefully
- ✅ Database tracks all operations
- ✅ No data loss during processing

---

## Next Steps After Testing

1. Document any bugs found
2. Optimize performance based on benchmarks
3. Add additional image processing modes
4. Implement advanced monitoring features
5. Prepare demo for presentation
6. Create deployment documentation

Good luck with your testing! 🚀
