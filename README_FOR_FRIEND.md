# 🎬 Cinema Data Pipeline - Quick Start

## 🚀 **FASTEST SETUP (5 minutes)**

### **1. Prerequisites Check**

**Windows:**
```cmd
# Verify you have these installed:
python --version   # Should be 3.8+
docker --version   # Should show Docker version
```

**macOS/Linux:**
```bash
# Verify you have these installed:
python3 --version  # Should be 3.8+
docker --version   # Should show Docker version
```

**Don't have them?**
- **Python**: Download from python.org (Windows: Check "Add Python to PATH" during installation)
- **Docker**: Download Docker Desktop from docker.com
- **Windows**: Enable WSL2 (Windows Subsystem for Linux) if prompted

### **2. One-Command Setup**

**Windows (Command Prompt):**
```cmd
# Navigate to project folder
cd dataPipeline

# Run the setup script
python setup_windows.py
```

**Windows (PowerShell):**
```powershell
# Navigate to project folder
cd dataPipeline

# Run the setup script
python setup_windows.py
```

**macOS/Linux:**
```bash
# Navigate to project folder
cd dataPipeline

# Run the magic setup script
chmod +x setup.sh
./setup.sh
```

**That's it! The script does everything:**
- ✅ Creates virtual environment
- ✅ Installs all dependencies  
- ✅ Starts Docker services
- ✅ Initializes Airflow
- ✅ Waits for services to be ready

### **3. Start the Pipeline**

**Windows (2 Command Prompts):**
```cmd
# Command Prompt 1: Start Airflow Web UI
venv\Scripts\activate
set AIRFLOW_HOME=%cd%\airflow
airflow webserver -p 8080

# Command Prompt 2: Start Airflow Scheduler  
venv\Scripts\activate
set AIRFLOW_HOME=%cd%\airflow
airflow scheduler
```

**macOS/Linux (2 Terminals):**
```bash
# Terminal 1: Start Airflow Web UI
source venv/bin/activate
export AIRFLOW_HOME=$(pwd)/airflow
airflow webserver -p 8080

# Terminal 2: Start Airflow Scheduler  
source venv/bin/activate
export AIRFLOW_HOME=$(pwd)/airflow
airflow scheduler
```

### **4. Run the Demo**
1. **Airflow UI**: http://localhost:8080
   - Find "cinema_data_pipeline" 
   - Click "Trigger DAG"
   - Watch it complete in 20 seconds! ⚡

2. **Kibana Dashboard**: http://localhost:5601
   - Go to Analytics → Dashboard
   - Explore interactive movie analytics! 📊

## 🎥 **For Your Video**

### **Perfect Demo Flow (15 minutes total):**

1. **Architecture Overview** (3 min)
   - Show project structure
   - Explain: IMDB → Airflow → Spark → Elasticsearch → Kibana

2. **Live Pipeline Run** (5 min)
   - Trigger the DAG
   - Show real-time task execution
   - Highlight 20-second completion

3. **Analytics Showcase** (7 min)
   - Open Kibana dashboards
   - Show 654 movies analyzed
   - Demonstrate interactive filters
   - Explore genre insights and trends

### **Key Talking Points:**
- **Performance**: 20-second runtime vs hours typically
- **Scale**: 654 movies, 22 genres, 23 years of data
- **Technology**: Modern data stack (Airflow, Spark, Elasticsearch)
- **Business Value**: Real-time movie analytics and insights

## 🔧 **If Something Goes Wrong**

### **Quick Fixes:**

**Windows:**
```cmd
# Services not starting?
docker restart elasticsearch kibana

# Airflow issues?
set AIRFLOW_HOME=%cd%\airflow
airflow db reset  # If needed

# Missing data?
airflow dags trigger cinema_data_pipeline

# Port conflicts?
netstat -ano | findstr :8080  # Check what's using the port
taskkill /PID [PID] /F        # Kill process if needed
```

**macOS/Linux:**
```bash
# Services not starting?
docker restart elasticsearch kibana

# Airflow issues?
export AIRFLOW_HOME=$(pwd)/airflow
airflow db reset  # If needed

# Missing data?
airflow dags trigger cinema_data_pipeline

# Port conflicts?
lsof -i :8080  # Check what's using the port
```

### **Check Everything is Working:**

**Windows:**
```cmd
# All services healthy?
curl http://localhost:9200/_cluster/health  # Elasticsearch
curl http://localhost:5601/api/status       # Kibana
curl http://localhost:8080                  # Airflow

# Data indexed?
curl "http://localhost:9200/_cat/indices?v"

# If curl not available, use PowerShell:
# Invoke-WebRequest http://localhost:9200/_cluster/health
```

**macOS/Linux:**
```bash
# All services healthy?
curl http://localhost:9200/_cluster/health  # Elasticsearch
curl http://localhost:5601/api/status       # Kibana
curl http://localhost:8080                  # Airflow

# Data indexed?
curl "http://localhost:9200/_cat/indices?v"
```

## 📊 **Expected Results**

**After successful setup:**
- **Pipeline Runtime**: ~20 seconds ⚡
- **Movies Analyzed**: 654 unique titles 🎬
- **Genres**: 22 categories 🎭
- **Visualizations**: 4 interactive dashboards 📊
- **Filters**: Real-time data filtering 🔍

## 🆘 **Need Help?**

**Check these first:**
1. Docker Desktop is running
2. All services started (wait 30 seconds)
3. Virtual environment is activated
4. Ports 8080, 9200, 5601 are free

**Still stuck?** The complete troubleshooting guide is in `DEPLOYMENT_GUIDE.md`

---

## 🎯 **TL;DR for Video**
1. Run `./setup.sh` 
2. Start Airflow webserver & scheduler
3. Trigger the pipeline at http://localhost:8080
4. Show results at http://localhost:5601
5. **Amazing 20-second cinema analytics pipeline!** 🚀

**Your friend will have a complete cinema analytics platform running in under 10 minutes!** 🎬📈 