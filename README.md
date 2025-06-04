# Flask Environment Display Application

A production-ready Flask application that displays Kubernetes environment information with comprehensive CI/CD pipeline.

## Features

- 🐍 Flask web application with environment information display
- 🔍 Health check endpoints for Kubernetes probes
- 📊 System metrics and resource monitoring
- 🎨 Customizable UI with environment-based theming
- 🔒 Security scanning and vulnerability checks
- 🧪 Comprehensive test suite with coverage reporting

## Development Setup

### Prerequisites

- Python 3.10+ 
- pip package manager

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nodefront
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Run the application**
   ```bash
   cd src
   python app.py
   ```

   The application will be available at `http://localhost:3000`

### Code Quality Tools

This project uses several tools to maintain code quality:

#### Linting and Formatting
- **flake8**: Python linting and style checking
- **black**: Code formatting (line length: 127 characters)
- **isort**: Import sorting and organization

#### Testing
- **pytest**: Testing framework
- **pytest-flask**: Flask-specific testing utilities
- **pytest-cov**: Code coverage reporting

#### Security
- **bandit**: Security vulnerability scanning
- **safety**: Dependency vulnerability checking
- **pip-audit**: Additional dependency auditing

### Running Quality Checks Locally

```bash
# Linting
flake8 src/

# Code formatting check
black --check --diff src/ tests/

# Import sorting check
isort --check-only --diff src/ tests/

# Run tests with coverage
pytest tests/ -v --cov=src --cov-report=term-missing

# Security scan
bandit -r src/

# Dependency vulnerability check
safety check
```

### Auto-formatting Code

```bash
# Format code with black
black src/ tests/

# Sort imports
isort src/ tests/
```

## CI/CD Pipeline

### Main CI/CD Workflow (`.github/workflows/cicd.yaml`)

Triggered on pushes to `main` branch affecting:
- `src/**`
- `Dockerfile`
- `requirements.txt`
- `requirements-dev.txt`

**CI Steps:**
1. **Python Setup**: Python 3.11 with pip caching
2. **Dependency Installation**: Install production and development dependencies
3. **Code Linting**: flake8 with syntax error detection and style checking
4. **Code Formatting**: black formatting verification
5. **Import Sorting**: isort import organization check
6. **Testing**: Automated test execution with fallback test creation
7. **Security Scanning**: bandit security vulnerability detection
8. **Docker Build**: Multi-platform Docker image build and push

**CD Steps:**
1. **Kustomize Update**: Update Kubernetes deployment image tags
2. **Git Commit**: Commit updated configurations
3. **ArgoCD Sync**: Trigger ArgoCD application synchronization

### Pull Request Checks (`.github/workflows/pr-checks.yaml`)

Triggered on pull requests to `main` branch with comprehensive quality gates:

**Multi-Python Testing:**
- Tests against Python 3.10, 3.11, and 3.12
- Ensures compatibility across Python versions

**Quality Checks:**
- Code linting and formatting verification
- Test execution with coverage reporting
- Security vulnerability scanning
- Dependency audit and vulnerability checks

**Coverage Reporting:**
- Codecov integration for coverage tracking
- Minimum coverage threshold enforcement

## Project Structure

```
.
├── src/
│   ├── app.py              # Main Flask application
│   └── gunicorn.conf.py    # Gunicorn configuration
├── tests/
│   ├── __init__.py
│   └── test_app.py         # Comprehensive test suite
├── .github/workflows/
│   ├── cicd.yaml           # Main CI/CD pipeline
│   └── pr-checks.yaml      # Pull request quality checks
├── kustomize/              # Kubernetes configurations
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── pyproject.toml          # Tool configurations
├── .flake8                 # Flake8 configuration
└── Dockerfile              # Container configuration
```

## Configuration Files

### Python Tool Configuration

- **pyproject.toml**: Centralized configuration for black, isort, pytest, and bandit
- **.flake8**: Flake8 linting configuration with project-specific rules
- **requirements-dev.txt**: Development dependencies including testing and quality tools

### Key Configuration Highlights

- **Line Length**: 127 characters (optimized for modern displays)
- **Python Target**: Python 3.11+ compatibility
- **Test Coverage**: 80% minimum coverage requirement
- **Security**: Comprehensive vulnerability scanning with bandit and safety

## Environment Variables

The application supports various environment variables for configuration:

- `ENVIRONMENT`: Deployment environment (development/staging/production)
- `BG_COLOR`: Background color for the UI theme
- `FONT_COLOR`: Font color for the UI theme
- `POD_NAME`: Kubernetes pod name
- `POD_NAMESPACE`: Kubernetes namespace
- `FROM_FIELD`: Host IP information

## API Endpoints

- `GET /`: Main environment display page
- `GET /healthcheck.html`: Health check endpoint for Kubernetes probes
- `GET /api/env`: JSON API endpoint for environment data

## Docker Deployment

The application includes a production-ready Dockerfile and is automatically built and pushed to Docker Hub through the CI/CD pipeline.

## Kubernetes Integration

- Kustomize-based configuration management
- ArgoCD GitOps deployment
- Health check endpoints for liveness and readiness probes
- Environment-specific overlays (development/staging/production)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the code quality standards
4. Run local quality checks
5. Submit a pull request

The PR checks will automatically verify code quality, run tests, and check for security vulnerabilities.

## License

[Add your license information here]
