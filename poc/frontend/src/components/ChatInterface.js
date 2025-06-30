import React, { useState, useEffect, useRef } from 'react';
import {
  Grid,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemAvatar,
  Avatar,
  TextField,
  IconButton,
  Box,
  Chip,
  Alert,
  CircularProgress,
  Divider
} from '@mui/material';
import { 
  Send, 
  Person, 
  SmartToy, 
  Circle 
} from '@mui/icons-material';
import { useSession } from '../context/SessionContext';
import { usePersona } from '../context/PersonaContext';

const ChatInterface = ({ personas }) => {
  const { chatWithPersona } = useSession();
  const { activePersona, setActivePersona, chatHistory, addMessage } = usePersona();
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory, activePersona]);

  const handlePersonaSelect = (persona) => {
    setActivePersona(persona);
    setError(null);
  };

  const handleSendMessage = async () => {
    if (!message.trim() || !activePersona || sending) return;

    const userMessage = {
      type: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };

    // Add user message to history
    addMessage(activePersona.id, userMessage);
    setMessage('');
    setSending(true);
    setError(null);

    try {
      const response = await chatWithPersona(activePersona.id, message);
      
      const assistantMessage = {
        type: 'assistant',
        content: response.persona_response,
        timestamp: response.timestamp,
        provider: response.provider,
        usage: response.usage,
        success: response.success
      };

      addMessage(activePersona.id, assistantMessage);
    } catch (err) {
      setError('Failed to send message');
      console.error('Chat error:', err);
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const getPersonaColor = (provider) => {
    const colors = {
      openai: '#00a67e',
      claude: '#d97706',
      ollama_local: '#8b5cf6',
      mock: '#6b7280'
    };
    return colors[provider] || '#6b7280';
  };

  if (personas.length === 0) {
    return (
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <SmartToy sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" color="text.secondary" gutterBottom>
          No personas created yet
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Create your first persona to start chatting!
        </Typography>
      </Paper>
    );
  }

  return (
    <Grid container spacing={2} sx={{ height: 'calc(100vh - 200px)' }}>
      {/* Persona List */}
      <Grid item xs={12} md={3}>
        <Paper sx={{ height: '100%', overflow: 'hidden' }}>
          <Box sx={{ p: 2, bgcolor: 'primary.main', color: 'white' }}>
            <Typography variant="h6">Personas</Typography>
          </Box>
          <List sx={{ overflow: 'auto', height: 'calc(100% - 64px)' }}>
            {personas.map((persona) => (
              <ListItem key={persona.id} disablePadding>
                <ListItemButton
                  selected={activePersona?.id === persona.id}
                  onClick={() => handlePersonaSelect(persona)}
                >
                  <ListItemAvatar>
                    <Avatar sx={{ bgcolor: getPersonaColor(persona.llm_provider) }}>
                      <Person />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={persona.name}
                    secondary={
                      <Box>
                        <Typography variant="caption" display="block">
                          {persona.llm_provider?.toUpperCase()} - {persona.llm_model}
                        </Typography>
                        <Box display="flex" alignItems="center" gap={0.5} mt={0.5}>
                          <Circle 
                            sx={{ 
                              fontSize: 8, 
                              color: persona.status === 'active' ? 'success.main' : 'error.main' 
                            }} 
                          />
                          <Typography variant="caption" color="text.secondary">
                            {persona.status}
                          </Typography>
                        </Box>
                      </Box>
                    }
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Paper>
      </Grid>

      {/* Chat Area */}
      <Grid item xs={12} md={9}>
        <Paper sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          {activePersona ? (
            <>
              {/* Chat Header */}
              <Box sx={{ p: 2, bgcolor: 'grey.50', borderBottom: 1, borderColor: 'grey.200' }}>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box display="flex" alignItems="center" gap={2}>
                    <Avatar sx={{ bgcolor: getPersonaColor(activePersona.llm_provider) }}>
                      <Person />
                    </Avatar>
                    <Box>
                      <Typography variant="h6">{activePersona.name}</Typography>
                      <Box display="flex" gap={1}>
                        <Chip 
                          label={activePersona.llm_provider?.toUpperCase()} 
                          size="small" 
                          variant="outlined"
                        />
                        <Chip 
                          label={activePersona.llm_model} 
                          size="small" 
                          variant="outlined"
                        />
                      </Box>
                    </Box>
                  </Box>
                </Box>
              </Box>

              {/* Messages */}
              <Box sx={{ flex: 1, overflow: 'auto', p: 1 }}>
                {error && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                  </Alert>
                )}
                
                {chatHistory[activePersona.id]?.map((msg, index) => (
                  <Box
                    key={index}
                    sx={{
                      display: 'flex',
                      justifyContent: msg.type === 'user' ? 'flex-end' : 'flex-start',
                      mb: 1
                    }}
                  >
                    <Paper
                      sx={{
                        p: 2,
                        maxWidth: '70%',
                        bgcolor: msg.type === 'user' ? 'primary.main' : 'grey.100',
                        color: msg.type === 'user' ? 'white' : 'text.primary'
                      }}
                    >
                      <Typography variant="body1">
                        {msg.content}
                      </Typography>
                      <Typography 
                        variant="caption" 
                        sx={{ 
                          opacity: 0.7, 
                          display: 'block', 
                          mt: 0.5 
                        }}
                      >
                        {new Date(msg.timestamp).toLocaleTimeString()}
                        {msg.provider && ` • ${msg.provider}`}
                        {msg.usage?.input_tokens && ` • ${msg.usage.input_tokens + msg.usage.output_tokens} tokens`}
                      </Typography>
                    </Paper>
                  </Box>
                ))}
                
                {sending && (
                  <Box display="flex" justifyContent="flex-start" mb={1}>
                    <Paper sx={{ p: 2, bgcolor: 'grey.100' }}>
                      <Box display="flex" alignItems="center" gap={1}>
                        <CircularProgress size={16} />
                        <Typography variant="body2" color="text.secondary">
                          {activePersona.name} is thinking...
                        </Typography>
                      </Box>
                    </Paper>
                  </Box>
                )}
                
                <div ref={messagesEndRef} />
              </Box>

              {/* Message Input */}
              <Box sx={{ p: 2, borderTop: 1, borderColor: 'grey.200' }}>
                <Box display="flex" gap={1}>
                  <TextField
                    fullWidth
                    multiline
                    maxRows={3}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={`Message ${activePersona.name}...`}
                    disabled={sending}
                  />
                  <IconButton
                    color="primary"
                    onClick={handleSendMessage}
                    disabled={!message.trim() || sending}
                  >
                    <Send />
                  </IconButton>
                </Box>
              </Box>
            </>
          ) : (
            <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Box textAlign="center">
                <SmartToy sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  Select a persona to start chatting
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Choose a persona from the left panel to begin your conversation
                </Typography>
              </Box>
            </Box>
          )}
        </Paper>
      </Grid>
    </Grid>
  );
};

export default ChatInterface;