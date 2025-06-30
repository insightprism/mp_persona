import React, { createContext, useContext, useState } from 'react';

const PersonaContext = createContext();

export const usePersona = () => {
  const context = useContext(PersonaContext);
  if (!context) {
    throw new Error('usePersona must be used within a PersonaProvider');
  }
  return context;
};

export const PersonaProvider = ({ children }) => {
  const [activePersona, setActivePersona] = useState(null);
  const [chatHistory, setChatHistory] = useState({});

  const addMessage = (personaId, message) => {
    setChatHistory(prev => ({
      ...prev,
      [personaId]: [...(prev[personaId] || []), message]
    }));
  };

  const clearHistory = (personaId) => {
    setChatHistory(prev => ({
      ...prev,
      [personaId]: []
    }));
  };

  const value = {
    activePersona,
    setActivePersona,
    chatHistory,
    addMessage,
    clearHistory,
  };

  return (
    <PersonaContext.Provider value={value}>
      {children}
    </PersonaContext.Provider>
  );
};