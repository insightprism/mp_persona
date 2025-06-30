import React, { useState, useEffect } from 'react';
import { 
  ThemeProvider, 
  createTheme,
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Paper,
  Button,
  Dialog
} from '@mui/material';
import { Chat, Person, Settings } from '@mui/icons-material';

import PersonaBuilder from './components/PersonaBuilder';
import ChatInterface from './components/ChatInterface';
import ComparisonView from './components/ComparisonView';
import { SessionProvider, useSession } from './context/SessionContext';
import { PersonaProvider } from './context/PersonaContext';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: 'Inter, sans-serif',
  },
});

function MainApp() {
  const [personaBuilderOpen, setPersonaBuilderOpen] = useState(false);
  const [comparisonMode, setComparisonMode] = useState(false);
  const { session, personas, createSession } = useSession();

  useEffect(() => {
    // Create initial session
    if (!session) {
      createSession();
    }
  }, [session, createSession]);

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      {/* Header */}
      <AppBar position="static" elevation={1}>
        <Toolbar>
          <Chat sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            🎭 Persona Chat System
          </Typography>
          <Button 
            color="inherit" 
            startIcon={<Settings />}
            onClick={() => setComparisonMode(!comparisonMode)}
          >
            {comparisonMode ? 'Chat Mode' : 'Compare Mode'}
          </Button>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container maxWidth="xl" sx={{ mt: 2, mb: 2 }}>
        <Grid container spacing={2}>
          {/* Control Panel */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2, mb: 2 }}>
              <Grid container spacing={2} alignItems="center">
                <Grid item>
                  <Button
                    variant="contained"
                    startIcon={<Person />}
                    onClick={() => setPersonaBuilderOpen(true)}
                  >
                    Create Persona
                  </Button>
                </Grid>
                <Grid item>
                  <Typography variant="body2" color="text.secondary">
                    Active Personas: {personas.length}
                  </Typography>
                </Grid>
                <Grid item>
                  <Typography variant="body2" color="text.secondary">
                    Session: {session?.session_id?.slice(0, 8)}...
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Main Interface */}
          <Grid item xs={12}>
            {comparisonMode ? (
              <ComparisonView personas={personas} />
            ) : (
              <ChatInterface personas={personas} />
            )}
          </Grid>
        </Grid>
      </Container>

      {/* Persona Builder Dialog */}
      <Dialog
        open={personaBuilderOpen}
        onClose={() => setPersonaBuilderOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <PersonaBuilder 
          onClose={() => setPersonaBuilderOpen(false)}
        />
      </Dialog>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SessionProvider>
        <PersonaProvider>
          <MainApp />
        </PersonaProvider>
      </SessionProvider>
    </ThemeProvider>
  );
}

export default App;