#!/bin/bash
# Start all services for development

echo "Starting Digital Clone System..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
fi

# Start signaling server
echo "Starting signaling server..."
cd apps/signaling
npm run dev &
SIGNALING_PID=$!
cd ../..

# Wait a bit for signaling to start
sleep 2

# Start AI engine
echo "Starting AI engine..."
python -m services.orchestrator.pipeline &
AI_ENGINE_PID=$!

# Wait a bit for AI engine to start
sleep 3

# Start frontend
echo "Starting frontend..."
cd apps/frontend
npm run dev &
FRONTEND_PID=$!
cd ../..

echo ""
echo "✅ All services started!"
echo "  Signaling: PID $SIGNALING_PID"
echo "  AI Engine: PID $AI_ENGINE_PID"
echo "  Frontend: PID $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $SIGNALING_PID $AI_ENGINE_PID $FRONTEND_PID; exit" INT TERM
wait

