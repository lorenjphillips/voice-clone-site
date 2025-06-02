#!/bin/bash

echo "🚀 Starting Imprint AI - Voice Clone & Knowledge Base System"
echo "==========================================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your OpenAI API key:"
    echo "OPENAI_API_KEY=your_key_here"
    exit 1
fi

# Check if frontend .env exists
if [ ! -f frontend/.env ]; then
    echo "Creating frontend .env file..."
    echo "VITE_API_URL=http://localhost:8000" > frontend/.env
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n🛑 Shutting down..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Application stopped"
    exit 0
}

# Set up trap for cleanup
trap cleanup SIGINT SIGTERM

# Kill any existing processes
echo "🔧 Cleaning up existing processes..."
pkill -f enhanced_api_server.py
pkill -f "npm run dev"
sleep 2

# Check if ports are available
if lsof -i :8000 > /dev/null; then
    echo "❌ Error: Port 8000 is already in use"
    exit 1
fi

if lsof -i :8080 > /dev/null; then
    echo "❌ Error: Port 8080 is already in use"
    exit 1
fi

# Start backend server
echo "🌐 Starting backend server on http://localhost:8000..."
python3 enhanced_api_server.py &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Backend is ready!"
        break
    fi
    attempt=$((attempt + 1))
    sleep 1
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Error: Backend failed to start"
    kill $BACKEND_PID
    exit 1
fi

# Start frontend server
echo "🎨 Starting frontend on http://localhost:8080..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Application started successfully!"
echo ""
echo "📋 Access the application:"
echo "   Frontend: http://localhost:8080"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🛑 To stop the application, press Ctrl+C"
echo ""

# Wait for user interrupt
wait 