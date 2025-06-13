# Kibana Dashboard Setup for Cinema Analytics

## Overview
This guide will help you set up Kibana dashboards to visualize the cinema analytics data that has been indexed into Elasticsearch.

## Prerequisites
- Elasticsearch running on `localhost:9200` ✅
- Cinema analytics data indexed ✅
- Kibana installed and running

## Starting Kibana

### Option 1: Docker (Recommended)
```bash
docker run -d --name kibana -p 5601:5601 -e "ELASTICSEARCH_HOSTS=http://host.docker.internal:9200" kibana:8.11.1
```

### Option 2: Local Installation
Download and start Kibana from https://www.elastic.co/downloads/kibana

## Accessing Kibana
Once Kibana is running, access it at: http://localhost:5601

## Data Views Setup (Kibana 8.x)

### ✅ Data Views Already Created!
The following data views have been automatically created for you:

1. **Movies Data View** ✅
   - Name: `cinema_analytics_movies`
   - Time field: `timestamp`
   - ID: `e39a4d32-09fa-4fbe-b142-4dbfcb60c6e7`

2. **Genres Data View** ✅
   - Name: `cinema_analytics_genres`
   - Time field: `timestamp`
   - ID: `e01e4491-11b9-4040-8234-be43e0455259`

3. **Trends Data View** ✅
   - Name: `cinema_analytics_trends`
   - Time field: `timestamp`
   - ID: `00816a60-c05c-4fe7-a1b3-5bc9491b7e4c`

### How to Find Data Views in Kibana 8.x
- **Option 1**: Go to **Stack Management** → Under "Kibana" section → **Data Views**
- **Option 2**: Go to **Discover** → Click the data view dropdown at the top
- **Option 3**: Go to **Analytics** → **Discover** → Select from data view list

## Dashboard Visualizations

### 1. Movie Analytics Dashboard

#### Top Rated Movies (Data Table)
- **Visualization Type**: Data Table
- **Index**: cinema_analytics_movies
- **Metrics**: Count
- **Buckets**: 
  - Terms: primaryTitle.keyword
  - Terms: averageRating
  - Terms: numVotes
- **Filters**: averageRating >= 8.0

#### Rating Distribution (Histogram)
- **Visualization Type**: Histogram
- **Index**: cinema_analytics_movies
- **Y-axis**: Count
- **X-axis**: averageRating (interval: 0.5)

#### Movies by Popularity Tier (Pie Chart)
- **Visualization Type**: Pie Chart
- **Index**: cinema_analytics_movies
- **Metrics**: Count
- **Buckets**: Terms on popularity_tier.keyword

### 2. Genre Analytics Dashboard

#### Genre Performance (Horizontal Bar Chart)
- **Visualization Type**: Horizontal Bar Chart
- **Index**: cinema_analytics_genres
- **Y-axis**: avg_rating
- **X-axis**: Terms on genre.keyword
- **Sort**: By avg_rating descending

#### Movies Count by Genre (Vertical Bar Chart)
- **Visualization Type**: Vertical Bar Chart
- **Index**: cinema_analytics_genres
- **Y-axis**: movie_count
- **X-axis**: Terms on genre.keyword

#### Genre Rating vs Vote Count (Scatter Plot)
- **Visualization Type**: Line Chart
- **Index**: cinema_analytics_genres
- **Y-axis**: avg_rating
- **X-axis**: avg_votes

### 3. Yearly Trends Dashboard

#### Movies Released Over Time (Line Chart)
- **Visualization Type**: Line Chart
- **Index**: cinema_analytics_trends
- **Y-axis**: movies_released
- **X-axis**: year

#### Average Rating Trends (Line Chart)
- **Visualization Type**: Line Chart
- **Index**: cinema_analytics_trends
- **Y-axis**: avg_rating
- **X-axis**: year

#### Runtime Trends (Area Chart)
- **Visualization Type**: Area Chart
- **Index**: cinema_analytics_trends
- **Y-axis**: avg_runtime
- **X-axis**: year

## Sample Queries for Discover

### High-Quality Movies
```json
{
  "query": {
    "bool": {
      "must": [
        {"range": {"averageRating": {"gte": 8.0}}},
        {"range": {"numVotes": {"gte": 1000}}}
      ]
    }
  },
  "sort": [
    {"averageRating": {"order": "desc"}},
    {"numVotes": {"order": "desc"}}
  ]
}
```

### Genre Analysis
```json
{
  "query": {"match_all": {}},
  "sort": [{"avg_rating": {"order": "desc"}}],
  "size": 50
}
```

### Recent Trends
```json
{
  "query": {
    "range": {
      "year": {"gte": 1900, "lte": 1920}
    }
  },
  "sort": [{"year": {"order": "desc"}}]
}
```

## Dashboard Layout Suggestions

### Main Cinema Analytics Dashboard
Create a single dashboard combining:
1. **Top Section**: Key metrics (total movies, avg rating, top genres)
2. **Middle Section**: Rating distribution and popularity tiers
3. **Bottom Section**: Yearly trends and genre performance

### Filters to Add
- **Time Range**: Based on timestamp
- **Rating Range**: averageRating slider
- **Vote Count**: numVotes range
- **Genre**: Multi-select dropdown
- **Year Range**: startYear slider

## Advanced Features

### 1. Alerts
Set up Watcher alerts for:
- New high-rated movies (rating > 9.0)
- Unusual voting patterns
- Data freshness monitoring

### 2. Machine Learning
Use Kibana ML to:
- Detect anomalies in rating patterns
- Forecast movie trends
- Identify outliers in genre performance

### 3. Canvas
Create executive dashboards with:
- Custom layouts
- Branded visualizations
- Export capabilities

## Data Refresh
The pipeline runs weekly and updates the Elasticsearch indices automatically. Dashboard data will refresh based on your configured refresh intervals.

## Troubleshooting

### Common Issues
1. **Index not found**: Ensure the pipeline has run successfully
2. **No data in visualizations**: Check index patterns and time ranges
3. **Performance issues**: Consider using data sampling for large datasets

### Useful Elasticsearch Queries
```bash
# Check index health
curl "http://localhost:9200/_cat/indices?v"

# Sample data from movies index
curl "http://localhost:9200/cinema_analytics_movies/_search?size=5&pretty"

# Get mapping information
curl "http://localhost:9200/cinema_analytics_movies/_mapping?pretty"
```

## Next Steps
1. Start Kibana
2. Create index patterns
3. Build visualizations
4. Combine into dashboards
5. Set up alerts and monitoring
6. Share with stakeholders

Your cinema analytics data is now ready for powerful visualizations and insights! 