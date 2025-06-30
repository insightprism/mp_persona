# MVP Web Interface for Persona System
## Architecture & Implementation Plan

## 🎯 MVP Features

### Core Functionality
- **Persona Configuration** - Set demographics, income, education, location
- **Model Selection** - Choose from OpenAI, Claude, Ollama models
- **Multi-Agent Chat** - Spawn multiple personas with different models
- **Side-by-Side Comparison** - Compare responses from different models
- **Session Management** - Save/load persona configurations
- **Real-time Chat** - WebSocket-based messaging

### User Interface Components
1. **Persona Builder** - Form-based persona configuration
2. **Model Selector** - Dropdown with available LLM providers/models
3. **Chat Interface** - Multi-pane chat with different personas
4. **Comparison View** - Side-by-side response analysis
5. **Configuration Panel** - Settings and API key management

## 🏗️ Technical Architecture

### Frontend (React)
```
src/
├── components/
│   ├── PersonaBuilder/
│   │   ├── PersonaForm.jsx
│   │   ├── DemographicsPanel.jsx
│   │   └── PreviewCard.jsx
│   ├── ModelSelector/
│   │   ├── ProviderSelect.jsx
│   │   ├── ModelSelect.jsx
│   │   └── ConfigPanel.jsx
│   ├── Chat/
│   │   ├── ChatContainer.jsx
│   │   ├── MessageList.jsx
│   │   ├── MessageInput.jsx
│   │   └── PersonaAvatar.jsx
│   ├── Comparison/
│   │   ├── ComparisonView.jsx
│   │   ├── ResponseCard.jsx
│   │   └── AnalysisPanel.jsx
│   └── Layout/
│       ├── Header.jsx
│       ├── Sidebar.jsx
│       └── Footer.jsx
├── hooks/
│   ├── usePersona.js
│   ├── useChat.js
│   ├── useWebSocket.js
│   └── useModels.js
├── services/
│   ├── api.js
│   ├── websocket.js
│   └── storage.js
├── utils/
│   ├── validators.js
│   └── formatters.js
└── context/
    ├── PersonaContext.js
    └── ChatContext.js
```

### Backend (FastAPI)
```
backend/
├── app/
│   ├── main.py
│   ├── models/
│   │   ├── persona.py
│   │   ├── chat.py
│   │   └── response.py
│   ├── routers/
│   │   ├── persona.py
│   │   ├── chat.py
│   │   ├── models.py
│   │   └── websocket.py
│   ├── services/
│   │   ├── persona_service.py
│   │   ├── llm_service.py
│   │   └── session_service.py
│   └── core/
│       ├── config.py
│       ├── websocket_manager.py
│       └── llm_adapter.py
└── requirements.txt
```

## 📱 User Interface Design

### 1. Main Dashboard
```
┌─────────────────────────────────────────────────────────┐
│ 🎭 Persona Chat System                    [Settings] [?] │
├─────────────────────────────────────────────────────────┤
│ [+ New Persona] [Load Config] [Compare Mode]            │
├─────────────┬───────────────────────────────────────────┤
│ PERSONAS    │ CHAT AREA                                 │
│             │                                           │
│ ┌─────────┐ │ ┌─Maria (GPT-4)─────────────────────────┐ │
│ │ Maria   │ │ │ 🤖 Hi! I'm Maria Rodriguez...         │ │
│ │ GPT-4   │ │ │                                       │ │
│ │ Active  │ │ │ 👤 What's your opinion on remote work? │ │
│ └─────────┘ │ │                                       │ │
│             │ │ 🤖 As someone living in an urban...   │ │
│ ┌─────────┐ │ └───────────────────────────────────────┘ │
│ │ David   │ │                                           │ │
│ │ Claude  │ │ [Type your message...]           [Send]  │ │
│ │ Inactive│ │                                           │ │
│ └─────────┘ │                                           │ │
└─────────────┴───────────────────────────────────────────┘
```

### 2. Persona Builder Modal
```
┌─────────────────────────────────────────────────────────┐
│ 🎭 Create New Persona                          [×]      │
├─────────────────────────────────────────────────────────┤
│ Name: [Maria Rodriguez        ]                         │
│ Age:  [34] Gender: [Female ▼] Race: [Hispanic ▼]       │
│ Education: [College ▼] Location: [Urban ▼]             │
│ Income: [50k-75k ▼] Job: [Administrative ▼]            │
│                                                         │
│ 🤖 AI Model Configuration                               │
│ Provider: [OpenAI ▼] Model: [GPT-4 ▼]                  │
│ Temperature: [0.8] [████████░░]                         │
│                                                         │
│ 🎨 Visual Assets                                        │
│ [Generate Image] [Generate Voice] [Preview]             │
│                                                         │
│                         [Cancel] [Create Persona]      │
└─────────────────────────────────────────────────────────┘
```

### 3. Comparison Mode
```
┌─────────────────────────────────────────────────────────┐
│ 📊 Model Comparison View                               │
├─────────────────┬─────────────────┬───────────────────┤
│ Maria (GPT-4)   │ Maria (Claude)  │ Maria (Llama3)    │
├─────────────────┼─────────────────┼───────────────────┤
│ 🤖 As someone   │ 🤖 *speaking   │ 🤖 Hola! Remote   │
│ living in an    │ as Maria* I     │ work has really   │
│ urban area...   │ think remote... │ changed things... │
│                 │                 │                   │
│ 📊 Response:    │ 📊 Response:    │ 📊 Response:      │
│ - Speed: 2.3s   │ - Speed: 1.8s   │ - Speed: 0.9s     │
│ - Tokens: 245   │ - Tokens: 198   │ - Tokens: 156     │
│ - Cost: $0.012  │ - Cost: $0.008  │ - Cost: $0.000    │
└─────────────────┴─────────────────┴───────────────────┘
│ Question: [What's your opinion on remote work?]        │
│                                      [Ask All Models] │
└─────────────────────────────────────────────────────────┘
```

## 🛠️ Implementation Steps

### Phase 1: Backend API (Week 1)
1. **FastAPI Setup**
   ```python
   # app/main.py
   from fastapi import FastAPI, WebSocket
   from fastapi.middleware.cors import CORSMiddleware
   
   app = FastAPI(title="Persona Chat API")
   app.add_middleware(CORSMiddleware, allow_origins=["*"])
   ```

2. **Persona Management API**
   ```python
   # app/routers/persona.py
   @router.post("/personas/")
   async def create_persona(persona_data: PersonaCreate):
       # Validate and create persona
       return {"id": "persona_123", "status": "created"}
   
   @router.get("/personas/{persona_id}")
   async def get_persona(persona_id: str):
       # Return persona configuration
   
   @router.post("/personas/{persona_id}/chat")
   async def chat_with_persona(persona_id: str, message: ChatMessage):
       # Send message to persona and get response
   ```

3. **WebSocket for Real-time Chat**
   ```python
   # app/routers/websocket.py
   @router.websocket("/ws/{session_id}")
   async def websocket_endpoint(websocket: WebSocket, session_id: str):
       await websocket.accept()
       # Handle real-time chat messages
   ```

4. **Model Provider Integration**
   ```python
   # app/services/llm_service.py
   class LLMService:
       async def get_available_models(self):
           return {
               "openai": ["gpt-4", "gpt-3.5-turbo"],
               "claude": ["claude-3-sonnet", "claude-3-haiku"],
               "ollama": ["llama3:8b", "mistral:7b"]
           }
       
       async def chat_with_model(self, provider, model, messages):
           # Use existing persona_llm_adapter
   ```

### Phase 2: React Frontend (Week 2)
1. **Project Setup**
   ```bash
   npx create-react-app persona-chat-ui
   cd persona-chat-ui
   npm install @mui/material @emotion/react @emotion/styled
   npm install socket.io-client axios react-router-dom
   ```

2. **Persona Builder Component**
   ```jsx
   // src/components/PersonaBuilder/PersonaForm.jsx
   import { useState } from 'react';
   import { TextField, Select, Button, Grid } from '@mui/material';
   
   export const PersonaForm = ({ onSubmit }) => {
     const [persona, setPersona] = useState({
       name: '', age: '', gender: '', race_ethnicity: '',
       education: '', location_type: '', income: ''
     });
     
     const handleSubmit = () => {
       onSubmit(persona);
     };
     
     return (
       <Grid container spacing={2}>
         <Grid item xs={6}>
           <TextField label="Name" value={persona.name} 
                     onChange={(e) => setPersona({...persona, name: e.target.value})} />
         </Grid>
         {/* More fields... */}
       </Grid>
     );
   };
   ```

3. **Chat Interface**
   ```jsx
   // src/components/Chat/ChatContainer.jsx
   import { useState, useEffect } from 'react';
   import { useWebSocket } from '../hooks/useWebSocket';
   
   export const ChatContainer = ({ personas }) => {
     const [messages, setMessages] = useState({});
     const [activePersona, setActivePersona] = useState(null);
     const { sendMessage, lastMessage } = useWebSocket();
     
     useEffect(() => {
       if (lastMessage) {
         const { persona_id, response } = JSON.parse(lastMessage);
         setMessages(prev => ({
           ...prev,
           [persona_id]: [...(prev[persona_id] || []), response]
         }));
       }
     }, [lastMessage]);
     
     return (
       <div className="chat-container">
         <PersonaList personas={personas} onSelect={setActivePersona} />
         <MessageList messages={messages[activePersona?.id] || []} />
         <MessageInput onSend={(msg) => sendMessage(activePersona.id, msg)} />
       </div>
     );
   };
   ```

4. **Model Comparison View**
   ```jsx
   // src/components/Comparison/ComparisonView.jsx
   export const ComparisonView = ({ personas, question }) => {
     const [responses, setResponses] = useState({});
     
     const askAllModels = async () => {
       const promises = personas.map(persona => 
         api.chatWithPersona(persona.id, question)
       );
       const results = await Promise.all(promises);
       setResponses(results.reduce((acc, result, index) => ({
         ...acc,
         [personas[index].id]: result
       }), {}));
     };
     
     return (
       <div className="comparison-grid">
         {personas.map(persona => (
           <ResponseCard 
             key={persona.id}
             persona={persona}
             response={responses[persona.id]}
           />
         ))}
       </div>
     );
   };
   ```

### Phase 3: Integration & Features (Week 3)
1. **WebSocket Integration**
   ```jsx
   // src/hooks/useWebSocket.js
   import { useEffect, useState } from 'react';
   import io from 'socket.io-client';
   
   export const useWebSocket = (sessionId) => {
     const [socket, setSocket] = useState(null);
     const [lastMessage, setLastMessage] = useState(null);
     
     useEffect(() => {
       const newSocket = io(`ws://localhost:8000/ws/${sessionId}`);
       newSocket.on('message', setLastMessage);
       setSocket(newSocket);
       
       return () => newSocket.close();
     }, [sessionId]);
     
     const sendMessage = (personaId, message) => {
       socket.emit('chat', { persona_id: personaId, message });
     };
     
     return { sendMessage, lastMessage };
   };
   ```

2. **State Management**
   ```jsx
   // src/context/PersonaContext.js
   import { createContext, useContext, useReducer } from 'react';
   
   const PersonaContext = createContext();
   
   export const PersonaProvider = ({ children }) => {
     const [state, dispatch] = useReducer(personaReducer, initialState);
     
     const createPersona = (personaData) => {
       dispatch({ type: 'CREATE_PERSONA', payload: personaData });
     };
     
     return (
       <PersonaContext.Provider value={{ ...state, createPersona }}>
         {children}
       </PersonaContext.Provider>
     );
   };
   ```

3. **API Service Layer**
   ```jsx
   // src/services/api.js
   import axios from 'axios';
   
   const api = axios.create({
     baseURL: 'http://localhost:8000/api'
   });
   
   export const personaAPI = {
     create: (data) => api.post('/personas/', data),
     get: (id) => api.get(`/personas/${id}`),
     chat: (id, message) => api.post(`/personas/${id}/chat`, { message }),
     getModels: () => api.get('/models/available')
   };
   ```

## 🚀 Deployment & Hosting

### Development Setup
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend  
cd frontend
npm install
npm start  # Runs on port 3000
```

### Production Deployment
- **Frontend**: Deploy to Vercel/Netlify
- **Backend**: Deploy to Railway/Render/AWS
- **Database**: PostgreSQL for session storage
- **WebSockets**: Redis for scaling

## 💰 Cost Estimation

### Development Time
- **Backend API**: 15-20 hours
- **React Frontend**: 25-30 hours  
- **Integration & Testing**: 10-15 hours
- **Total**: ~50-65 hours

### Infrastructure Costs (Monthly)
- **Hosting**: $10-20 (Railway/Render)
- **Database**: $5-10 (PostgreSQL)
- **LLM APIs**: Variable based on usage
- **Total**: $15-30/month + API costs

## 🎯 Key Success Metrics

1. **User Experience**
   - Persona creation time < 2 minutes
   - Chat response time < 3 seconds
   - Side-by-side comparison functionality

2. **Technical Performance**  
   - Support 10+ concurrent personas
   - WebSocket connection stability
   - Cross-model response accuracy

3. **Feature Completeness**
   - All demographic configurations
   - 3+ LLM provider support
   - Session save/restore
   - Real-time chat experience

This MVP provides a solid foundation for expanding into a full-featured persona research platform!