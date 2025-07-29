# Project Structure

## Root Directory Organization

```
.
├── exam_generator/          # Backend service (Strands Agent)
├── flask-service/           # HTML rendering service
├── frontend/                # React frontend application
├── tests/                   # Test suite
├── cache/                   # Question caching (auto-generated)
├── quicksight_data/         # Analytics data exports
├── start.sh / stop.sh       # Service management scripts
└── requirements.txt         # Python dependencies
```

## Backend Service (`exam_generator/`)

```
exam_generator/
├── __init__.py
├── server.py               # Flask HTTP server and API endpoints
├── agent.py                # Strands Agent configuration and workflow
├── config.py               # Configuration management
├── tools/                  # Agent tools for question generation
│   ├── content_tools.py    # Content processing and validation
│   ├── exam_tools.py       # Core question generation logic
│   ├── reference_tools.py  # Reference material processing
│   └── render_tools.py     # HTML rendering integration
└── utils/                  # Utility modules
    ├── error_utils.py      # Error handling and HTTP responses
    ├── logging_utils.py    # Logging configuration
    └── task_manager.py     # Workflow tracking and evaluation
```

## Frontend Application (`frontend/`)

```
frontend/
├── src/
│   ├── components/         # React components
│   │   ├── ExamForm.tsx    # Main form for exam parameters
│   │   └── ResultDisplay.tsx # Results and status display
│   ├── contexts/           # React contexts
│   │   └── LanguageContext.tsx # Internationalization
│   ├── App.tsx             # Main application component
│   ├── translations.ts     # Language translations
│   └── dropdownOptions.ts  # Form option configurations
├── public/                 # Static assets
├── dist/                   # Build output (generated)
├── package.json            # Node.js dependencies and scripts
└── vite.config.ts          # Vite build configuration
```

## Flask Rendering Service (`flask-service/`)

```
flask-service/
├── app/
│   ├── __init__.py
│   ├── extensions/         # Markdown extensions
│   │   ├── checkbox.py     # Checkbox question rendering
│   │   ├── radio.py        # Radio button rendering
│   │   └── textbox.py      # Text input rendering
│   └── static/             # HTML templates and JavaScript
│       ├── app.js          # Client-side interaction logic
│       ├── base.html       # Base HTML template
│       └── wrapper.html    # Wrapper template
├── data/                   # Generated HTML files (runtime)
├── markdown-quiz-files/    # Markdown input files
└── main.py                 # Flask application entry point
```

## Testing Structure (`tests/`)

```
tests/
├── __init__.py
├── test_exam_tools.py      # Unit tests for question generation
└── test_workflow.py        # Integration tests for complete workflows
```

## Key Architectural Patterns

### Agent-Tool Pattern
- `agent.py` orchestrates the workflow using Strands Agent framework
- Individual tools in `tools/` directory handle specific tasks
- Tools are composable and can be called independently or in sequence

### Service Separation
- **Backend**: Handles AI logic and question generation
- **Flask Service**: Dedicated to HTML rendering and static file serving
- **Frontend**: Pure UI layer with no business logic

### Caching Strategy
- Questions cached in `cache/` directory using MD5 hashes
- Cache keys based on topic, difficulty, type, and reference materials
- 30-day TTL with automatic cleanup

### Error Handling Layers
- Tool-level: Exponential backoff retry for API calls
- Agent-level: Overall retry logic for workflow recovery
- HTTP-level: Standardized error responses in `error_utils.py`

### Configuration Management
- Centralized in `exam_generator/config.py`
- Separate configs for server, AWS, LLM, and exam parameters
- Environment-based credential management