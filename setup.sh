#!/bin/bash

# Cinema Data Pipeline Setup Script

echo "🎬 Setting up Cinema Data Pipeline..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create data directory structure
echo "Creating data lake directory structure..."
mkdir -p data/{raw,formatted,usage}/{imdb,omdb,analytics}/{title_basics,title_ratings,title_principals,movie_details,genre_insights,yearly_trends,director_insights}

# Set up Airflow
echo "Setting up Apache Airflow..."
export AIRFLOW_HOME=$(pwd)/airflow
mkdir -p $AIRFLOW_HOME

# Initialize Airflow database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

# Copy DAG to Airflow dags folder
mkdir -p $AIRFLOW_HOME/dags
cp dags/cinema_pipeline_dag.py $AIRFLOW_HOME/dags/

echo "✅ Setup completed!"
echo ""
echo "🚀 To start the pipeline:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start Airflow: airflow standalone"
echo "3. Open browser: http://localhost:8080"
echo "4. Login with admin/admin"
echo "5. Enable and trigger the 'cinema_data_pipeline' DAG"
echo ""
echo "📝 Don't forget to:"
echo "- Set your OMDB API key in config.py"
echo "- Start Elasticsearch if you want indexing functionality" 