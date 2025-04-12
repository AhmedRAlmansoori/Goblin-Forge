// components/dashboard/MinionDashboard.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Table, Badge, Button, Alert, Row, Col, Card, ProgressBar } from 'react-bootstrap';
import StatusBadge from '../common/StatusBadge';

const API_URL = 'http://localhost:8000/api';

function MinionDashboard() {
  const [minionStatus, setMinionStatus] = useState({});
  const [pendingTasks, setPendingTasks] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Improved useEffect with immediate fetch and polling
  useEffect(() => {
    // Immediate fetch when component mounts
    fetchData();
    
    // Set up polling interval
    const interval = setInterval(() => {
      fetchData();
    }, 5000); // Poll every 5 seconds
    
    // Cleanup on unmount
    return () => clearInterval(interval);
  }, []); // Empty dependency array means this runs once on mount
  useEffect(() => {
    console.log('Minion status updated:', minionStatus);
  }, [minionStatus]);
  
  useEffect(() => {
    console.log('Pending tasks updated:', pendingTasks);
  }, [pendingTasks]);
  
  const fetchData = async () => {
    try {
      console.log('Fetching minion data...');
      
      // Fetch minion status
      const statusResponse = await axios.get(`${API_URL}/minion_status`);
      console.log('Minion status:', statusResponse.data);
      setMinionStatus(statusResponse.data.minions || {});
      
      // Fetch pending tasks
      const pendingResponse = await axios.get(`${API_URL}/pending_tasks`);
      console.log('Pending tasks:', pendingResponse.data);
      setPendingTasks(pendingResponse.data || []);
      
      // Fetch metrics
      const metricsResponse = await axios.get(`${API_URL}/minion_metrics`);
      console.log('Metrics:', metricsResponse.data);
      setMetrics(metricsResponse.data || {});
      
      setError(null);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching minion data:', err);
      setError('Failed to load minion data. Please try again later.');
      setLoading(false);
    }
  };

  const cancelTask = async (taskId) => {
    try {
      const response = await axios.post(`${API_URL}/cancel_task/${taskId}`);
      alert(response.data.message);
      fetchData();
    } catch (err) {
      alert('Failed to cancel task: ' + err.message);
    }
  };

  const pauseMinion = async (minionId) => {
    try {
      const response = await axios.post(`${API_URL}/pause_minion/${minionId}`);
      alert(response.data.message);
      fetchData();
    } catch (err) {
      alert('Failed to pause minion: ' + err.message);
    }
  };

  const resumeMinion = async (minionId) => {
    try {
      const response = await axios.post(`${API_URL}/resume_minion/${minionId}`);
      alert(response.data.message);
      fetchData();
    } catch (err) {
      alert('Failed to resume minion: ' + err.message);
    }
  };

  // Render loading state
  if (loading && Object.keys(minionStatus).length === 0) {
    return (
      <div className="text-center p-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <p className="mt-3">Loading minion status...</p>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <Alert variant="danger">
        {error}
        <Button variant="primary" className="ms-3" onClick={fetchData}>
          Retry
        </Button>
      </Alert>
    );
  }

  return (
    <>
      {/* Metrics Overview */}
      {metrics && (
        <Row className="mb-4">
          <Col md={3}>
            <Card className="text-center h-100">
              <Card.Body>
                <h6 className="text-muted">CPU Usage</h6>
                <h3>{metrics.cpu_percent}%</h3>
                <ProgressBar 
                  now={metrics.cpu_percent} 
                  variant={metrics.cpu_percent > 80 ? 'danger' : metrics.cpu_percent > 60 ? 'warning' : 'success'} 
                />
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center h-100">
              <Card.Body>
                <h6 className="text-muted">Memory Usage</h6>
                <h3>{metrics.memory_percent}%</h3>
                <ProgressBar 
                  now={metrics.memory_percent} 
                  variant={metrics.memory_percent > 80 ? 'danger' : metrics.memory_percent > 60 ? 'warning' : 'success'} 
                />
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center h-100">
              <Card.Body>
                <h6 className="text-muted">Active Tasks</h6>
                <h3>{metrics.active_tasks}</h3>
                <ProgressBar 
                  now={(metrics.active_tasks / 5) * 100} 
                  variant="info" 
                />
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center h-100">
              <Card.Body>
                <h6 className="text-muted">Error Rate</h6>
                <h3>{metrics.error_rate?.toFixed(1) || "0"}%</h3>
                <ProgressBar 
                  now={metrics.error_rate || 0} 
                  variant={(metrics.error_rate || 0) > 20 ? 'danger' : (metrics.error_rate || 0) > 10 ? 'warning' : 'success'} 
                />
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Active Minions */}
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h5 className="mb-0">Active Minions</h5>
        <Button variant="outline-primary" size="sm" onClick={fetchData}>
          Refresh
        </Button>
      </div>

      {Object.keys(minionStatus).length === 0 ? (
        <div className="text-center p-4">
          <p className="text-muted">No active minions. Deploy some to see them here!</p>
        </div>
      ) : (
        <Table responsive hover>
          <thead>
            <tr>
              <th>Minion ID</th>
              <th>Status</th>
              <th>Current Task</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(minionStatus).map(([id, status]) => (
              <tr key={id}>
                <td>{id.substring(0, 15)}...</td>
                <td>
                  <StatusBadge status={status} />
                </td>
                <td>
                  {pendingTasks.find(task => task.task_id === id)?.mode || 'None'}
                </td>
                <td>
                  {status === "Busy Goblin" && (
                    <Button variant="danger" size="sm" onClick={() => cancelTask(id)}>
                      Cancel
                    </Button>
                  )}
                  {status === "Idle Goblin" && (
                    <Button variant="secondary" size="sm" onClick={() => pauseMinion(id)}>
                      Pause
                    </Button>
                  )}
                  {status === "Paused Goblin" && (
                    <Button variant="success" size="sm" onClick={() => resumeMinion(id)}>
                      Resume
                    </Button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}

      {/* Pending Tasks */}
      <div className="d-flex justify-content-between align-items-center mt-4 mb-3">
        <h5 className="mb-0">Pending Tasks</h5>
      </div>

      {pendingTasks.length === 0 ? (
        <div className="text-center p-4">
          <p className="text-muted">No pending tasks in the queue.</p>
        </div>
      ) : (
        <Table responsive hover>
          <thead>
            <tr>
              <th>Task ID</th>
              <th>Gadget</th>
              <th>Mode</th>
              <th>Submitted</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {pendingTasks.map((task) => (
              <tr key={task.task_id}>
                <td>{task.task_id.substring(0, 8)}...</td>
                <td>{task.gadget_name || 'Unknown'}</td>
                <td>{task.mode || 'Unknown'}</td>
                <td>{new Date(task.submit_time).toLocaleString()}</td>
                <td>
                  <Button 
                    variant="danger" 
                    size="sm" 
                    onClick={() => cancelTask(task.task_id)}
                  >
                    Cancel
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </>
  );
  
}

export default MinionDashboard;