# 🖼️ Distributed Image Processing Pipeline with Kafka

A complete distributed system for processing large images using Apache Kafka, featuring parallel processing, real-time monitoring, and a web interface.

## 🎯 Features

- ✅ **Web UI** - Upload images and view results via Flask web interface
- ✅ **Distributed Processing** - Multiple workers process image tiles in parallel
- ✅ **Kafka Integration** - Reliable message passing for task distribution
- ✅ **Real-time Monitoring** - Dashboard showing worker status and job progress
- ✅ **Metadata Tracking** - SQLite database for job and worker tracking
- ✅ **Heartbeat System** - Automatic worker health monitoring
- ✅ **Progress Tracking** - Real-time progress updates for each job

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │  (Web Browser)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Flask App   │  (Upload & Dashboard)
│ + Master    │  (Image splitting & reconstruction)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Kafka    │  (Message Broker)
│   Broker    │  - tasks topic
│             │  - results topic
│             │  - heartbeats topic
└──────┬──────┘
       │
       ▼
┌─────────────┬─────────────┐
│  Worker 1   │  Worker 2   │
│ (Process)   │ (Process)   │
└─────────────┴─────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- Apache Kafka (running on broker)
- ZeroTier or network connectivity to Kafka broker

## 🚀 Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Kafka Broker IP

Update the `BROKER_IP` in the following files:
- `master_api.py`
- `consumer.py`
- `producer.py`
- `worker_main.py`
- `worker_heartbeat.py`

```python
BROKER_IP = "YOUR_KAFKA_IP:9092"  # e.g., "172.24.52.130:9092"
```

### 3. Initialize Database

```bash
python database.py
```

## 🎮 Usage

### Starting the System

#### 1. Start the Web UI & Master Node

```bash
python app.py
```

Access the application at:
- **Upload Page**: http://localhost:5000
- **Dashboard**: http://localhost:5000/dashboard

#### 2. Start Worker Nodes

Open separate terminals for each worker:

**Worker 1:**
```bash
python worker_main.py
```

**Worker 2:**
Edit `worker_main.py` to set `WORKER_ID = "worker-2"`, then:
```bash
python worker_main.py
```

### Using the Web Interface

1. **Upload Image**
   - Go to http://localhost:5000
   - Click or drag-and-drop an image (min 1024x1024)
   - Click "Process Image"

2. **Monitor Progress**
   - View real-time progress on the upload page
   - Check detailed metrics on the dashboard

3. **Download Results**
   - Click "Download" button when processing completes
   - Processed image will be downloaded automatically

## 📁 Project Structure

```
.
├── app.py                 # Flask web application
├── master_api.py          # Master node logic (task distribution & collection)
├── database.py            # SQLite database operations
├── worker_main.py         # Worker node implementation
├── consumer.py            # Kafka consumer utilities
├── producer.py            # Kafka producer utilities
├── processor.py           # Image processing logic (blur)
├── worker_heartbeat.py    # Standalone heartbeat sender
├── master_node.py         # Original standalone master (legacy)
├── templates/
│   ├── index.html        # Upload page UI
│   └── dashboard.html    # Monitoring dashboard UI
├── uploads/              # Uploaded images
├── outputs/              # Processed images
└── requirements.txt      # Python dependencies
```

## 🗄️ Database Schema

### Jobs Table
Tracks image processing jobs with status, progress, and metadata.

### Tiles Table
Tracks individual tile processing status.

### Workers Table
Stores worker heartbeats and task counts.

## 🔧 Configuration

### Tile Size
Default: 512x512 pixels. Can be adjusted in `master_api.py`:
```python
TILE_SIZE = 512
```

### Processing Timeout
Default: 120 seconds. Adjust in `master_api.py`:
```python
WAIT_TIMEOUT = 120
```

### Heartbeat Interval
Default: 5 seconds. Adjust in `worker_main.py`:
```python
HEARTBEAT_INTERVAL = 5
```

## 📊 API Endpoints

### Jobs
- `POST /api/upload` - Upload and process image
- `GET /api/jobs` - List all jobs
- `GET /api/jobs/<job_id>/status` - Get job progress
- `GET /api/jobs/<job_id>/result` - Download processed image

### Workers
- `GET /api/workers` - List all workers
- `GET /api/workers/active` - List active workers

### Stats
- `GET /api/stats` - Get system statistics

## 🎨 Image Processing

Currently implements **Gaussian Blur** with a 51x51 kernel. To change processing:

Edit `processor.py`:
```python
def process_blur(b64_tile):
    # Your custom processing here
    # Example: Grayscale conversion
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
```

## 🐛 Troubleshooting

### Kafka Connection Issues
- Verify Kafka broker is running
- Check `BROKER_IP` configuration
- Test network connectivity: `telnet <KAFKA_IP> 9092`

### Workers Not Processing
- Check worker console for errors
- Verify Kafka topics exist: `tasks`, `results`, `heartbeats`
- Ensure consumer group is properly configured

### Database Errors
- Delete `image_processing.db` and run `python database.py`
- Check file permissions

## 📈 Performance Tips

1. **More Workers**: Run multiple worker instances for faster processing
2. **Smaller Tiles**: Reduce `TILE_SIZE` for better parallelization (but more overhead)
3. **Kafka Partitions**: Configure Kafka with partitions matching worker count
4. **Network**: Use local network or high-speed connection for large images

## 🎓 Project Requirements Checklist

- ✅ Master node with tiling and reconstruction
- ✅ Worker nodes with Kafka integration
- ✅ Kafka broker with 3 topics
- ✅ Flask web UI with upload
- ✅ Real-time monitoring dashboard
- ✅ SQLite metadata storage
- ✅ Heartbeat monitoring
- ✅ Progress tracking
- ✅ Job status display

## 📝 License

This project is for educational purposes (PES University - Big Data Course).

## 👥 Contributors

- Your Team Members Here

## 🙏 Acknowledgments

- Apache Kafka
- Flask Framework
- OpenCV Library
- PES University BD Course
