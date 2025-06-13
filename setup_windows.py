#!/usr/bin/env python3
"""
Cinema Data Pipeline - Windows Setup Script
Automated setup for Windows machines
"""

import subprocess
import sys
import os
import time
import shutil

def run_command(command, shell=True, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=shell, cwd=cwd, 
                              capture_output=True, text=True, timeout=300)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print(f"❌ Command timed out: {command}")
        return False, "", "Timeout"
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False, "", str(e)

def check_prerequisites():
    """Check if required software is installed"""
    print("🔍 Checking prerequisites...")
    
    # Check Python
    success, stdout, stderr = run_command("python --version")
    if success and "3." in stdout:
        print(f"✅ Python: {stdout.strip()}")
    else:
        print("❌ Python 3.8+ required. Download from python.org")
        return False
    
    # Check Docker
    success, stdout, stderr = run_command("docker --version")
    if success:
        print(f"✅ Docker: {stdout.strip()}")
    else:
        print("❌ Docker required. Download Docker Desktop from docker.com")
        return False
    
    return True

def create_virtual_environment():
    """Create and set up virtual environment"""
    print("🐍 Creating virtual environment...")
    
    # Remove existing venv if present
    if os.path.exists("venv"):
        shutil.rmtree("venv")
    
    success, stdout, stderr = run_command("python -m venv venv")
    if not success:
        print(f"❌ Failed to create virtual environment: {stderr}")
        return False
    
    print("✅ Virtual environment created")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    
    # Windows activation command
    activate_cmd = "venv\\Scripts\\activate && "
    
    success, stdout, stderr = run_command(f"{activate_cmd}pip install -r requirements.txt")
    if not success:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False
    
    print("✅ Dependencies installed")
    return True

def start_docker_services():
    """Start Elasticsearch and Kibana containers"""
    print("🐳 Starting Docker services...")
    
    # Start Elasticsearch
    print("Starting Elasticsearch...")
    es_cmd = ('docker run -d --name elasticsearch -p 9200:9200 -p 9300:9300 '
              '-e "discovery.type=single-node" -e "xpack.security.enabled=false" '
              'elasticsearch:8.11.1')
    
    success, stdout, stderr = run_command(es_cmd)
    if not success and "already in use" not in stderr:
        print(f"⚠️  Elasticsearch start warning: {stderr}")
        # Try to start existing container
        run_command("docker start elasticsearch")
    
    # Start Kibana
    print("Starting Kibana...")
    kibana_cmd = ('docker run -d --name kibana -p 5601:5601 '
                  '-e "ELASTICSEARCH_HOSTS=http://host.docker.internal:9200" '
                  'kibana:8.11.1')
    
    success, stdout, stderr = run_command(kibana_cmd)
    if not success and "already in use" not in stderr:
        print(f"⚠️  Kibana start warning: {stderr}")
        # Try to start existing container
        run_command("docker start kibana")
    
    print("✅ Docker services started")
    return True

def initialize_airflow():
    """Initialize Airflow database"""
    print("✈️  Initializing Airflow...")
    
    # Set environment variable and initialize
    airflow_home = os.path.join(os.getcwd(), "airflow")
    os.environ["AIRFLOW_HOME"] = airflow_home
    
    activate_cmd = "venv\\Scripts\\activate && "
    
    success, stdout, stderr = run_command(f"{activate_cmd}airflow db init")
    if not success:
        print(f"❌ Failed to initialize Airflow: {stderr}")
        return False
    
    print("✅ Airflow initialized")
    return True

def wait_for_services():
    """Wait for services to be ready"""
    print("⏳ Waiting for services to start...")
    
    # Wait for Elasticsearch
    for i in range(12):  # 60 seconds total
        success, stdout, stderr = run_command("curl -s http://localhost:9200/_cluster/health", shell=True)
        if success:
            print("✅ Elasticsearch is ready")
            break
        time.sleep(5)
        print(f"⏳ Waiting for Elasticsearch... ({i+1}/12)")
    
    # Wait for Kibana
    for i in range(12):  # 60 seconds total
        success, stdout, stderr = run_command("curl -s http://localhost:5601/api/status", shell=True)
        if success:
            print("✅ Kibana is ready")
            break
        time.sleep(5)
        print(f"⏳ Waiting for Kibana... ({i+1}/12)")
    
    return True

def create_data_views():
    """Create Kibana data views via API"""
    print("📊 Creating Kibana data views...")
    
    data_views = [
        {
            "title": "cinema_analytics_movies",
            "timeFieldName": "timestamp"
        },
        {
            "title": "cinema_analytics_genres", 
            "timeFieldName": "timestamp"
        },
        {
            "title": "cinema_analytics_trends",
            "timeFieldName": "timestamp"
        }
    ]
    
    for dv in data_views:
        cmd = f'''curl -X POST "http://localhost:5601/api/data_views/data_view" -H "Content-Type: application/json" -H "kbn-xsrf: true" -d "{{\\"data_view\\": {{\\"title\\": \\"{dv['title']}\\", \\"timeFieldName\\": \\"{dv['timeFieldName']}\\"}}"}}"'''
        run_command(cmd)
    
    print("✅ Data views created")
    return True

def main():
    """Main setup function"""
    print("🎬 Cinema Data Pipeline - Windows Setup")
    print("=" * 50)
    
    try:
        # Check prerequisites
        if not check_prerequisites():
            print("❌ Prerequisites check failed. Please install required software.")
            return False
        
        # Create virtual environment
        if not create_virtual_environment():
            return False
        
        # Install dependencies
        if not install_dependencies():
            return False
        
        # Start Docker services
        if not start_docker_services():
            return False
        
        # Initialize Airflow
        if not initialize_airflow():
            return False
        
        # Wait for services
        if not wait_for_services():
            return False
        
        # Create data views
        create_data_views()
        
        print("\n🎉 SETUP COMPLETE!")
        print("=" * 50)
        print("📋 Next Steps:")
        print("1. Open 2 Command Prompt windows")
        print("2. In first window:")
        print("   venv\\Scripts\\activate")
        print("   set AIRFLOW_HOME=%cd%\\airflow")
        print("   airflow webserver -p 8080")
        print("3. In second window:")
        print("   venv\\Scripts\\activate") 
        print("   set AIRFLOW_HOME=%cd%\\airflow")
        print("   airflow scheduler")
        print("4. Open http://localhost:8080")
        print("5. Trigger 'cinema_data_pipeline' DAG")
        print("6. View results at http://localhost:5601")
        print("\n🚀 Your cinema analytics platform is ready!")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 