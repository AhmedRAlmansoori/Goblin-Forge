// components/dashboard/CompletedTasks.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Table, Button, Alert, Spinner } from 'react-bootstrap';
import StatusBadge from '../common/StatusBadge';
import TaskResultModal from './TaskResultModal';

const API_URL = 'http://localhost:8000/api';

function CompletedTasks() {
  const [completedTasks, setCompletedTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedResult, setSelectedResult] = useState(null);
  const [showResultModal, setShowResultModal] = useState(false);

  // Improved useEffect with immediate fetch and polling
  useEffect(() => {
    // Immediate fetch when component mounts
    fetchCompletedTasks();
    
    // Set up polling interval
    const interval = setInterval(() => {
      fetchCompletedTasks();
    }, 5000); // Poll every 5 seconds
    
    // Cleanup on unmount
    return () => clearInterval(interval);
  }, []); // Empty dependency array means this runs once on mount

  const fetchCompletedTasks = async () => {
    try {
      console.log('Fetching completed tasks...');
      const response = await axios.get(`${API_URL}/completed_tasks`);
      console.log('Completed tasks response:', response.data);
      setCompletedTasks(response.data || []);
      setError(null);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching completed tasks:', err);
      setError('Failed to load completed tasks. Please try again later.');
      setLoading(false);
    }
  };

  const viewResult = (result) => {
    console.log('Viewing result:', result);
    // Check if result contains necessary data for preview
    if (result.result) {
      console.log('Result preview:', result.result.result_preview);
      console.log('Result file:', result.result.result_file);
    } else {
      console.log('No result data found');
    }
    setSelectedResult(result);
    setShowResultModal(true);
  };

  const handleCloseModal = () => {
    setShowResultModal(false);
    setSelectedResult(null);
  };

  const retryTask = async (taskId) => {
    try {
      const response = await axios.post(`${API_URL}/retry_task/${taskId}`);
      alert(`Task has been requeued: ${response.data.message}`);
      fetchCompletedTasks();
    } catch (err) {
      alert('Failed to retry task: ' + err.message);
    }
  };

  // Render loading state
  if (loading && completedTasks.length === 0) {
    return (
      <div className="text-center p-5">
        <Spinner animation="border" variant="primary" />
        <p className="mt-3">Loading completed tasks...</p>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <Alert variant="danger">
        {error}
        <Button variant="primary" className="ms-3" onClick={fetchCompletedTasks}>
          Retry
        </Button>
      </Alert>
    );
  }

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h5 className="mb-0">Completed Tasks</h5>
        <Button variant="outline-primary" size="sm" onClick={fetchCompletedTasks}>
          Refresh
        </Button>
      </div>
      
      {completedTasks.length === 0 ? (
        <div className="text-center p-4">
          <p className="text-muted">No completed tasks found. Deploy some minions to see results here!</p>
        </div>
      ) : (
        <Table responsive hover>
          <thead>
            <tr>
              <th>Task ID</th>
              <th>Gadget</th>
              <th>Mode</th>
              <th>Status</th>
              <th>Completion Time</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {completedTasks.map((task) => (
              <tr key={task.task_id}>
                <td>{task.task_id.substring(0, 8)}...</td>
                <td>{task.gadget_name || 'Unknown'}</td>
                <td>{task.mode || 'Unknown'}</td>
                <td>
                  <StatusBadge status={task.status} />
                </td>
                <td>{task.completion_time ? new Date(task.completion_time).toLocaleString() : 'N/A'}</td>
                <td>
                  <Button 
                    variant="primary" 
                    size="sm" 
                    className="me-2"
                    onClick={() => viewResult(task)}
                  >
                    View Result
                  </Button>
                  {task.status === 'Troubled Goblin' && (
                    <Button 
                      variant="warning" 
                      size="sm" 
                      onClick={() => retryTask(task.task_id)}
                    >
                      Retry
                    </Button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}

      {selectedResult && (
        <TaskResultModal
          task={selectedResult}
          show={showResultModal}
          onHide={handleCloseModal}
          onRetry={retryTask}
        />
      )}
    </>
  );
}

export default CompletedTasks;