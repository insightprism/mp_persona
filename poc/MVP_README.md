# 🎭 Persona Chat System - MVP Web Interface

A React-based web interface for interacting with AI personas across multiple LLM providers (OpenAI, Claude, Ollama).

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Option 1: Use Startup Scripts (Recommended)
```bash
# Terminal 1: Start Backend
./start_backend.sh

# Terminal 2: Start Frontend (in new terminal)
./start_frontend.sh
```

### Option 2: Manual Setup

#### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Accessing the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

## 🎯 Features

### Core Functionality
✅ **Persona Creation** - Configure demographics, education, income, location  
✅ **Multi-Provider LLM Support** - OpenAI, Claude, Ollama  
✅ **Real-time Chat** - Individual conversations with personas  
✅ **Model Comparison** - Side-by-side response analysis  
✅ **Session Management** - Persistent conversations  
✅ **Cost Tracking** - Token usage and cost estimation  

### Persona Configuration
- **Demographics**: Name, age, gender, race/ethnicity
- **Background**: Education level, location type, income bracket
- **AI Model**: Provider selection (OpenAI/Claude/Ollama), model choice
- **API Keys**: Secure key management per session

### Chat Features
- **Individual Chat**: One-on-one conversations with personas
- **Multi-turn Conversations**: Persistent chat history
- **Response Metrics**: Speed, token usage, cost tracking
- **Provider Status**: Real-time availability checking

### Comparison Mode
- **Simultaneous Testing**: Send same question to multiple personas
- **Performance Metrics**: Response time, token usage, cost comparison
- **Visual Analysis**: Side-by-side response cards
- **Summary Statistics**: Aggregated performance data

## 🔧 Configuration

### API Keys
Set environment variables for the providers you want to use:

```bash
# OpenAI
export OPENAI_API_KEY="sk-your-openai-key-here"

# Claude/Anthropic
export ANTHROPIC_API_KEY="sk-ant-your-claude-key-here"

# Ollama (no key needed - local installation)
# Install: curl -fsSL https://ollama.ai/install.sh | sh
# Start: ollama serve
# Download model: ollama pull llama3:8b
```

### Provider Configuration
The system automatically detects available providers:

1. **OpenAI**: Requires API key, supports GPT-4, GPT-3.5-turbo
2. **Claude**: Requires API key, supports Claude-3-Sonnet, Claude-3-Haiku  
3. **Ollama**: No API key needed, supports local models (llama3, mistral, etc.)

## 📱 User Interface

### Main Dashboard
```
┌─────────────────────────────────────────────────────────┐
│ 🎭 Persona Chat System                   [Compare Mode] │
├─────────────────────────────────────────────────────────┤
│ [+ New Persona] Active: 2  Session: abc123...          │
├─────────────┬───────────────────────────────────────────┤
│ PERSONAS    │ CHAT / COMPARISON                         │
│             │                                           │
│ ○ Maria     │ ┌─Maria (GPT-4)──────────────────────────┐ │
│   GPT-4     │ │ 🤖 Hi! I'm Maria Rodriguez, a 34-year │ │
│   Active    │ │ old Hispanic woman living in the city. │ │
│             │ └─────────────────────────────────────────┘ │
│ ○ David     │                                           │
│   Claude    │ 👤 What's your opinion on remote work?    │
│   Inactive  │                                           │
│             │ [Type message...]              [Send]    │
└─────────────┴───────────────────────────────────────────┘
```

### Persona Builder
```
┌─────────────────────────────────────────────────────────┐
│ 🎭 Create New Persona                          [×]      │
├─────────────────────────────────────────────────────────┤
│ Name: [Maria Rodriguez        ]                         │
│ Age:  [34] Gender: [Female ▼] Race: [Hispanic ▼]       │
│ Education: [College ▼] Location: [Urban ▼]             │
│ Income: [50k-75k ▼]                                     │
│                                                         │
│ 🤖 AI Model: [OpenAI ▼] [GPT-4 ▼] [✓ Available]        │
│ API Key: [••••••••••••••••••••]                        │
│                                                         │
│                         [Cancel] [Create Persona]      │
└─────────────────────────────────────────────────────────┘
```

### Comparison View
```
┌─────────────────────────────────────────────────────────┐
│ 📊 Model Comparison                                     │
├─────────────────┬─────────────────┬───────────────────┤
│ Maria (GPT-4)   │ Maria (Claude)  │ Maria (Llama3)    │
├─────────────────┼─────────────────┼───────────────────┤
│ 🤖 Remote work  │ 🤖 I believe    │ 🤖 From my        │
│ has definitely  │ remote work     │ perspective...    │
│ changed how...  │ offers great... │                   │
│                 │                 │                   │
│ ⏱️  2.3s         │ ⏱️  1.8s         │ ⏱️  0.9s           │
│ 🎫 245 tokens   │ 🎫 198 tokens   │ 🎫 156 tokens     │
│ 💰 $0.012       │ 💰 $0.008       │ 💰 $0.000         │
└─────────────────┴─────────────────┴───────────────────┘
│ Question: [What's your opinion on remote work?]        │
│                                      [Ask All Models] │
└─────────────────────────────────────────────────────────┘
```

## 🏗️ Architecture

### Backend (FastAPI)
- **Session Management**: In-memory storage for MVP
- **Persona Creation**: Integration with existing persona system
- **Multi-Provider LLM**: Uses enhanced persona_llm_adapter
- **WebSocket Support**: Real-time chat functionality
- **API Endpoints**: RESTful API for all operations

### Frontend (React + Material-UI)
- **Component Architecture**: Modular, reusable components
- **State Management**: React Context for global state
- **Real-time Updates**: WebSocket integration
- **Responsive Design**: Mobile-friendly interface
- **Error Handling**: Graceful fallbacks and error states

### Key Components
- **PersonaBuilder**: Form-based persona configuration
- **ChatInterface**: Real-time messaging with personas
- **ComparisonView**: Side-by-side model analysis
- **SessionContext**: Global state management
- **PersonaContext**: Chat history and active persona

## 🧪 Testing the MVP

### 1. Create Your First Persona
1. Click "Create Persona"
2. Fill in demographics (Maria Rodriguez, 34, Hispanic, Female, etc.)
3. Select AI provider (OpenAI/Claude/Ollama)
4. Enter API key if required
5. Click "Create Persona"

### 2. Start Chatting
1. Select persona from left panel
2. Type message: "What's your opinion on remote work?"
3. See authentic response based on demographics
4. Continue conversation

### 3. Test Comparison Mode
1. Create 2-3 personas with different AI models
2. Click "Compare Mode" 
3. Enter question: "How do you approach financial decisions?"
4. Click "Ask All Models"
5. Compare responses, speed, and costs

### 4. Test Different Providers
- **OpenAI**: Needs API key, high quality responses
- **Claude**: Needs API key, thoughtful responses  
- **Ollama**: Local, free, good for testing

## 📊 Sample Use Cases

### Market Research
```javascript
// Create personas representing target demographics
const personas = [
  { name: "Sarah", age: 28, income: "50k_75k", location: "urban" },
  { name: "Mike", age: 45, income: "over_100k", location: "suburban" },
  { name: "Elena", age: 35, income: "25k_40k", location: "rural" }
];

// Test product concepts
const questions = [
  "What factors influence your car buying decisions?",
  "How important is environmental impact in your purchases?", 
  "What technology features do you value most?"
];
```

### Political Polling
```javascript
// Diverse demographic representation
const voterPersonas = [
  { race: "white", age: 55, education: "high_school", location: "rural" },
  { race: "black", age: 32, education: "college", location: "urban" },
  { race: "hispanic", age: 41, education: "graduate", location: "suburban" }
];

// Policy questions
const questions = [
  "What are your thoughts on healthcare policy?",
  "How do you feel about economic policies?",
  "What issues matter most to you?"
];
```

### User Experience Research
```javascript
// Tech adoption patterns
const techPersonas = [
  { age: 25, education: "college", tech_comfort: "high" },
  { age: 50, education: "high_school", tech_comfort: "medium" },
  { age: 65, education: "graduate", tech_comfort: "low" }
];

// UX testing questions
const questions = [
  "How do you typically discover new apps?",
  "What makes a website easy to use?",
  "How important is mobile optimization?"
];
```

## 🚀 Production Deployment

### Environment Setup
```bash
# Production environment variables
export NODE_ENV=production
export REACT_APP_API_BASE_URL=https://your-api-domain.com
export DATABASE_URL=postgresql://user:pass@host:port/db
export REDIS_URL=redis://host:port
```

### Deployment Options

#### Option 1: Railway/Render
- **Backend**: Deploy FastAPI to Railway/Render
- **Frontend**: Deploy React build to Vercel/Netlify
- **Database**: PostgreSQL addon
- **WebSockets**: Redis for scaling

#### Option 2: Docker
```dockerfile
# backend/Dockerfile
FROM python:3.10-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# frontend/Dockerfile  
FROM node:16-alpine
COPY . /app
WORKDIR /app
RUN npm install && npm run build
CMD ["npm", "run", "serve"]
```

#### Option 3: AWS/GCP
- **Backend**: ECS/Cloud Run
- **Frontend**: S3+CloudFront/Cloud Storage+CDN
- **Database**: RDS/Cloud SQL
- **WebSockets**: ElastiCache/Memorystore

## 🔐 Security & Privacy

### Data Protection
- **API Keys**: Stored in session memory only
- **No Persistence**: Persona data not saved to disk
- **CORS Protection**: Restricted origins
- **Input Validation**: All inputs sanitized

### Production Security
- **HTTPS Only**: SSL/TLS encryption
- **Environment Variables**: Secret management
- **Rate Limiting**: API throttling
- **Authentication**: User management system
- **Database Encryption**: Encrypted at rest

## 📈 Scaling Considerations

### Current Limitations (MVP)
- **In-Memory Storage**: Limited to single server
- **No Authentication**: Open access
- **Session Persistence**: Lost on restart
- **Concurrent Users**: ~10-50 users

### Production Scaling
- **Database**: PostgreSQL for persistence
- **Redis**: Session and WebSocket scaling
- **Load Balancing**: Multiple backend instances
- **CDN**: Static asset delivery
- **Monitoring**: Logging and metrics

## 🛠️ Development

### Adding New Features
1. **Backend**: Add FastAPI endpoints in `backend/app/routers/`
2. **Frontend**: Create React components in `frontend/src/components/`
3. **Integration**: Update context providers and API calls

### Customization
- **Themes**: Modify Material-UI theme in `App.js`
- **Providers**: Add new LLM providers to `persona_llm_adapter.py`
- **Demographics**: Extend persona fields in `PersonaBuilder.js`

### Testing
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests  
cd frontend
npm test

# Integration tests
npm run test:e2e
```

## 💰 Cost Estimates

### Development
- **Time**: 50-65 hours total
- **Skills**: React, Python, FastAPI, LLM integration

### Infrastructure (Monthly)
- **Hosting**: $15-30 (Railway/Render)
- **Database**: $5-10 (PostgreSQL) 
- **CDN**: $0-5 (Vercel/Netlify)
- **LLM APIs**: Variable based on usage

### Usage Costs
- **OpenAI**: ~$0.01-0.05 per persona response
- **Claude**: ~$0.005-0.02 per persona response
- **Ollama**: Free (local compute costs)

## 🎯 Next Steps

### Phase 2 Features
- **User Authentication**: Login/signup system
- **Persona Templates**: Pre-built demographic profiles
- **Export Functionality**: CSV/JSON data export
- **Analytics Dashboard**: Usage statistics and insights
- **Batch Testing**: Run surveys across multiple personas

### Phase 3 Enhancements  
- **Voice Integration**: Audio conversations
- **Image Generation**: Visual persona profiles
- **Advanced Analytics**: Sentiment analysis, topic modeling
- **API Access**: Third-party integrations
- **White-label**: Customizable branding

## 📞 Support

### Common Issues
1. **Port conflicts**: Change ports in config files
2. **API key errors**: Check environment variables
3. **CORS issues**: Verify allowed origins
4. **Module errors**: Run `npm install` / `pip install -r requirements.txt`

### Getting Help
- **Documentation**: Check API docs at `/docs`
- **Logs**: Check browser console and server logs
- **GitHub Issues**: Report bugs and feature requests

---

🎉 **Your MVP is ready!** Start creating personas and exploring multi-model AI conversations.