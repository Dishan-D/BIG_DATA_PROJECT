# Distributed Image Processing System

A distributed image processing system built with Apache Kafka, Flask, and OpenCV for parallel image transformation processing.

**Course**: Big Data (UE23CS343AB2)  
**Author**: Dishan D, Harshaa K V, Nagarjun N H, Gagan Bharadwaj
**Date**: November 2025

---

## 🏗️ System Architecture

This system implements a master-worker architecture with Kafka as the message broker:

- **Master Node** (Flask): Splits images into tiles, distributes tasks via Kafka, collects results
- **Worker Nodes**: Consume tasks from Kafka, apply image transformations, send results back
- **Kafka**: Message broker with 3 topics:
  - `tasks` (2 partitions): Image tile processing tasks
  - `results`: Processed tile results
  - `heartbeats`: Worker health monitoring

---

## 📋 Prerequisites

- Python 3.8+
- Apache Kafka broker running and accessible
- Required Python packages (see Installation)

---

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd big_data_project_ui
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Kafka broker**
   
   Update the Kafka broker IP in these files if needed:
   - `consumer.py` → `BROKER_IP`
   - `producer.py` → `BROKER_IP`
   - `master_node.py` → `BROKER_IP`
   
   Default: `172.24.52.130:9092`

4. **Initialize Kafka topics** (run once)
   ```bash
   python init_kafka_topics.py
   ```

5. **Create required directories**
   ```bash
   mkdir -p uploads outputs
   ```

---

## 🎯 Usage

### 1. Start the Master Node (Flask Server)

```bash
python app.py
```

The web interface will be available at: `http://localhost:5000`

### 2. Start Worker Nodes

In separate terminals, start 2 workers:

```bash
# Terminal 1 - Worker 1
python worker_main.py worker-1

# Terminal 2 - Worker 2
python worker_main.py worker-2
```

**Note**: You can start more workers by giving them unique IDs (worker-3, worker-4, etc.)

### 3. Process Images

1. Open `http://localhost:5000` in your browser
2. Select image transformations:
   - **Grayscale**: Convert to black & white
   - **Invert**: Color negative effect
   - **Blur**: Gaussian blur (99×99 kernel)
3. Upload an image (PNG, JPG, JPEG, or BMP)
4. View real-time processing status on the dashboard
5. Download processed image when complete

---

## 📁 Project Structure

```
big_data_project_ui/
├── app.py                    # Flask web server & REST API
├── master_api.py             # Image splitting, task distribution, result collection
├── worker_main.py            # Worker process (consumes tasks, processes tiles)
├── processor.py              # Image transformation logic (OpenCV)
├── consumer.py               # Kafka consumer configuration
├── producer.py               # Kafka producer functions
├── database.py               # SQLite database operations
├── config.py                 # Application configuration
├── worker_heartbeat.py       # Worker health monitoring
├── init_kafka_topics.py      # Kafka topic initialization script
├── requirements.txt          # Python dependencies
├── templates/
│   ├── index.html           # Upload page with transformation selector
│   └── dashboard.html       # Real-time job monitoring dashboard
├── static/                   # CSS/JS assets
├── uploads/                  # Uploaded images (created at runtime)
└── outputs/                  # Processed images (created at runtime)
```

---

## 🎨 Image Transformations

The system supports 3 image transformations that can be applied individually or combined:

1. **Grayscale** (`apply_grayscale`)
   - Converts image to black and white
   - Uses OpenCV's `cvtColor(COLOR_BGR2GRAY)`

2. **Invert** (`apply_invert`)
   - Creates color negative effect
   - Inverts all pixel values (255 - pixel_value)

3. **Blur** (`apply_gaussian_blur`)
   - Applies Gaussian blur with 99×99 kernel
   - Creates strong smoothing effect

Transformations are applied in the order selected by the user.

---

## 🔧 Configuration

### Kafka Settings

Edit `consumer.py` and `producer.py`:
- **Broker**: `BROKER_IP = "172.24.52.130:9092"`
- **Topics**: `tasks`, `results`, `heartbeats`
- **Partitions**: 2 (for `tasks` topic, enables load balancing)

### Image Processing

Edit `master_api.py`:
- **Tile Size**: `TILE_SIZE = 512` (pixels)
- **Minimum Image Size**: 1024×1024 pixels

### Flask Server

Edit `app.py`:
- **Port**: `5000`
- **Upload Folder**: `uploads/`
- **Output Folder**: `outputs/`

---

## 🗄️ Database Schema

SQLite database (`image_processing.db`) with 3 tables:

**jobs**
- `job_id` (TEXT PRIMARY KEY): Unique job identifier
- `filename` (TEXT): Original filename
- `status` (TEXT): Job status (pending/processing/completed/failed)
- `created_at` (TIMESTAMP): Creation time
- `output_path` (TEXT): Path to processed image

**tiles**
- `tile_id` (INTEGER PRIMARY KEY)
- `job_id` (TEXT): Foreign key to jobs
- `x`, `y` (INTEGER): Tile position
- `status` (TEXT): Tile status (pending/processing/completed)
- `worker_id` (TEXT): Assigned worker
- `processed_data` (TEXT): Base64 encoded result

**workers**
- `worker_id` (TEXT PRIMARY KEY)
- `status` (TEXT): Worker status (online/offline)
- `last_heartbeat` (TIMESTAMP): Last heartbeat time

---

## 🐛 Troubleshooting

### Workers can't connect to Kafka
**Error**: "No route to host" when connecting to Kafka

**Solution**: 
- Ensure you're on the correct network (college network/VPN)
- Verify Kafka broker IP: `ping 172.24.52.130`
- Check if Kafka is running on the broker server

### No results collected
**Error**: Processed images not appearing

**Solution**:
- Check worker logs for errors
- Verify workers are running: Check dashboard for heartbeats
- Restart workers to clear any stuck state

### Image size too small
**Error**: "Image too small" message

**Solution**: Upload images larger than 1024×1024 pixels

### Transformations not applied
**Error**: Processed image looks identical to input

**Solution**:
- Restart all workers to ensure latest code is loaded
- Check that transformations are selected before upload
- Verify worker logs show correct transformations

---

## 📊 Monitoring

### Dashboard (`http://localhost:5000/dashboard`)

Real-time monitoring of:
- **Active Jobs**: Current processing jobs with progress
- **Worker Health**: Online/offline status and last heartbeat
- **Job History**: Completed jobs with status

### Logs

Each component logs important events:
- **Master**: Job creation, tile distribution, result collection
- **Workers**: Task processing, transformation application, errors
- **Heartbeats**: Worker health status updates

---

## 🔐 Security Notes

- This is a development/academic project
- No authentication or authorization implemented
- Not suitable for production use without security enhancements
- Upload size limits should be configured for production

---

## 📝 License

Academic project for Big Data course at PES University.

---

## 🤝 Contributing

This is an academic project. For questions or issues, contact the author.

---

## 🙏 Acknowledgments

- Apache Kafka for distributed messaging
- Flask for web framework
- OpenCV for image processing
- PES University Big Data course instructors
