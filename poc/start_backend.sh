#!/bin/bash
# Start the Persona Chat System Backend

echo "🚀 Starting Persona Chat System Backend..."

cd "$(dirname "$0")/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check for API keys
echo "🔑 Checking API keys..."
if [ -n "$OPENAI_API_KEY" ]; then
    echo "✓ OpenAI API key found"
else
    echo "⚠️  OpenAI API key not set (optional)"
fi

if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✓ Claude API key found"
else
    echo "⚠️  Claude API key not set (optional)"
fi

# Check if Ollama is running
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✓ Ollama is running locally"
else
    echo "⚠️  Ollama not running (optional)"
fi

echo ""
echo "🌐 Starting FastAPI server on http://localhost:8001"
echo "📖 API docs available at http://localhost:8001/docs"
echo "Press Ctrl+C to stop"
echo ""

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload