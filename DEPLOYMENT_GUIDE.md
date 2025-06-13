# Cinema Data Pipeline - Deployment Guide

## 📦 **Project Overview**
Complete cinema analytics platform with Airflow, PySpark, Elasticsearch, and Kibana.

**Performance**: 20-second pipeline runtime processing 654 movies with interactive dashboards.

## 🚀 **Quick Setup for New Machine**

### **Prerequisites**
- **Windows 10/11**, macOS, or Linux
- **Python 3.8+** (Windows: ensure "Add Python to PATH" is checked during installation)
- **Docker Desktop** (Windows: WSL2 backend recommended)
- **8GB+ RAM** recommended
- **Windows-specific**: WSL2 (Windows Subsystem for Linux) may be required by Docker

### **Option 1: GitHub Clone (Recommended)**

**Windows:**
```cmd
# Clone the repository
git clone [YOUR_REPO_URL]
cd dataPipeline

# Run automated setup
python setup_windows.py

# Start Airflow (open 2 Command Prompts)
# Command Prompt 1:
venv\Scripts\activate
set AIRFLOW_HOME=%cd%\airflow
airflow webserver -p 8080

# Command Prompt 2:
venv\Scripts\activate
set AIRFLOW_HOME=%cd%\airflow
airflow scheduler
```

**macOS/Linux:**
```bash
# Clone the repository
git clone [YOUR_REPO_URL]
cd dataPipeline

# Run automated setup
chmod +x setup.sh
./setup.sh

# Start services
docker start elasticsearch
docker start kibana

# Run the pipeline
source venv/bin/activate
export AIRFLOW_HOME=$(pwd)/airflow
airflow webserver -p 8080 &
airflow scheduler &
```

### **Option 2: Direct Folder Transfer**

If sending the folder directly, **exclude these large directories**:
- `venv/` (virtual environment)
- `airflow/logs/` (log files)
- `spark-warehouse/` (temporary Spark files)
- `__pycache__/` (Python cache)
- `.git/` (if present)

**Clean folder size should be ~30MB**

## 🔧 **Step-by-Step Setup Instructions**

### **1. System Prerequisites**

**Windows:**
```cmd
# Install Python 3.8+ (if not installed)
python --version

# Install Docker Desktop (with WSL2 backend)
# Download from: https://www.docker.com/products/docker-desktop

# Verify Docker is running
docker --version

# Enable WSL2 if prompted by Docker
wsl --install
```

**macOS/Linux:**
```bash
# Install Python 3.8+ (if not installed)
python3 --version

# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop

# Verify Docker is running
docker --version
```

### **2. Project Setup**

**Windows:**
```cmd
# Navigate to project directory
cd dataPipeline

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize Airflow
set AIRFLOW_HOME=%cd%\airflow
airflow db init
```

**macOS/Linux:**
```bash
# Navigate to project directory
cd dataPipeline

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize Airflow
export AIRFLOW_HOME=$(pwd)/airflow
airflow db init
```

### **3. Start Services**

```bash
# Start Elasticsearch
docker run -d --name elasticsearch -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" -e "xpack.security.enabled=false" \
  elasticsearch:8.11.1

# Start Kibana  
docker run -d --name kibana -p 5601:5601 \
  -e "ELASTICSEARCH_HOSTS=http://host.docker.internal:9200" \
  kibana:8.11.1

# Wait 30 seconds for services to start
sleep 30

# Verify services
curl http://localhost:9200/_cluster/health
curl http://localhost:5601/api/status
```

### **4. Start Airflow**

**Windows (2 Command Prompts):**
```cmd
# Command Prompt 1: Start webserver
venv\Scripts\activate
set AIRFLOW_HOME=%cd%\airflow
airflow webserver -p 8080

# Command Prompt 2: Start scheduler
venv\Scripts\activate  
set AIRFLOW_HOME=%cd%\airflow
airflow scheduler
```

**macOS/Linux (2 Terminals):**
```bash
# Terminal 1: Start webserver
source venv/bin/activate
export AIRFLOW_HOME=$(pwd)/airflow
airflow webserver -p 8080

# Terminal 2: Start scheduler
source venv/bin/activate  
export AIRFLOW_HOME=$(pwd)/airflow
airflow scheduler
```

### **5. Run the Pipeline**

```bash
# Access Airflow UI
open http://localhost:8080

# Trigger the pipeline
# In Airflow UI: Enable "cinema_data_pipeline" DAG and trigger it
# OR via command line:
airflow dags trigger cinema_data_pipeline
```

### **6. Access Dashboards**

```bash
# Kibana dashboards
open http://localhost:5601

# The data views are pre-configured:
# - cinema_analytics_movies
# - cinema_analytics_genres  
# - cinema_analytics_trends
```

## 📊 **Expected Results**

After running the pipeline successfully:

### **Data Generated**
- **654 movie records** with ratings and categories
- **22 genre insights** with performance metrics
- **23 yearly trends** showing historical data

### **Elasticsearch Indices**
```bash
# Verify data indexing
curl "http://localhost:9200/_cat/indices?v"

# Should show:
# cinema_analytics_movies (654 docs)
# cinema_analytics_genres (22 docs)  
# cinema_analytics_trends (23 docs)
```

### **Kibana Visualizations**
1. **Movie Rating Distribution** - Bar chart by quality category
2. **Popularity Distribution** - Donut chart by popularity tier
3. **Genre Performance** - Bar chart by genre ratings
4. **Movies by Year** - Time series of movie releases

## 🔧 **Troubleshooting**

### **Common Issues**

**1. Docker not starting**
```bash
# Start Docker Desktop application first
open -a Docker
# Wait for Docker to start, then retry
```

**2. Port conflicts**

**Windows:**
```cmd
# Check what's running on ports
netstat -ano | findstr :8080   # Airflow
netstat -ano | findstr :9200   # Elasticsearch  
netstat -ano | findstr :5601   # Kibana

# Kill processes if needed
taskkill /PID [PID] /F
```

**macOS/Linux:**
```bash
# Check what's running on ports
lsof -i :8080  # Airflow
lsof -i :9200  # Elasticsearch  
lsof -i :5601  # Kibana

# Kill processes if needed
kill -9 [PID]
```

**3. Elasticsearch connection issues**
```bash
# Restart Elasticsearch
docker restart elasticsearch
sleep 20

# Check status
curl http://localhost:9200/_cluster/health
```

**4. Missing data in Kibana**
```bash
# Check Elasticsearch data
curl "http://localhost:9200/cinema_analytics_movies/_count"

# If no data, re-run pipeline
airflow dags trigger cinema_data_pipeline
```

### **Pipeline Status Check**
```bash
# Check last DAG run
airflow dags list-runs -d cinema_data_pipeline --limit 1

# View task status
airflow tasks list cinema_data_pipeline
```

## 📁 **Project Structure**

```
dataPipeline/
├── airflow/
│   ├── dags/
│   │   ├── cinema_pipeline_dag.py     # Main pipeline
│   │   └── lib/                       # Pipeline modules
├── lib/                               # Shared libraries
├── data/                              # Data lake structure
│   ├── raw/                          # Source data
│   ├── formatted/                    # Processed data
│   └── usage/                        # Analytics output
├── config.py                         # Configuration
├── requirements.txt                  # Dependencies
├── setup.sh                         # Automated setup
└── README.md                        # Project documentation
```

## 🎬 **Demo Script**

For video demonstration:

1. **Show Architecture** (2 min)
   - Project structure
   - Technology stack
   - Data flow diagram

2. **Start Services** (3 min)
   - Docker containers
   - Airflow initialization
   - Service health checks

3. **Run Pipeline** (5 min)
   - Trigger DAG execution
   - Show real-time task progress
   - Highlight 20-second runtime

4. **Show Results** (5 min)
   - Elasticsearch indices
   - Kibana data views
   - Interactive dashboards
   - Filter functionality

5. **Business Value** (2 min)
   - Analytics insights
   - Scalability discussion
   - Production readiness

## 🚀 **Production Scaling**

**To scale for production:**
1. Replace sample data with full IMDB datasets
2. Add monitoring and alerting
3. Implement authentication/authorization
4. Set up data backup and recovery
5. Configure auto-scaling

## 📞 **Support**

**If you encounter issues:**
1. Check the troubleshooting section
2. Verify all prerequisites are installed
3. Ensure Docker containers are running
4. Check Airflow logs in `airflow/logs/`

**Expected setup time: 15-20 minutes on a new machine**

Your cinema analytics platform is ready for demonstration! 🎬📊 