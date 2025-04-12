# Goblin Forge

<img src="frontend/public/goblin-logo.png" width="200" height="200" />


A Python-based web application designed to simplify executing CLI binaries through an intuitive, visually appealing, and menu-driven web interface.


## Overview

Goblin Forge provides a user-friendly interface to configure and execute command-line tools via a web browser. It streamlines the workflow of selecting execution modes, setting parameters, and managing results, all through a plugin system called "Goblin Gadgets."

### Key Features

- **Intuitive Web Interface**: Easy-to-use tabbed interface for accessing different tools
- **Plugin Architecture**: Extend with custom tools via the Goblin Gadgets plugin system
- **Concurrent Execution**: Process multiple tasks simultaneously with resource-conscious worker management
- **Organized Results Storage**: Automatic saving and organization of execution outputs
- **Mode-based Configuration**: Each tool can expose multiple operational modes with customized parameters

## System Architecture

Goblin Forge follows a modern, modular architecture:

- **Backend**: FastAPI for modern, async-friendly REST API
- **Frontend**: React with Bootstrap for a clean, responsive UI
- **Worker Management**: Celery with Redis for task queuing and concurrent processing
- **Plugin System**: Dynamic Python module loading for Goblin Gadgets
- **Results Management**: Automated storage and cleanup of execution results

## Project Structure

```
goblin_forge/
├── __init__.py                   # Root package marker
├── api/
│   ├── __init__.py               # API package marker
│   └── main.py                   # FastAPI application and endpoints
├── core/
│   ├── __init__.py               # Core package marker
│   ├── minion_manager.py         # Worker process management
│   ├── results_manager.py        # Results handling
│   └── plugin_loader.py          # Plugin discovery and loading
├── plugins/
│   ├── __init__.py               # Plugins package marker
│   ├── base_gadget.py            # Base class for all gadgets
│   ├── scanner_gadget.py         # Example network scanner gadget
│   └── encoder_gadget.py         # Example encoder/decoder gadget
├── frontend/                     # React application directory
│   ├── public/
│   │   ├── index.html
│   │   ├── manifest.json
│   │   └── goblin-logo.svg
│   ├── src/
│   │   ├── App.js                # Main React application
│   │   ├── App.css
│   │   ├── index.js
│   │   └── index.css
│   ├── package.json
│   └── package-lock.json
├── tasks/
│   ├── __init__.py               # Tasks package marker
│   └── gadget_tasks.py           # Celery task definitions
├── utils/
│   ├── __init__.py               # Utils package marker
│   └── file_helpers.py           # Helper utilities
├── results/                      # Directory for storing execution results
│   └── .gitkeep                  # To ensure directory is tracked in git
├── requirements.txt              # Python dependencies
├── setup.py                      # For packaging the project
└── README.md                     # Project documentation
```

## Installation

### Prerequisites

- Python 3.8+
- Node.js 14+
- Redis (for Celery task queue)

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/goblin-forge.git
   cd goblin-forge
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install Redis (if not already installed):
   - **Linux**: `sudo apt install redis-server`
   - **macOS**: `brew install redis`
   - **Windows**: Download from [Redis for Windows](https://github.com/tporadowski/redis/releases)

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd goblin_forge/frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Create a development build:
   ```bash
   npm run build
   ```

## Running the Application

### Start Redis

```bash
redis-server
```

### Start Celery Worker (Minions)

```bash
cd goblin-forge
celery -A goblin_forge.core.minion_manager.celery_app worker --loglevel=info
```

### Start Backend Server

```bash
cd goblin-forge
uvicorn goblin_forge.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend Development Server

```bash
cd goblin-forge/frontend
npm start
```

The application will be available at http://localhost:3000

## Docker Deployment (Quick Setup)

If you want to quickly test Goblin Forge without installing all the required dependencies, you can use Docker. This is especially useful for Windows users.

### Prerequisites

- Docker Desktop (for Windows/Mac) or Docker Engine (for Linux)
- VSCode with Docker extension (recommended but optional)

### Setup Steps

1. **Create Docker configuration files in your project root:**

   Create `docker-compose.yml`:
   ```yaml
   version: '3.8'

   services:
     # Redis service for Celery task queue
     redis:
       image: redis:alpine
       ports:
         - "6379:6379"
       networks:
         - goblin-network

     # Backend API service
     backend:
       build:
         context: .
         dockerfile: Dockerfile.backend
       ports:
         - "8000:8000"
       volumes:
         - ./:/app
         - ./results:/app/results
       depends_on:
         - redis
       networks:
         - goblin-network
       environment:
         - REDIS_URL=redis://redis:6379/0
         - PYTHONPATH=/app

     # Celery worker service
     worker:
       build:
         context: .
         dockerfile: Dockerfile.backend
       command: celery -A goblin_forge.core.minion_manager.celery_app worker --loglevel=info
       volumes:
         - ./:/app
         - ./results:/app/results
       depends_on:
         - redis
         - backend
       networks:
         - goblin-network
       environment:
         - REDIS_URL=redis://redis:6379/0
         - PYTHONPATH=/app

     # Frontend service
     frontend:
       build:
         context: .
         dockerfile: Dockerfile.frontend
       ports:
         - "3000:3000"
       volumes:
         - ./frontend:/app/frontend
       depends_on:
         - backend
       networks:
         - goblin-network

   networks:
     goblin-network:
       driver: bridge
   ```

   Create `Dockerfile.backend`:
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       nmap \
       && rm -rf /var/lib/apt/lists/*

   # Copy requirements
   COPY requirements.txt /app/

   # Install Python dependencies
   RUN pip install --no-cache-dir -r requirements.txt

   # Copy the application
   COPY . /app/

   # Run FastAPI application
   CMD ["uvicorn", "goblin_forge.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
   ```

   Create `Dockerfile.frontend`:
   ```dockerfile
   FROM node:16-alpine

   WORKDIR /app

   # Copy package files
   COPY frontend/package.json frontend/package-lock.json /app/frontend/

   # Install Node.js dependencies
   WORKDIR /app/frontend
   RUN npm install

   # Copy the rest of the frontend code
   COPY frontend/ /app/frontend/

   # Set working directory to the frontend directory
   WORKDIR /app/frontend

   # Start the development server
   CMD ["npm", "start"]
   ```

2. **Update your configuration files for Docker:**

   Update `core/minion_manager.py` to use environment variables for Redis:
   ```python
   celery_app = Celery('goblin_forge',
                       broker=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
                       backend=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
   ```

   Update CORS settings in `api/main.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000", "http://frontend:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - Frontend UI: http://localhost:3000
   - Backend API: http://localhost:8000/docs

5. **Stop the application when done:**
   ```bash
   # Press Ctrl+C in the terminal or run:
   docker-compose down
   ```

Using Docker allows you to run the entire application stack without installing Redis, Python dependencies, or Node.js directly on your system. This provides a cleaner testing environment that's closer to production.

## Usage Guide

1. **Browse Available Gadgets**: When you open the application, you'll see tabs for each available Goblin Gadget.

2. **Select a Gadget**: Click on a tab to select the gadget you want to use.

3. **Choose Execution Modes**: Each gadget has multiple execution modes. Select the checkbox next to each mode you want to run.

4. **Configure Parameters**: For each selected mode, fill in the required parameters in the form.

5. **Deploy Minions**: Click the "Deploy Minions" button to start execution.

6. **View Results**: After execution, results will appear in the Results panel with paths to output files.

## Creating a Goblin Gadget

To create a new Goblin Gadget, follow these steps:

1. Create a new Python file in the `goblin_forge/plugins/` directory (e.g., `my_gadget.py`)

2. Implement the `BaseGadget` interface:

```python
from goblin_forge.plugins.base_gadget import BaseGadget

class MyGadget(BaseGadget):
    name = "My Awesome Gadget"
    description = "Does something cool"
    tab_id = "my_gadget"
    binary_name = "mytool"  # Optional: name of binary executable to use
    binary_path = None      # Optional: specific path to binary
    
    def get_modes(self):
        return [
            {
                "id": "mode1",
                "name": "Mode 1",
                "description": "First operation mode"
            },
            {
                "id": "mode2",
                "name": "Mode 2",
                "description": "Second operation mode"
            }
        ]
    
    def get_form_schema(self, mode):
        # Define input fields for each mode
        if mode == "mode1":
            return {
                "input1": {
                    "type": "string",
                    "label": "Input 1",
                    "required": True,
                    "placeholder": "Enter value"
                }
            }
        return {}
    
    async def execute(self, mode, params, result_dir):
        # Implement execution logic
        # For binary-based gadgets:
        binary_path = self.get_binary_path()
        
        # Example command construction
        cmd = [binary_path, "--some-flag", params.get("input1")]
        
        # Execute command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # Write output to result file
        result_file = Path(result_dir) / "output.txt"
        with open(result_file, 'wb') as f:
            f.write(stdout)
        
        return {
            "status": "completed",
            "result_file": str(result_file)
        }
```

3. Your plugin will be automatically discovered when the application starts

## Configuration Options

### Maximum Concurrent Workers

By default, Goblin Forge limits concurrent execution to 5 workers (Minions). To change this:

Edit `goblin_forge/core/minion_manager.py`:
```python
celery_app.conf.update(
    worker_concurrency=10,  # Change from 5 to desired number
    # ...other settings...
)
```

### Result Retention Period

By default, results are kept for 7 days. To change this:

Edit `goblin_forge/api/main.py`:
```python
minion_manager = MinionManager(retention_days=14)  # Change from 7 to desired number
```

### Customizing Frontend

The React frontend can be customized in various ways:

1. **Styling**: Edit `frontend/src/App.css` to change the appearance
2. **Layout**: Modify `frontend/src/App.js` to adjust the component layout
3. **Logo**: Replace the SVG logo in `frontend/public/goblin-logo.svg`

## Testing

### Running Tests

```bash
pytest
```

### Example Test Script

```python
# test_gadget.py
from goblin_forge.plugins.scanner_gadget import ScannerGadget
import asyncio
import tempfile
from pathlib import Path

def test_scanner_gadget():
    gadget = ScannerGadget()
    modes = gadget.get_modes()
    assert len(modes) > 0
    
    # Test execution
    with tempfile.TemporaryDirectory() as temp_dir:
        result = asyncio.run(gadget.execute("quick_scan", {"target": "localhost"}, temp_dir))
        assert result["status"] == "completed"
        assert Path(result["result_file"]).exists()
```

## Troubleshooting

### Common Issues

1. **Minions Not Running**
   - Check that Redis server is running
   - Verify Celery worker is started correctly
   - Check for permission issues in the results directory

2. **Plugins Not Appearing**
   - Ensure all plugins follow the BaseGadget interface
   - Check for import errors in plugin files
   - Restart the application to reload plugins

3. **Frontend Connection Issues**
   - Verify the API URL in `frontend/src/App.js` matches your server
   - Check for CORS issues in the browser console
   - Ensure the backend server is running

4. **Docker Issues**
   - Port conflicts: Check if ports 3000, 6379, or 8000 are already in use
   - Volume permissions: On Windows, you might need to use Docker's WSL2 backend
   - Container communication: Ensure containers can reach each other on the network

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the powerful API framework
- [React](https://reactjs.org/) for the frontend library
- [Celery](https://docs.celeryproject.org/) for distributed task processing
- [Bootstrap](https://getbootstrap.com/) for UI components