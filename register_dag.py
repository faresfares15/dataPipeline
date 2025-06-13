#!/usr/bin/env python3
"""
Script to register the cinema_data_pipeline DAG in Airflow's database
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from airflow.models import DagBag
from airflow import settings

def register_dag():
    """Register the cinema data pipeline DAG in the database."""
    
    print("🔄 Registering cinema_data_pipeline DAG...")
    
    # Load DAG
    dagbag = DagBag(dag_folder='airflow/dags', include_examples=False)
    dag = dagbag.get_dag('cinema_data_pipeline')
    
    if dag:
        print('✅ DAG found in DagBag')
        
        # Import to database
        session = settings.Session()
        try:
            dag.sync_to_db(session=session)
            session.commit()
            print('✅ DAG synced to database successfully!')
            print(f'📋 DAG ID: {dag.dag_id}')
            print(f'📂 File: {dag.fileloc}')
            return True
        except Exception as e:
            print(f'❌ Error syncing DAG: {e}')
            session.rollback()
            return False
        finally:
            session.close()
    else:
        print('❌ DAG not found in DagBag')
        print('Available DAGs:', list(dagbag.dags.keys()))
        return False

if __name__ == "__main__":
    success = register_dag()
    sys.exit(0 if success else 1) 