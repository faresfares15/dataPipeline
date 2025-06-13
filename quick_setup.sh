#!/bin/bash

echo "🎬 Cinema Data Pipeline - Quick Setup"
echo "======================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Start Elasticsearch
echo "🔍 Starting Elasticsearch..."
docker run -d --name elasticsearch \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  elasticsearch:8.11.1

# Start Kibana
echo "📊 Starting Kibana..."
docker run -d --name kibana \
  -p 5601:5601 \
  -e "ELASTICSEARCH_HOSTS=http://host.docker.internal:9200" \
  kibana:8.11.1

# Wait for Elasticsearch
echo "⏳ Waiting for Elasticsearch to start..."
sleep 30

# Initialize Airflow
echo "🚁 Setting up Airflow..."
export AIRFLOW_HOME=$(pwd)/airflow
airflow db init

# Create admin user
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin \
  --quiet

echo ""
echo "✅ Setup Complete!"
echo ""
echo "🚀 Next Steps:"
echo "1. Start Airflow Webserver: export AIRFLOW_HOME=$(pwd)/airflow && airflow webserver --port 8080"
echo "2. Start Airflow Scheduler: export AIRFLOW_HOME=$(pwd)/airflow && airflow scheduler"
echo "3. Go to http://localhost:8080 (admin/admin)"
echo "4. Trigger 'cinema_data_pipeline' DAG"
echo "5. View dashboards at http://localhost:5601"
echo ""
echo "📖 Full guide: See DEPLOYMENT_GUIDE.md" 