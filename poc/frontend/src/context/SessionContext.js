import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const SessionContext = createContext();

export const useSession = () => {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
};

export const SessionProvider = ({ children }) => {
  const [session, setSession] = useState(null);
  const [personas, setPersonas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const apiClient = axios.create({
    baseURL: 'http://localhost:8001/api',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  const createSession = async () => {
    try {
      setLoading(true);
      const response = await apiClient.post('/sessions/');
      setSession(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to create session');
      console.error('Session creation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadSession = async (sessionId) => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/sessions/${sessionId}`);
      setSession(response.data);
      setPersonas(response.data.personas || []);
      setError(null);
    } catch (err) {
      setError('Failed to load session');
      console.error('Session load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const createPersona = async (personaData) => {
    if (!session) {
      throw new Error('No active session');
    }

    try {
      setLoading(true);
      const response = await apiClient.post(
        `/sessions/${session.session_id}/personas/`,
        personaData
      );
      
      const newPersona = response.data;
      setPersonas(prev => [...prev, newPersona]);
      setError(null);
      return newPersona;
    } catch (err) {
      setError('Failed to create persona');
      console.error('Persona creation error:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const chatWithPersona = async (personaId, message) => {
    try {
      const response = await apiClient.post(`/personas/${personaId}/chat`, {
        message: message
      });
      return response.data;
    } catch (err) {
      console.error('Chat error:', err);
      throw err;
    }
  };

  const getPersonaMessages = async (personaId) => {
    try {
      const response = await apiClient.get(`/personas/${personaId}/messages`);
      return response.data;
    } catch (err) {
      console.error('Messages fetch error:', err);
      throw err;
    }
  };

  const getAvailableModels = async () => {
    try {
      const response = await apiClient.get('/models/available');
      return response.data;
    } catch (err) {
      console.error('Models fetch error:', err);
      throw err;
    }
  };

  const value = {
    session,
    personas,
    loading,
    error,
    createSession,
    loadSession,
    createPersona,
    chatWithPersona,
    getPersonaMessages,
    getAvailableModels,
  };

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  );
};