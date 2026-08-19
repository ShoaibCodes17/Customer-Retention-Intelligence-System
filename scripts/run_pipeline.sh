#!/usr/bin/env bash
set -e

echo "1/5 Cleaning raw data..."
python -m src.data.clean

echo "2/5 Loading into MySQL..."
python -m src.data.load_to_db

echo "3/5 Computing RFM features..."
python -m src.features.rfm

echo "4/5 Training churn model..."
python -m src.models.train

echo "5/5 Scoring customers..."
python -m src.models.predict

echo "Pipeline complete. Run 'python -m src.api.app' to start the API + dashboard."
