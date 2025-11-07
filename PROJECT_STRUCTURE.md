# 🗂️ PROJECT_STRUCTURE.md

# Project Structure - Visual Guide

```
big_data_project_ui/
│
├── 🌐 WEB APPLICATION
│   ├── app.py                      # Flask server & REST API
│   ├── templates/
│   │   ├── index.html             # Upload page (drag-drop UI)
│   │   └── dashboard.html         # Monitoring dashboard
│   └── static/                     # CSS/JS assets (empty - inline CSS used)
│
├── 🧠 MASTER NODE
│   ├── master_api.py              # Orchestration logic (NEW)
│   │   ├── Image splitting
│   │   ├── Task distribution
│   │   ├── Result collection
│   │   └── Heartbeat monitoring
│   └── master_node.py             # Standalone version (legacy)
│
├── 👷 WORKER COMPONENTS
│   ├── worker_main.py             # Worker process (processing + heartbeat)
│   ├── worker_heartbeat.py        # Standalone heartbeat sender
│   ├── consumer.py                # Kafka consumer utilities
│   ├── producer.py                # Kafka producer utilities
│   └── processor.py               # Image processing logic (blur)
│
├── 🗄️ DATABASE
│   ├── database.py                # SQLite operations (NEW)
│   │   ├── Jobs tracking
│   │   ├── Tiles management
│   │   └── Worker monitoring
│   └── image_processing.db        # SQLite database file (created at runtime)
│
├── ⚙️ CONFIGURATION
│   ├── config.py                  # Centralized settings (NEW)
│   └── requirements.txt           # Python dependencies
│
├── 📚 DOCUMENTATION
│   ├── README.md                  # Main documentation
│   ├── TESTING_GUIDE.md          # Testing procedures
│   ├── IMPLEMENTATION_SUMMARY.md # What was implemented
│   └── PROJECT_STRUCTURE.md      # This file
│
├── 🔧 SCRIPTS
│   └── setup.sh                   # Quick setup script
│
└── 📁 RUNTIME DIRECTORIES (created automatically)
    ├── uploads/                   # Uploaded images
    └── outputs/                   # Processed images
```

---

## 📊 Component Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                          │
│                    (Web Interface)                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                     app.py (Flask)                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Routes:                                               │  │
│  │ • /               → Upload page                       │  │
│  │ • /dashboard      → Monitoring                        │  │
│  │ • /api/upload     → Process image                     │  │
│  │ • /api/jobs       → List jobs                         │  │
│  │ • /api/workers    → Worker status                     │  │
│  │ • /api/stats      → System stats                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────┬────────────────────────────┬──────────────────┘
              │                            │
              ↓                            ↓
┌─────────────────────────┐    ┌─────────────────────────┐
│   master_api.py         │    │    database.py          │
│   ┌─────────────────┐   │    │   ┌─────────────────┐   │
│   │ Split image     │   │    │   │ Jobs table      │   │
│   │ Send to Kafka   │◄──┼────┼───┤ Tiles table     │   │
│   │ Collect results │   │    │   │ Workers table   │   │
│   │ Monitor workers │   │    │   └─────────────────┘   │
│   └─────────────────┘   │    └─────────────────────────┘
└────────┬────────────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────────┐
│                    KAFKA BROKER                              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ tasks       │  │ results      │  │ heartbeats   │       │
│  │ (tiles in)  │  │ (tiles out)  │  │ (worker ❤️)  │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
└────┬────────────────────┬────────────────────┬──────────────┘
     │                    │                    │
     ↓                    ↓                    ↓
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   WORKER 1       │  │   WORKER 2       │  │   WORKER N       │
│  ┌────────────┐  │  │  ┌────────────┐  │  │  ┌────────────┐  │
│  │ consumer.py│  │  │  │ consumer.py│  │  │  │ consumer.py│  │
│  │     ↓      │  │  │  │     ↓      │  │  │  │     ↓      │  │
│  │processor.py│  │  │  │processor.py│  │  │  │processor.py│  │
│  │     ↓      │  │  │  │     ↓      │  │  │  │     ↓      │  │
│  │ producer.py│  │  │  │ producer.py│  │  │  │ producer.py│  │
│  └────────────┘  │  │  └────────────┘  │  │  └────────────┘  │
│  worker_main.py  │  │  worker_main.py  │  │  worker_main.py  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## 🔄 Data Flow Diagram

```
1. IMAGE UPLOAD
   User → Flask UI → app.py → Saves to uploads/ → Returns job_id

2. TASK DISTRIBUTION
   app.py → master_api.py
                ↓
           Split image into tiles
                ↓
           Create job in database.py
                ↓
           Publish tiles to Kafka (tasks topic)

3. PARALLEL PROCESSING
   Kafka (tasks) → Worker 1 (consumer.py) → processor.py → producer.py
                → Worker 2 (consumer.py) → processor.py → producer.py
                → Worker N (consumer.py) → processor.py → producer.py
                                ↓
                    All send to Kafka (results topic)

4. RESULT COLLECTION
   Kafka (results) → master_api.py
                        ↓
                   Collect all tiles
                        ↓
                   Update database.py (progress)
                        ↓
                   Reconstruct image
                        ↓
                   Save to outputs/
                        ↓
                   Update job status = "completed"

5. HEARTBEAT MONITORING
   Worker → Kafka (heartbeats) → master_api.py → database.py
                                                      ↓
                                              Update worker status

6. DASHBOARD DISPLAY
   Browser → app.py → database.py → Return JSON
               ↓
          Dashboard updates every 2 seconds
```

---

## 📦 File Dependencies

```
app.py
├── depends on: master_api, database, Flask, werkzeug
└── imports from: master_api.process_image_async, database.*

master_api.py
├── depends on: database, consumer, producer, processor, Kafka
├── imports from: database.*, cv2, numpy, PIL
└── creates: producer, result_consumer, heartbeat_consumer

database.py
├── depends on: sqlite3, threading
└── standalone (no local imports)

worker_main.py
├── depends on: consumer, producer, processor
└── imports from: consumer.*, producer.*, processor.*

consumer.py
├── depends on: confluent_kafka
└── standalone utility

producer.py
├── depends on: confluent_kafka
└── standalone utility

processor.py
├── depends on: cv2, numpy
└── standalone utility
```

---

## 🎯 Execution Order

### For Development/Testing:

```bash
# Terminal 1: Start Flask + Master
python app.py
  ↓
  Initializes database
  Starts Flask server
  Spawns result consumer thread
  Spawns heartbeat monitor thread
  Ready to accept uploads

# Terminal 2: Start Worker 1
python worker_main.py
  ↓
  Connects to Kafka
  Subscribes to tasks topic
  Starts heartbeat thread
  Waits for tasks

# Terminal 3: Start Worker 2 (optional)
# (Edit WORKER_ID first)
python worker_main.py
  ↓
  Same as Worker 1

# Browser: Access UI
http://localhost:5000
  ↓
  Upload image
  ↓
  Monitor progress
  ↓
  Download result
```

---

## 📋 File Size Reference

| File | Lines | Purpose | Priority |
|------|-------|---------|----------|
| app.py | 160 | Web server | HIGH |
| master_api.py | 240 | Orchestration | HIGH |
| database.py | 250 | Data persistence | HIGH |
| templates/index.html | 350 | Upload UI | HIGH |
| templates/dashboard.html | 280 | Monitoring UI | HIGH |
| worker_main.py | 60 | Worker process | HIGH |
| consumer.py | 45 | Kafka consumer | MEDIUM |
| producer.py | 35 | Kafka producer | MEDIUM |
| processor.py | 25 | Image processing | MEDIUM |
| config.py | 100 | Configuration | MEDIUM |
| master_node.py | 170 | Legacy standalone | LOW |
| worker_heartbeat.py | 50 | Standalone heartbeat | LOW |

---

## 🎨 UI Pages Overview

### Page 1: Upload (index.html)
```
┌─────────────────────────────────────────────┐
│  🖼️ Distributed Image Processing            │
│  Upload images for parallel processing      │
├─────────────────────────────────────────────┤
│                                              │
│     ┌───────────────────────────────┐      │
│     │         📁 UPLOAD AREA        │      │
│     │   Click or drag and drop       │      │
│     │   PNG, JPG, JPEG, BMP          │      │
│     └───────────────────────────────┘      │
│                                              │
│     [Image Preview]                         │
│     [🚀 Process Image] [❌ Clear]           │
│                                              │
├─────────────────────────────────────────────┤
│  📋 Recent Jobs                             │
│  ┌─────────────────────────────────────┐   │
│  │ 📄 image1.jpg         [PROCESSING]   │   │
│  │ ████████░░░░░░░░░░ 45%              │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### Page 2: Dashboard (dashboard.html)
```
┌─────────────────────────────────────────────┐
│  📊 Monitoring Dashboard                     │
│  Real-time system monitoring                 │
├─────────────────────────────────────────────┤
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐       │
│  │ 📊 5 │ │ ✅ 3 │ │ ⚙️ 2 │ │ 👷 2 │       │
│  │ Jobs │ │ Done │ │ Proc │ │ Work │       │
│  └──────┘ └──────┘ └──────┘ └──────┘       │
├─────────────────────────────────────────────┤
│  💚 Worker Status                            │
│  ┌────────────────────┬──────────────────┐  │
│  │ 🤖 worker-1 ACTIVE │ 🤖 worker-2     │  │
│  │ Tasks: 45          │ Tasks: 38        │  │
│  │ Last: 2s ago       │ Last: 3s ago     │  │
│  └────────────────────┴──────────────────┘  │
├─────────────────────────────────────────────┤
│  📋 Recent Activity                          │
│  ┌───────────────────────────────────────┐  │
│  │ ✅ Job completed: image1.jpg          │  │
│  │ 🚀 New job started: image2.jpg        │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

---

## 🔐 Security Considerations

- File upload validation (type & size)
- Secure filename handling (werkzeug)
- SQL injection prevention (parameterized queries)
- Thread-safe database operations
- Input sanitization on API endpoints

---

## 🚀 Scalability Features

- Multiple workers supported
- Kafka consumer groups for load balancing
- Thread-safe operations
- Database indexing on primary keys
- Asynchronous processing
- Background task handling

---

## 💾 Storage Structure

```
Runtime Storage:
├── uploads/
│   └── {job_id}_{filename}       # Original uploaded images
├── outputs/
│   └── {job_id}_processed_{filename}  # Processed images
└── image_processing.db           # SQLite database
    ├── jobs table                # Job metadata
    ├── tiles table               # Tile status
    └── workers table             # Worker heartbeats
```

---

## 🎓 For Demonstration

### Show These Components:
1. ✅ Upload page - Drag and drop functionality
2. ✅ Dashboard - Real-time worker monitoring
3. ✅ Multi-worker processing - Parallel execution
4. ✅ Progress tracking - Live updates
5. ✅ Database - Job persistence
6. ✅ Fault tolerance - Stop/start workers

### Explain These Concepts:
1. 📚 Message queue architecture
2. 📚 Distributed processing
3. 📚 Load balancing with consumer groups
4. 📚 Heartbeat monitoring
5. 📚 Database schema design
6. 📚 RESTful API design

---

**Quick Reference for Demo:**
- Upload: `http://localhost:5000`
- Dashboard: `http://localhost:5000/dashboard`
- Start Master: `python app.py`
- Start Worker: `python worker_main.py`

---

Created: November 7, 2025
Project: Distributed Image Processing Pipeline
Course: Big Data (UE23CS343AB2)
