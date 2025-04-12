import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Spinner, Alert, Nav, Tab, Button, Form, Card, Badge, ListGroup } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

// Base API URL
// const API_URL = 'http://localhost:8000/api';
const API_URL = process.env.REACT_APP_API_URL || 'http://backend:8000/api';


function App() {
  const [gadgets, setGadgets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(null);
  const [minionStatus, setMinionStatus] = useState({});

  useEffect(() => {
    // Fetch available Goblin Gadgets on component mount
    const fetchGadgets = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${API_URL}/gadgets`);
        setGadgets(response.data);
        
        // Set active tab to first gadget if available
        if (response.data.length > 0) {
          setActiveTab(response.data[0].id);
        }
      } catch (err) {
        setError('Failed to load Goblin Gadgets. Please try again later.');
        console.error('Error fetching gadgets:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchGadgets();

    // Set up polling for minion status updates
    const statusInterval = setInterval(async () => {
      try {
        const response = await axios.get(`${API_URL}/minion_status`);
        setMinionStatus(response.data.minions || {});
      } catch (err) {
        console.error('Error fetching minion status:', err);
      }
    }, 5000); // Poll every 5 seconds

    return () => clearInterval(statusInterval);
  }, []);

  // Render loading spinner
  if (loading) {
    return (
      <Container className="d-flex justify-content-center align-items-center vh-100">
        <div className="text-center">
          <Spinner animation="border" role="status" variant="primary" className="mb-3">
            <span className="visually-hidden">Loading Goblin Forge...</span>
          </Spinner>
          <div>Loading Goblin Forge...</div>
        </div>
      </Container>
    );
  }

  // Render error message
  if (error) {
    return (
      <Container className="mt-5">
        <Alert variant="danger">
          <Alert.Heading>Oh no! Something went wrong!</Alert.Heading>
          <p>{error}</p>
        </Alert>
      </Container>
    );
  }

  return (
    <div className="goblin-forge">
      <header className="app-header bg-dark text-light py-4">
        <Container>
          <div className="d-flex align-items-center">
            <div className="goblin-logo me-3">🧙‍♂️</div>
            <div>
              <h1 className="mb-0">Goblin Forge</h1>
              <p className="mb-0 text-muted">CLI tools with a friendly face</p>
            </div>
          </div>
        </Container>
      </header>

      <Container className="mt-4">
        <div className="minion-status-bar mb-3">
          <div className="d-flex justify-content-between align-items-center">
            <h5 className="mb-0">Minion Status</h5>
            <div className="status-indicators">
              {Object.entries(minionStatus).map(([id, status]) => (
                <Badge 
                  key={id}
                  bg={status === "Busy Goblin" ? "warning" : 
                      status === "Troubled Goblin" ? "danger" : "success"}
                  className="me-2 p-2"
                >
                  {status}
                </Badge>
              ))}
              {Object.keys(minionStatus).length === 0 && (
                <Badge bg="secondary" className="p-2">No Active Minions</Badge>
              )}
            </div>
          </div>
        </div>

        {gadgets.length === 0 ? (
          <Alert variant="warning">
            No Goblin Gadgets found. Please check your plugin directory.
          </Alert>
        ) : (
          <Tab.Container activeKey={activeTab} onSelect={setActiveTab}>
            <div className="gadget-container">
              <Nav variant="tabs" className="mb-3">
                {gadgets.map((gadget) => (
                  <Nav.Item key={gadget.id}>
                    <Nav.Link eventKey={gadget.id}>{gadget.name}</Nav.Link>
                  </Nav.Item>
                ))}
              </Nav>
              
              <Tab.Content>
                {gadgets.map((gadget) => (
                  <Tab.Pane key={gadget.id} eventKey={gadget.id}>
                    <GadgetPanel gadget={gadget} />
                  </Tab.Pane>
                ))}
              </Tab.Content>
            </div>
          </Tab.Container>
        )}
      </Container>

      <footer className="app-footer mt-5 py-3 bg-light">
        <Container>
          <p className="text-center text-muted mb-0">
            Goblin Forge &copy; {new Date().getFullYear()} | Your friendly CLI interface
          </p>
        </Container>
      </footer>
    </div>
  );
}

// GadgetPanel component - Displays gadget modes and form
function GadgetPanel({ gadget }) {
  const [selectedModes, setSelectedModes] = useState([]);
  const [parameters, setParameters] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [results, setResults] = useState([]);

  // Handle mode selection
  const handleModeToggle = (modeId) => {
    if (selectedModes.includes(modeId)) {
      setSelectedModes(selectedModes.filter(id => id !== modeId));
    } else {
      setSelectedModes([...selectedModes, modeId]);
    }
  };

  // Handle form input changes
  const handleInputChange = (modeId, fieldName, value) => {
    setParameters(prev => ({
      ...prev,
      [modeId]: {
        ...(prev[modeId] || {}),
        [fieldName]: value
      }
    }));
  };

  // Submit selected modes for execution
  const handleSubmit = async () => {
    if (selectedModes.length === 0) {
      alert('Please select at least one mode to run');
      return;
    }

    try {
      setSubmitting(true);
      
      const response = await axios.post(`${API_URL}/submit_task`, {
        gadget_id: gadget.id,
        modes: selectedModes,
        parameters: parameters
      });

      // Add new result to the results list
      setResults([
        {
          id: Date.now().toString(),
          timestamp: new Date().toLocaleString(),
          task_ids: response.data.task_ids,
          result_dirs: response.data.result_dirs,
          status: 'Submitted'
        },
        ...results
      ]);

      // Clear selected modes and parameters
      setSelectedModes([]);
      setParameters({});
      
    } catch (error) {
      console.error('Error submitting task:', error);
      alert('Failed to submit task. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  // Render the panel content
  return (
    <div className="gadget-panel">
      <div className="gadget-description mb-4">
        <h3>{gadget.name}</h3>
        <p className="text-muted">{gadget.description}</p>
      </div>

      <div className="row">
        <div className="col-md-7">
          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">Available Modes</h5>
            </Card.Header>
            <Card.Body>
              {gadget.modes.map((mode) => (
                <div key={mode.id} className="mode-item mb-3 pb-3 border-bottom">
                  <Form.Check
                    type="checkbox"
                    id={`mode-${mode.id}`}
                    label={<strong>{mode.name}</strong>}
                    checked={selectedModes.includes(mode.id)}
                    onChange={() => handleModeToggle(mode.id)}
                    className="mb-1"
                  />
                  <p className="text-muted small ms-4">{mode.description}</p>
                  
                  {selectedModes.includes(mode.id) && mode.form_schema && (
                    <div className="mode-parameters mt-3 ms-4">
                      {Object.entries(mode.form_schema).map(([fieldName, field]) => (
                        <Form.Group key={fieldName} className="mb-3">
                          <Form.Label>{field.label}</Form.Label>
                          
                          {field.type === 'textarea' ? (
                            <Form.Control
                              as="textarea"
                              rows={3}
                              placeholder={field.placeholder || ''}
                              required={field.required}
                              value={(parameters[mode.id] || {})[fieldName] || ''}
                              onChange={(e) => handleInputChange(mode.id, fieldName, e.target.value)}
                            />
                          ) : field.type === 'select' ? (
                            <Form.Select 
                              required={field.required}
                              value={(parameters[mode.id] || {})[fieldName] || (field.default || '')}
                              onChange={(e) => handleInputChange(mode.id, fieldName, e.target.value)}
                            >
                              <option value="">Select an option</option>
                              {field.options.map(option => (
                                <option key={option.value} value={option.value}>
                                  {option.label}
                                </option>
                              ))}
                            </Form.Select>
                          ) : field.type === 'multiselect' ? (
                            <div>
                              {field.options.map(option => (
                                <Form.Check
                                  key={option.value}
                                  type="checkbox"
                                  id={`${mode.id}-${fieldName}-${option.value}`}
                                  label={option.label}
                                  checked={((parameters[mode.id] || {})[fieldName] || []).includes(option.value)}
                                  onChange={(e) => {
                                    const currentValues = ((parameters[mode.id] || {})[fieldName] || []);
                                    const newValues = e.target.checked
                                      ? [...currentValues, option.value]
                                      : currentValues.filter(v => v !== option.value);
                                    handleInputChange(mode.id, fieldName, newValues);
                                  }}
                                />
                              ))}
                            </div>
                          ) : (
                            <Form.Control
                              type="text"
                              placeholder={field.placeholder || ''}
                              required={field.required}
                              value={(parameters[mode.id] || {})[fieldName] || ''}
                              onChange={(e) => handleInputChange(mode.id, fieldName, e.target.value)}
                            />
                          )}
                          
                          {field.description && (
                            <Form.Text className="text-muted">
                              {field.description}
                            </Form.Text>
                          )}
                        </Form.Group>
                      ))}
                    </div>
                  )}
                </div>
              ))}

              <div className="d-grid gap-2 mt-4">
                <Button 
                  variant="primary" 
                  size="lg"
                  onClick={handleSubmit}
                  disabled={submitting || selectedModes.length === 0}
                >
                  {submitting ? (
                    <>
                      <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-2" />
                      Deploying Minions...
                    </>
                  ) : (
                    'Deploy Minions'
                  )}
                </Button>
              </div>
            </Card.Body>
          </Card>
        </div>

        <div className="col-md-5">
          <Card>
            <Card.Header>
              <h5 className="mb-0">Results</h5>
            </Card.Header>
            <ListGroup variant="flush">
              {results.length === 0 ? (
                <ListGroup.Item className="text-muted text-center py-4">
                  No results yet. Deploy some minions!
                </ListGroup.Item>
              ) : (
                results.map((result) => (
                  <ListGroup.Item key={result.id}>
                    <div className="d-flex justify-content-between align-items-start mb-1">
                      <small className="text-muted">{result.timestamp}</small>
                      <Badge bg="info">{result.status}</Badge>
                    </div>
                    <div className="result-dirs small">
                      {result.result_dirs.map((dir, idx) => (
                        <div key={idx} className="result-dir mb-1">
                          <strong>Result {idx + 1}:</strong> {dir}
                        </div>
                      ))}
                    </div>
                  </ListGroup.Item>
                ))
              )}
            </ListGroup>
          </Card>
        </div>
      </div>
    </div>
  );
}

export default App;