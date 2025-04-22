// components/gadgets/GadgetForm.js
import React, { useState } from 'react';
import { Form } from 'react-bootstrap';
import axios from 'axios';

function GadgetForm({ gadget, selectedModes, parameters, onModeToggle, onInputChange }) {
  const [uploadProgress, setUploadProgress] = useState({});

  const handleFileUpload = async (modeId, fieldName, event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post('http://localhost:8000/api/upload_file', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(prev => ({
            ...prev,
            [`${modeId}-${fieldName}`]: percentCompleted
          }));
        }
      });

      // Update the form field with the uploaded file path
      onInputChange(modeId, fieldName, response.data.file_path);
    } catch (error) {
      console.error('Error uploading file:', error);
      // Handle error appropriately
    }
  };

  return (
    <>
      {gadget.modes.map((mode) => (
        <div key={mode.id} className="mode-item mb-3 pb-3 border-bottom">
          <Form.Check
            type="checkbox"
            id={`mode-${mode.id}`}
            label={<strong>{mode.name}</strong>}
            checked={selectedModes.includes(mode.id)}
            onChange={() => onModeToggle(mode.id)}
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
                      onChange={(e) => onInputChange(mode.id, fieldName, e.target.value)}
                    />
                  ) : field.type === 'select' ? (
                    <Form.Select 
                      required={field.required}
                      value={(parameters[mode.id] || {})[fieldName] || (field.default || '')}
                      onChange={(e) => onInputChange(mode.id, fieldName, e.target.value)}
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
                            onInputChange(mode.id, fieldName, newValues);
                          }}
                        />
                      ))}
                    </div>
                  ) : field.type === 'file' ? (
                    <div>
                      <Form.Control
                        type="file"
                        onChange={(e) => handleFileUpload(mode.id, fieldName, e)}
                      />
                      {uploadProgress[`${mode.id}-${fieldName}`] !== undefined && (
                        <div className="mt-2">
                          <div className="progress">
                            <div 
                              className="progress-bar" 
                              role="progressbar" 
                              style={{ width: `${uploadProgress[`${mode.id}-${fieldName}`]}%` }}
                              aria-valuenow={uploadProgress[`${mode.id}-${fieldName}`]}
                              aria-valuemin="0"
                              aria-valuemax="100"
                            >
                              {uploadProgress[`${mode.id}-${fieldName}`]}%
                            </div>
                          </div>
                        </div>
                      )}
                      {(parameters[mode.id] || {})[fieldName] && (
                        <div className="mt-2">
                          <small className="text-muted">
                            File uploaded: {(parameters[mode.id] || {})[fieldName]}
                          </small>
                        </div>
                      )}
                    </div>
                  ) : (
                    <Form.Control
                      type="text"
                      placeholder={field.placeholder || ''}
                      required={field.required}
                      value={(parameters[mode.id] || {})[fieldName] || ''}
                      onChange={(e) => onInputChange(mode.id, fieldName, e.target.value)}
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
    </>
  );
}

export default GadgetForm;