// components/dashboard/MetricsPanel.js
import React from 'react';
import { Row, Col, Card, ProgressBar } from 'react-bootstrap';

function MetricsPanel({ metrics }) {
  if (!metrics) {
    return null;
  }

  // Helper function to determine progress bar variant based on value
  const getVariant = (value, thresholds) => {
    if (value > thresholds.danger) return 'danger';
    if (value > thresholds.warning) return 'warning';
    return 'success';
  };

  return (
    <Row className="mb-4">
      <Col md={3}>
        <Card className="text-center h-100">
          <Card.Body>
            <h6 className="text-muted">CPU Usage</h6>
            <h3>{metrics.cpu_percent}%</h3>
            <ProgressBar 
              now={metrics.cpu_percent} 
              variant={getVariant(metrics.cpu_percent, { warning: 60, danger: 80 })} 
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
              variant={getVariant(metrics.memory_percent, { warning: 60, danger: 80 })} 
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
            <h3>{metrics.error_rate.toFixed(1)}%</h3>
            <ProgressBar 
              now={metrics.error_rate} 
              variant={getVariant(metrics.error_rate, { warning: 10, danger: 20 })} 
            />
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );
}

export default MetricsPanel;