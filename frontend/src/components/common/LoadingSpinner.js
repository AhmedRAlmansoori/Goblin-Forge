// components/common/LoadingSpinner.js
import React from 'react';
import { Spinner } from 'react-bootstrap';

function LoadingSpinner({ text = 'Loading...', size = null }) {
  return (
    <div className="text-center py-4">
      <Spinner 
        animation="border" 
        role="status" 
        variant="primary" 
        size={size}
        className="mb-2"
      >
        <span className="visually-hidden">{text}</span>
      </Spinner>
      <div>{text}</div>
    </div>
  );
}

export default LoadingSpinner;