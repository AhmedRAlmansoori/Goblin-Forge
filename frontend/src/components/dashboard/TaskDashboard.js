// components/dashboard/TaskDashboard.js
import React, { useState } from 'react';
import { Card, Nav } from 'react-bootstrap';
import MinionDashboard from './MinionDashboard';
import CompletedTasks from './CompletedTasks';

function TaskDashboard() {
  const [activeTab, setActiveTab] = useState('active');

  return (
    <Card className="mt-4 mb-4">
      <Card.Header>
        <Nav variant="tabs" activeKey={activeTab} onSelect={(k) => setActiveTab(k)}>
          <Nav.Item>
            <Nav.Link eventKey="active">Active Minions</Nav.Link>
          </Nav.Item>
          <Nav.Item>
            <Nav.Link eventKey="completed">Completed Tasks</Nav.Link>
          </Nav.Item>
        </Nav>
      </Card.Header>
      <Card.Body>
        {activeTab === 'active' && <MinionDashboard />}
        {activeTab === 'completed' && <CompletedTasks />}
      </Card.Body>
    </Card>
  );
}

export default TaskDashboard;