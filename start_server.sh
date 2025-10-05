#!/bin/bash
# Script to start the Norwegian Language Learning API server

echo "🇳🇴 Starting Norwegian Language Learning API..."
echo ""

# Check if database exists, if not, seed it
if [ ! -f "norwegian_learning.db" ]; then
    echo "📊 Database not found. Seeding with sample data..."
    python3 seed_data.py
    echo ""
fi

echo "🚀 Starting FastAPI server..."
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🔍 Alternative docs: http://localhost:8000/redoc"
echo "🌐 API Root: http://localhost:8000/"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
