import React, { useState, useEffect } from 'react';
import {
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Typography,
  Divider,
  Alert,
  CircularProgress,
  Box,
  Chip
} from '@mui/material';
import { Person, Psychology, Settings } from '@mui/icons-material';
import { useSession } from '../context/SessionContext';

const PersonaBuilder = ({ onClose }) => {
  const { createPersona, getAvailableModels, loading } = useSession();
  const [formData, setFormData] = useState({
    name: '',
    age: 30,
    race_ethnicity: '',
    gender: '',
    education: '',
    location_type: '',
    income: '',
    llm_provider: '',
    llm_api_key: '',
    llm_model: ''
  });
  const [availableModels, setAvailableModels] = useState(null);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadModels = async () => {
      try {
        const models = await getAvailableModels();
        setAvailableModels(models);
        
        // Auto-select first available provider
        const providers = Object.entries(models.providers);
        const availableProvider = providers.find(([_, config]) => config.available);
        if (availableProvider) {
          const [providerName, config] = availableProvider;
          setFormData(prev => ({
            ...prev,
            llm_provider: providerName,
            llm_model: config.models[0] || ''
          }));
        }
      } catch (err) {
        setError('Failed to load available models');
      }
    };
    loadModels();
  }, [getAvailableModels]);

  const handleChange = (field) => (event) => {
    const value = event.target.value;
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Auto-select default model when provider changes
    if (field === 'llm_provider' && availableModels) {
      const provider = availableModels.providers[value];
      if (provider && provider.models.length > 0) {
        setFormData(prev => ({ ...prev, llm_model: provider.models[0] }));
      }
    }
  };

  const handleSubmit = async () => {
    try {
      setCreating(true);
      setError(null);
      
      // Validate required fields
      const required = ['name', 'race_ethnicity', 'gender', 'education', 'location_type', 'income'];
      const missing = required.filter(field => !formData[field]);
      if (missing.length > 0) {
        throw new Error(`Missing required fields: ${missing.join(', ')}`);
      }

      await createPersona(formData);
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to create persona');
    } finally {
      setCreating(false);
    }
  };

  const getProviderStatus = (provider, config) => {
    if (config.available) {
      return <Chip label="Available" color="success" size="small" />;
    } else if (config.requires_key) {
      return <Chip label="API Key Required" color="warning" size="small" />;
    } else {
      return <Chip label="Unavailable" color="error" size="small" />;
    }
  };

  return (
    <>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <Person />
          <Typography variant="h6">Create New Persona</Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        <Grid container spacing={2}>
          {/* Basic Information */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Person fontSize="small" />
              Basic Information
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Name"
              value={formData.name}
              onChange={handleChange('name')}
              placeholder="e.g., Maria Rodriguez"
              required
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Age"
              type="number"
              value={formData.age}
              onChange={handleChange('age')}
              inputProps={{ min: 18, max: 80 }}
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Gender</InputLabel>
              <Select
                value={formData.gender}
                onChange={handleChange('gender')}
                label="Gender"
              >
                <MenuItem value="female">Female</MenuItem>
                <MenuItem value="male">Male</MenuItem>
                <MenuItem value="non-binary">Non-binary</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Race/Ethnicity</InputLabel>
              <Select
                value={formData.race_ethnicity}
                onChange={handleChange('race_ethnicity')}
                label="Race/Ethnicity"
              >
                <MenuItem value="white">White</MenuItem>
                <MenuItem value="black">Black/African American</MenuItem>
                <MenuItem value="hispanic">Hispanic/Latino</MenuItem>
                <MenuItem value="asian">Asian</MenuItem>
                <MenuItem value="native_american">Native American</MenuItem>
                <MenuItem value="mixed">Mixed</MenuItem>
                <MenuItem value="other">Other</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Education</InputLabel>
              <Select
                value={formData.education}
                onChange={handleChange('education')}
                label="Education"
              >
                <MenuItem value="high_school">High School</MenuItem>
                <MenuItem value="college">College</MenuItem>
                <MenuItem value="graduate">Graduate Degree</MenuItem>
                <MenuItem value="professional">Professional Degree</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Location</InputLabel>
              <Select
                value={formData.location_type}
                onChange={handleChange('location_type')}
                label="Location"
              >
                <MenuItem value="urban">Urban</MenuItem>
                <MenuItem value="suburban">Suburban</MenuItem>
                <MenuItem value="rural">Rural</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Income Level</InputLabel>
              <Select
                value={formData.income}
                onChange={handleChange('income')}
                label="Income Level"
              >
                <MenuItem value="under_25k">Under $25k</MenuItem>
                <MenuItem value="25k_40k">$25k - $40k</MenuItem>
                <MenuItem value="40k_50k">$40k - $50k</MenuItem>
                <MenuItem value="50k_75k">$50k - $75k</MenuItem>
                <MenuItem value="75k_100k">$75k - $100k</MenuItem>
                <MenuItem value="over_100k">Over $100k</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          {/* AI Model Configuration */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1, mt: 2 }}>
              <Psychology fontSize="small" />
              AI Model Configuration
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>
          
          {availableModels && (
            <>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Provider</InputLabel>
                  <Select
                    value={formData.llm_provider}
                    onChange={handleChange('llm_provider')}
                    label="Provider"
                  >
                    {Object.entries(availableModels.providers).map(([provider, config]) => (
                      <MenuItem key={provider} value={provider} disabled={!config.available}>
                        <Box display="flex" justifyContent="space-between" alignItems="center" width="100%">
                          <span>{provider.toUpperCase()}</span>
                          {getProviderStatus(provider, config)}
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Model</InputLabel>
                  <Select
                    value={formData.llm_model}
                    onChange={handleChange('llm_model')}
                    label="Model"
                    disabled={!formData.llm_provider}
                  >
                    {formData.llm_provider && availableModels.providers[formData.llm_provider]?.models.map(model => (
                      <MenuItem key={model} value={model}>
                        {model}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              {formData.llm_provider && availableModels.providers[formData.llm_provider]?.requires_key && (
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="API Key"
                    type="password"
                    value={formData.llm_api_key}
                    onChange={handleChange('llm_api_key')}
                    placeholder="Enter your API key"
                    helperText="Required for this provider. Your key is stored securely for this session only."
                  />
                </Grid>
              )}
            </>
          )}
        </Grid>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose} disabled={creating}>
          Cancel
        </Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained" 
          disabled={creating || loading}
          startIcon={creating ? <CircularProgress size={20} /> : <Person />}
        >
          {creating ? 'Creating...' : 'Create Persona'}
        </Button>
      </DialogActions>
    </>
  );
};

export default PersonaBuilder;