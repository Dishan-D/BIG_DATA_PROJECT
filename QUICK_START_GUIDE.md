# 🚀 QUICK_START_GUIDE.md

# Quick Start Guide - 5 Minutes to Running System

## ⚡ Prerequisites Check

```bash
# Check Python version (need 3.8+)
python3 --version

# Check pip
pip --version

# Verify Kafka broker is accessible
telnet 172.24.52.130 9092
# (Press Ctrl+C to exit if connection successful)
```

---

## 📦 Step 1: Install (1 minute)

```bash
# Navigate to project directory
cd ~/Documents/PES/Sem_5/BD/big_data_project_ui

# Install all dependencies
pip install -r requirements.txt
```

**Expected packages:**
- Flask
- confluent-kafka
- opencv-python
- Pillow
- numpy
- werkzeug

---

## 🗄️ Step 2: Initialize Database (10 seconds)

```bash
python database.py
```

**Expected output:**
```
✅ Database initialized successfully
```

**Created:** `image_processing.db` file

---

## ⚙️ Step 3: Configure (30 seconds)

**Update Kafka broker IP in these files:**

```bash
# Quick sed command to update all files (macOS/Linux)
BROKER_IP="YOUR_KAFKA_IP:9092"

# Or manually edit these files:
# - master_api.py (line 21)
# - consumer.py (line 4)
# - producer.py (line 4)
# - worker_main.py (line 8)
```

---

## 🎬 Step 4: Start Components (2 minutes)

### Terminal 1: Web UI + Master
```bash
python app.py
```

**Wait for:**
```
🚀 Starting Flask Web UI...
📍 Upload images at: http://localhost:5000
📊 Dashboard at: http://localhost:5000/dashboard
 * Running on http://0.0.0.0:5000
```

### Terminal 2: Worker 1
```bash
python worker_main.py
```

**Wait for:**
```
🟢 Worker subscribed to topic 'tasks'
🚀 worker-1 started (BLUR mode) and waiting for tiles...
```

### Terminal 3: Worker 2 (Optional)
```bash
# First, edit worker_main.py line 7:
# WORKER_ID = "worker-2"

python worker_main.py
```

---

## 🎯 Step 5: Test (1 minute)

### Upload an Image

1. **Open browser:** http://localhost:5000
2. **Drag and drop** an image (or click to browse)
3. **Click** "🚀 Process Image"
4. **Watch** progress bar update
5. **Click** "⬇️ Download" when complete

### Check Dashboard

1. **Open:** http://localhost:5000/dashboard
2. **Verify:**
   - Active Workers: 1 or 2
   - Processing Jobs: 1
   - Workers show green "ACTIVE" status

---

## 🎉 Success Indicators

✅ Flask shows no errors
✅ Workers show "waiting for tiles" message
✅ Dashboard shows workers as ACTIVE
✅ Upload page loads correctly
✅ Image uploads successfully
✅ Progress bar updates in real-time
✅ Processed image downloads

---

## 🐛 Quick Troubleshooting

### Problem: "Failed to connect to Kafka"
```bash
# Check Kafka broker
telnet 172.24.52.130 9092

# Verify BROKER_IP is correct
grep "BROKER_IP" master_api.py consumer.py producer.py
```

### Problem: "Import confluent_kafka could not be resolved"
```bash
# Reinstall Kafka library
pip install --upgrade confluent-kafka
```

### Problem: "Database locked"
```bash
# Delete and recreate database
rm image_processing.db
python database.py
```

### Problem: Workers not processing
```bash
# Check Kafka topics exist on broker
# (Run on Kafka broker machine)
kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Problem: Port 5000 already in use
```bash
# Find what's using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or change port in app.py (line 153)
app.run(host='0.0.0.0', port=5001)
```

---

## 📝 Command Reference

### Start Components
```bash
python app.py              # Master + Web UI
python worker_main.py      # Worker
python database.py         # Initialize DB
python config.py           # View configuration
```

### Stop Components
```
Ctrl+C                     # In each terminal
```

### Reset Database
```bash
rm image_processing.db
python database.py
```

### Clean Up Files
```bash
rm -rf uploads/* outputs/*
```

---

## 🌐 URLs

| Page | URL | Purpose |
|------|-----|---------|
| Upload | http://localhost:5000 | Upload images |
| Dashboard | http://localhost:5000/dashboard | Monitor system |
| Jobs API | http://localhost:5000/api/jobs | List all jobs |
| Stats API | http://localhost:5000/api/stats | System stats |
| Workers API | http://localhost:5000/api/workers | Worker status |

---

## 📊 API Quick Reference

```bash
# Upload image
curl -X POST -F "image=@test.jpg" http://localhost:5000/api/upload

# Get all jobs
curl http://localhost:5000/api/jobs

# Get job status
curl http://localhost:5000/api/jobs/{job_id}/status

# Get active workers
curl http://localhost:5000/api/workers/active

# Get system stats
curl http://localhost:5000/api/stats

# Download result
curl http://localhost:5000/api/jobs/{job_id}/result -o output.jpg
```

---

## 🎨 Sample Test Images

Create test images with Python:

```python
import numpy as np
import cv2

# Create 2048x2048 gradient image
img = np.zeros((2048, 2048, 3), dtype=np.uint8)
for i in range(2048):
    for j in range(2048):
        img[i, j] = [i % 256, j % 256, (i+j) % 256]

cv2.imwrite("test_image.jpg", img)
print("✅ Test image created!")
```

Or download sample images:
- https://unsplash.com/ (free high-res images)
- https://picsum.photos/2048 (random image)

---

## 📱 Demo Checklist

Before presenting:

- [ ] All dependencies installed
- [ ] Database initialized
- [ ] Kafka broker accessible
- [ ] At least 2 workers running
- [ ] Test image uploaded successfully
- [ ] Dashboard shows active workers
- [ ] Can download processed result
- [ ] Prepared to explain architecture
- [ ] Know how to demonstrate fault tolerance
- [ ] Sample images ready (1024x1024 minimum)

---

## 🎓 Key Points for Viva

**Architecture:**
- Master-worker distributed system
- Kafka for message passing
- SQLite for metadata
- Flask for web interface

**Data Flow:**
1. User uploads → Master splits → Kafka
2. Workers consume → Process → Kafka
3. Master collects → Reconstructs → User downloads

**Scaling:**
- Add more workers = faster processing
- Kafka consumer groups = automatic load balancing
- Database tracks everything

**Fault Tolerance:**
- Workers can fail and restart
- Heartbeat monitoring detects failures
- Master times out if workers unavailable
- Database persists all state

---

## ⏱️ Performance Expectations

| Image Size | Tiles | Workers | Time |
|------------|-------|---------|------|
| 1024x1024 | 4 | 1 | ~5s |
| 1024x1024 | 4 | 2 | ~3s |
| 2048x2048 | 16 | 1 | ~15s |
| 2048x2048 | 16 | 2 | ~8s |
| 4096x4096 | 64 | 2 | ~30s |

*Times are approximate and depend on network/CPU*

---

## 🆘 Emergency Commands

```bash
# Kill everything
pkill -f "python app.py"
pkill -f "python worker_main.py"

# Reset everything
rm image_processing.db
rm -rf uploads/* outputs/*
python database.py

# Fresh start
python app.py &
python worker_main.py &
```

---

## 📞 Support Files

- **Full docs:** README.md
- **Testing guide:** TESTING_GUIDE.md
- **Implementation details:** IMPLEMENTATION_SUMMARY.md
- **Architecture:** PROJECT_STRUCTURE.md
- **This file:** QUICK_START_GUIDE.md

---

## ✨ Pro Tips

1. **Use Chrome DevTools:** Network tab to see API calls
2. **Keep terminals visible:** Show parallel processing
3. **Use large images:** Better demonstrates parallelism
4. **Have backup:** Sample images and results ready
5. **Test beforehand:** Run through entire flow once

---

**That's it! You're ready to go! 🚀**

If you encounter issues not covered here, check TESTING_GUIDE.md or README.md for detailed troubleshooting.

---

Last Updated: November 7, 2025
Project: Distributed Image Processing Pipeline with Kafka
