#!/usr/bin/env python3
"""
Debug script to see what's happening during formatting.
"""
import pandas as pd

# Read the sample data
df = pd.read_csv('data/raw/imdb/title_basics/20250612/title_basics_sample.tsv', sep='\t', na_values='\\N')

print(f"Original data shape: {df.shape}")
print(f"Title types: {df['titleType'].value_counts()}")
print(f"Start years: {df['startYear'].value_counts().head()}")

# Apply filters step by step
print("\nAfter titleType filter:")
df_filtered = df[df['titleType'].isin(['movie', 'tvSeries', 'short'])]
print(f"Shape: {df_filtered.shape}")

print("\nAfter startYear conversion:")
df_filtered['startYear'] = pd.to_numeric(df_filtered['startYear'], errors='coerce')
print(f"Start years after conversion: {df_filtered['startYear'].value_counts().head()}")

print("\nAfter year filter (>= 1890):")
df_final = df_filtered[df_filtered['startYear'] >= 1890]
print(f"Final shape: {df_final.shape}")

if len(df_final) > 0:
    print(f"Sample records:")
    print(df_final[['tconst', 'titleType', 'primaryTitle', 'startYear', 'genres']].head())
else:
    print("No records after filtering!")
    print("Checking for NaN values in startYear:")
    print(f"NaN count: {df_filtered['startYear'].isna().sum()}")
    print("Sample startYear values:")
    print(df_filtered['startYear'].head(10)) 