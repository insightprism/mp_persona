#!/bin/bash
# Start the Persona Chat System Frontend

echo "🎨 Starting Persona Chat System Frontend..."

cd "$(dirname "$0")/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

echo ""
echo "🌐 Starting React development server on http://localhost:3000"
echo "🔗 Backend should be running on http://localhost:8001"
echo "Press Ctrl+C to stop"
echo ""

# Start the React development server
npm start