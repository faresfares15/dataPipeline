#!/bin/bash

# Cinema Data Pipeline Trigger Script
# This script runs the cinema_data_pipeline using Airflow

echo "🎬 Starting Cinema Data Pipeline..."
echo "============================================"

# Activate virtual environment
source venv/bin/activate

# Set AIRFLOW_HOME explicitly
export AIRFLOW_HOME=$(pwd)/airflow
echo "🏠 AIRFLOW_HOME: $AIRFLOW_HOME"

# Run the DAG with today's date
TODAY=$(date +%Y-%m-%d)
echo "📅 Running pipeline for date: $TODAY"
echo "⚡ Executing via Airflow..."

# Execute the DAG
airflow dags test cinema_data_pipeline $TODAY

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Pipeline completed successfully!"
    echo "🎯 Your cinema analytics are ready!"
    echo "📊 Check Elasticsearch indices:"
    echo "   - cinema_analytics_movies"
    echo "   - cinema_analytics_genres" 
    echo "   - cinema_analytics_trends"
    echo "💡 Access Kibana at: http://localhost:5601"
else
    echo ""
    echo "❌ Pipeline failed. Check the logs above."
    exit 1
fi 