// components/dashboard/TaskResultModal.js
import React from 'react';
import { Modal, Button, Table, Tabs, Tab } from 'react-bootstrap';
import StatusBadge from '../common/StatusBadge';

function TaskResultModal({ task, show, onHide, onRetry }) {
  if (!task) {
    return null;
  }

  // Check if we have result data in different possible locations
  const resultData = task.result || {};

  // Log the task and result structure to help debug
  console.log('Task in modal:', task);
  console.log('Result data extracted:', resultData);

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Task Result</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Tabs defaultActiveKey="details" className="mb-3">
          <Tab eventKey="details" title="Details">
            <Table bordered>
              <tbody>
                <tr>
                  <th>Task ID</th>
                  <td>{task.task_id}</td>
                </tr>
                <tr>
                  <th>Gadget</th>
                  <td>{task.gadget_name || resultData.gadget_name || 'Unknown'}</td>
                </tr>
                <tr>
                  <th>Mode</th>
                  <td>{task.mode || resultData.mode || 'Unknown'}</td>
                </tr>
                <tr>
                  <th>Status</th>
                  <td>
                    <StatusBadge status={task.status} />
                  </td>
                </tr>
                <tr>
                  <th>Submit Time</th>
                  <td>{task.submit_time ? new Date(task.submit_time).toLocaleString() : 'N/A'}</td>
                </tr>
                <tr>
                  <th>Completion Time</th>
                  <td>{task.completion_time ? new Date(task.completion_time).toLocaleString() : 'N/A'}</td>
                </tr>
                <tr>
                  <th>Execution Time</th>
                  <td>{task.execution_time_seconds ? `${task.execution_time_seconds.toFixed(2)} seconds` : 'N/A'}</td>
                </tr>
                <tr>
                  <th>Result Directory</th>
                  <td><code>{task.result_dir || resultData.result_dir || 'N/A'}</code></td>
                </tr>
                {(task.error || resultData.error) && (
                  <tr>
                    <th>Error</th>
                    <td className="text-danger">{task.error || resultData.error}</td>
                  </tr>
                )}
              </tbody>
            </Table>
          </Tab>
          
          <Tab eventKey="params" title="Parameters">
            <pre className="bg-light p-3 rounded">
              {JSON.stringify(task.params || {}, null, 2)}
            </pre>
          </Tab>
          
          <Tab eventKey="result" title="Result">
            <div>
              {/* Try to find result file in different possible locations */}
              {(resultData.result_file || (resultData.result && resultData.result.result_file)) && (
                <div className="mb-3">
                  <h6>Result Files</h6>
                  <ul className="list-group">
                    <li className="list-group-item">
                      <span>{resultData.result_file || resultData.result?.result_file}</span>
                    </li>
                  </ul>
                </div>
              )}
              
              {/* Try to find result preview in different possible locations */}
              {(resultData.result_preview || (resultData.result && resultData.result.result_preview)) && (
                <div>
                  <h6>Result Preview</h6>
                  <div className="border p-3 rounded bg-light">
                    <pre style={{whiteSpace: 'pre-wrap'}}>
                      {resultData.result_preview || resultData.result?.result_preview}
                    </pre>
                  </div>
                </div>
              )}
              
              {/* If no results found in the expected places, try to show raw result data */}
              {!resultData.result_file && !resultData.result?.result_file && 
               !resultData.result_preview && !resultData.result?.result_preview && (
                <div>
                  <div className="alert alert-info mb-3">
                    No specific preview available for this result. Showing raw result data:
                  </div>
                  <pre className="bg-light p-3 rounded border">
                    {JSON.stringify(resultData, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </Tab>
        </Tabs>
      </Modal.Body>
      <Modal.Footer>
        {task.status === 'Troubled Goblin' && (
          <Button variant="warning" onClick={() => onRetry(task.task_id)}>
            Retry Task
          </Button>
        )}
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
}

export default TaskResultModal;