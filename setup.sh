#!/bin/bash
# Quick Start Script for Distributed Image Processing Pipeline

echo "🚀 Starting Distributed Image Processing Pipeline"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "🗄️ Initializing database..."
python database.py

# Create necessary directories
mkdir -p uploads outputs

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Update BROKER_IP in configuration files"
echo "2. Start Kafka broker (on remote server)"
echo "3. Run: python app.py (to start web UI)"
echo "4. Run: python worker_main.py (in separate terminals for each worker)"
echo ""
echo "🌐 Access the application at: http://localhost:5000"
echo "📊 Dashboard available at: http://localhost:5000/dashboard"
