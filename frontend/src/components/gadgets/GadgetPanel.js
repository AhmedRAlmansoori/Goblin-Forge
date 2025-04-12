// components/gadgets/GadgetPanel.js
import React, { useState } from 'react';
import { Card, Button, Spinner } from 'react-bootstrap';
import axios from 'axios';
import GadgetForm from './GadgetForm';

const API_URL = 'http://localhost:8000/api';

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
              <GadgetForm 
                gadget={gadget} 
                selectedModes={selectedModes}
                parameters={parameters}
                onModeToggle={handleModeToggle}
                onInputChange={handleInputChange}
              />
              
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
            <Card.Body className="p-0">
              {results.length === 0 ? (
                <div className="text-muted text-center py-4">
                  No results yet. Deploy some minions!
                </div>
              ) : (
                <ul className="list-group list-group-flush">
                  {results.map((result) => (
                    <li key={result.id} className="list-group-item">
                      <div className="d-flex justify-content-between align-items-start mb-1">
                        <small className="text-muted">{result.timestamp}</small>
                        <span className="badge bg-info">{result.status}</span>
                      </div>
                      <div className="result-dirs small">
                        {result.result_dirs.map((dir, idx) => (
                          <div key={idx} className="result-dir mb-1">
                            <strong>Result {idx + 1}:</strong> {dir}
                          </div>
                        ))}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </Card.Body>
          </Card>
        </div>
      </div>
    </div>
  );
}

export default GadgetPanel;