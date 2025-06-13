#!/bin/bash

# Cinema Data Pipeline - Project Cleaner
# Removes large files and temporary data for sharing

echo "🧹 Cleaning project for sharing..."

# Remove virtual environment (largest component)
if [ -d "venv" ]; then
    echo "Removing virtual environment..."
    rm -rf venv
fi

# Remove Airflow logs and temporary files
if [ -d "airflow/logs" ]; then
    echo "Removing Airflow logs..."
    rm -rf airflow/logs/*
fi

# Remove Spark warehouse (temporary files)
if [ -d "spark-warehouse" ]; then
    echo "Removing Spark warehouse..."
    rm -rf spark-warehouse
fi

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Remove large original IMDB files if they exist
if [ -f "title.basics.tsv" ]; then
    echo "Removing large IMDB files..."
    rm -f title.basics.tsv title.ratings.tsv title.principals.tsv
    rm -f *.tsv.gz
fi

# Remove any .DS_Store files (macOS)
find . -name ".DS_Store" -delete 2>/dev/null

# Remove scheduler.log if exists
rm -f scheduler.log

# Keep only essential data - remove old dated folders
if [ -d "data" ]; then
    echo "Cleaning old data folders..."
    # Keep only the latest date folder in each category
    find data -type d -name "202*" | sort | head -n -3 | xargs rm -rf 2>/dev/null
fi

echo "✅ Project cleaned successfully!"
echo "📦 Checking final size..."
du -sh .
echo ""
echo "📋 Files to share:"
echo "- All Python code and configuration files"
echo "- Sample data and Parquet files"
echo "- Documentation and setup scripts"
echo "- Airflow DAGs and libraries"
echo ""
echo "❌ Excluded (will be regenerated):"
echo "- venv/ (virtual environment)"
echo "- airflow/logs/ (log files)"
echo "- spark-warehouse/ (temporary files)"
echo "- __pycache__/ (Python cache)"
echo ""
echo "🚀 Ready for sharing! Size should be ~30MB" 