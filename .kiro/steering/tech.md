# Technology Stack

## Backend Technologies

- **Framework**: Strands Agent framework for AI agent orchestration
- **Language**: Python 3.8+
- **Web Framework**: Flask for HTTP services and rendering
- **AI/ML**: AWS Bedrock (Claude models) for content generation
- **Concurrency**: ThreadPoolExecutor for parallel question generation
- **Caching**: Local file system with pickle serialization
- **Dependencies**: boto3, strands-agents, flask, requests, beautifulsoup4

## Frontend Technologies

- **Framework**: React 18+ with TypeScript
- **UI Library**: Material-UI (MUI) v6
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with PostCSS and Autoprefixer
- **Package Manager**: npm

## Infrastructure

- **Cloud Provider**: AWS (Bedrock for LLM services)
- **Authentication**: AWS credentials for Bedrock access
- **Storage**: Local file system for caching and data persistence
- **Deployment**: Shell scripts for service management

## Common Commands

### Setup and Installation
```bash
# Install all dependencies (auto-detects Python 3.10)
./setup.sh

# Install Python dependencies only
pip install -r requirements.txt

# Install frontend dependencies
cd frontend && npm install
```

### Development and Testing
```bash
# Start all services
./start.sh

# Start specific components
./start.sh backend flask    # Backend and Flask only
./start.sh frontend         # Frontend only

# Stop all services
./stop.sh

# Stop specific components  
./stop.sh backend           # Backend only

# Run tests
python run_tests.py         # All tests
python -m unittest tests.test_exam_tools  # Specific test module

# API testing
./test_api.sh
```

### Build and Deployment
```bash
# Frontend build
cd frontend && npm run build

# Frontend development server
cd frontend && npm run dev

# Frontend linting
cd frontend && npm run lint
```

## Configuration Requirements

- AWS credentials must be configured for Bedrock access
- Python virtual environment recommended
- Node.js 16+ and npm 8+ required for frontend
- Port 5000 (backend), 5006 (Flask), 5173 (frontend) should be available