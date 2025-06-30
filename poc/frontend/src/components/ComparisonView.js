import React, { useState } from 'react';
import {
  Grid,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Card,
  CardContent,
  CardHeader,
  Avatar,
  Chip,
  CircularProgress,
  Alert,
  Divider
} from '@mui/material';
import { 
  Send, 
  Person, 
  CompareArrows,
  Timer,
  TokenIcon,
  AttachMoney
} from '@mui/icons-material';
import { useSession } from '../context/SessionContext';

const ComparisonView = ({ personas }) => {
  const { chatWithPersona } = useSession();
  const [question, setQuestion] = useState('');
  const [responses, setResponses] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAskAll = async () => {
    if (!question.trim() || personas.length === 0) return;

    setLoading(true);
    setError(null);
    setResponses({});

    try {
      // Send question to all personas simultaneously
      const promises = personas.map(async (persona) => {
        const startTime = Date.now();
        try {
          const response = await chatWithPersona(persona.id, question);
          const endTime = Date.now();
          
          return {
            persona_id: persona.id,
            persona_name: persona.name,
            provider: persona.llm_provider,
            model: persona.llm_model,
            response: response.persona_response,
            success: response.success,
            usage: response.usage,
            response_time: endTime - startTime,
            timestamp: response.timestamp,
            error: response.error
          };
        } catch (err) {
          const endTime = Date.now();
          return {
            persona_id: persona.id,
            persona_name: persona.name,
            provider: persona.llm_provider,
            model: persona.llm_model,
            response: `Error: ${err.message}`,
            success: false,
            response_time: endTime - startTime,
            error: err.message
          };
        }
      });

      const results = await Promise.all(promises);
      
      // Convert results to object keyed by persona_id
      const responseMap = results.reduce((acc, result) => {
        acc[result.persona_id] = result;
        return acc;
      }, {});
      
      setResponses(responseMap);
    } catch (err) {
      setError('Failed to send question to personas');
    } finally {
      setLoading(false);
    }
  };

  const calculateCost = (usage, provider) => {
    if (!usage || !usage.input_tokens) return 0;
    
    const costs = {
      openai: {
        input: 0.00003,  // $0.03/1k tokens
        output: 0.00006  // $0.06/1k tokens
      },
      claude: {
        input: 0.000003,  // $0.003/1k tokens
        output: 0.000015  // $0.015/1k tokens
      },
      ollama_local: {
        input: 0,
        output: 0
      }
    };
    
    const providerCosts = costs[provider] || costs.openai;
    return (usage.input_tokens * providerCosts.input) + 
           (usage.output_tokens * providerCosts.output);
  };

  const getProviderColor = (provider) => {
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
        <CompareArrows sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" color="text.secondary" gutterBottom>
          No personas available for comparison
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Create at least one persona to use comparison mode
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      {/* Question Input */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CompareArrows />
          Model Comparison
        </Typography>
        <Divider sx={{ mb: 2 }} />
        
        <Box display="flex" gap={2} alignItems="flex-end">
          <TextField
            fullWidth
            label="Question for all personas"
            multiline
            rows={2}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g., What's your opinion on remote work?"
            disabled={loading}
          />
          <Button
            variant="contained"
            onClick={handleAskAll}
            disabled={!question.trim() || loading || personas.length === 0}
            startIcon={loading ? <CircularProgress size={20} /> : <Send />}
            sx={{ whiteSpace: 'nowrap', minWidth: 120 }}
          >
            {loading ? 'Asking...' : 'Ask All'}
          </Button>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
        
        <Box display="flex" gap={1} mt={2} flexWrap="wrap">
          <Typography variant="body2" color="text.secondary">
            Testing {personas.length} personas:
          </Typography>
          {personas.map((persona) => (
            <Chip
              key={persona.id}
              label={`${persona.name} (${persona.llm_provider})`}
              size="small"
              variant="outlined"
              avatar={<Avatar sx={{ bgcolor: getProviderColor(persona.llm_provider) }}>
                <Person fontSize="small" />
              </Avatar>}
            />
          ))}
        </Box>
      </Paper>

      {/* Response Comparison Grid */}
      {Object.keys(responses).length > 0 && (
        <Grid container spacing={2}>
          {personas.map((persona) => {
            const response = responses[persona.id];
            if (!response) return null;

            return (
              <Grid item xs={12} md={6} lg={4} key={persona.id}>
                <Card sx={{ height: '100%' }}>
                  <CardHeader
                    avatar={
                      <Avatar sx={{ bgcolor: getProviderColor(persona.llm_provider) }}>
                        <Person />
                      </Avatar>
                    }
                    title={persona.name}
                    subheader={
                      <Box>
                        <Typography variant="caption" display="block">
                          {response.provider?.toUpperCase()} - {response.model}
                        </Typography>
                        <Chip
                          label={response.success ? 'Success' : 'Error'}
                          color={response.success ? 'success' : 'error'}
                          size="small"
                          sx={{ mt: 0.5 }}
                        />
                      </Box>
                    }
                  />
                  
                  <CardContent>
                    {/* Response Text */}
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        mb: 2, 
                        maxHeight: 200, 
                        overflow: 'auto',
                        bgcolor: response.success ? 'grey.50' : 'error.50',
                        p: 1,
                        borderRadius: 1
                      }}
                    >
                      {response.response}
                    </Typography>
                    
                    {/* Metrics */}
                    {response.success && (
                      <Box>
                        <Divider sx={{ mb: 1 }} />
                        <Grid container spacing={1}>
                          <Grid item xs={6}>
                            <Box display="flex" alignItems="center" gap={0.5}>
                              <Timer sx={{ fontSize: 16, color: 'text.secondary' }} />
                              <Typography variant="caption">
                                {response.response_time}ms
                              </Typography>
                            </Box>
                          </Grid>
                          
                          {response.usage && response.usage.input_tokens && (
                            <>
                              <Grid item xs={6}>
                                <Box display="flex" alignItems="center" gap={0.5}>
                                  <TokenIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                                  <Typography variant="caption">
                                    {(response.usage.input_tokens + response.usage.output_tokens)} tokens
                                  </Typography>
                                </Box>
                              </Grid>
                              
                              <Grid item xs={12}>
                                <Box display="flex" alignItems="center" gap={0.5}>
                                  <AttachMoney sx={{ fontSize: 16, color: 'text.secondary' }} />
                                  <Typography variant="caption">
                                    ~${calculateCost(response.usage, response.provider).toFixed(4)}
                                  </Typography>
                                </Box>
                              </Grid>
                            </>
                          )}
                        </Grid>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}

      {/* Summary Statistics */}
      {Object.keys(responses).length > 0 && (
        <Paper sx={{ p: 3, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Comparison Summary
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="primary">
                  {Object.values(responses).filter(r => r.success).length}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Successful Responses
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="secondary">
                  {Math.round(Object.values(responses).reduce((sum, r) => sum + r.response_time, 0) / Object.values(responses).length)}ms
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Avg Response Time
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="success.main">
                  {Object.values(responses).reduce((sum, r) => 
                    sum + (r.usage ? r.usage.input_tokens + r.usage.output_tokens : 0), 0
                  )}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Total Tokens
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="warning.main">
                  ${Object.values(responses).reduce((sum, r) => 
                    sum + calculateCost(r.usage, r.provider), 0
                  ).toFixed(4)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Total Cost
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Paper>
      )}
    </Box>
  );
};

export default ComparisonView;