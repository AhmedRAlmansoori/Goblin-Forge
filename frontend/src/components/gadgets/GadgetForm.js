// components/gadgets/GadgetForm.js
import React from 'react';
import { Form } from 'react-bootstrap';

function GadgetForm({ gadget, selectedModes, parameters, onModeToggle, onInputChange }) {
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