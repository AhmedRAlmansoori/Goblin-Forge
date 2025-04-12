// App.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Spinner, Alert, Nav, Tab } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import TaskDashboard from './components/dashboard/TaskDashboard';
import GadgetPanel from './components/gadgets/GadgetPanel';

// Base API URL
const API_URL = 'http://localhost:8000/api';

function App() {
  const [gadgets, setGadgets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(null);

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
        {/* Task Dashboard */}
        <TaskDashboard />

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

export default App;