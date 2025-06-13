#!/bin/bash

# This script mimics: source venv/bin/activate && airflow dags trigger cinema_data_pipeline
# But uses the working 'test' approach instead of 'trigger'

source venv/bin/activate && export AIRFLOW_HOME=$(pwd)/airflow && airflow dags test cinema_data_pipeline $(date +%Y-%m-%d) 