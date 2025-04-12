// components/common/StatusBadge.js
import React from 'react';
import { Badge } from 'react-bootstrap';

function StatusBadge({ status }) {
  let variant = 'secondary';
  let displayText = status;
  
  switch (status) {
    case 'Idle Goblin':
      variant = 'success';
      displayText = 'Completed';
      break;
    case 'Busy Goblin':
      variant = 'warning';
      displayText = 'Running';
      break;
    case 'Troubled Goblin':
      variant = 'danger';
      displayText = 'Error';
      break;
    case 'Sleepy Goblin':
      variant = 'secondary';
      displayText = 'Idle';
      break;
    case 'Paused Goblin':
      variant = 'info';
      displayText = 'Paused';
      break;
    case 'completed':
      variant = 'success';
      displayText = 'Completed';
      break;
    case 'error':
      variant = 'danger';
      displayText = 'Error';
      break;
    default:
      // Use defaults
  }
  
  return (
    <Badge bg={variant}>{displayText}</Badge>
  );
}

export default StatusBadge;