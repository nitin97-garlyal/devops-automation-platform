# DevOps-Automation-Platform

A production-grade, enterprise-ready DevOps automation platform built incrementally across realistic industry phases.

---

## Phase 1: Application Foundation & Health Checks

Phase 1 establishes the core application service, modular configuration, health probes (Kubernetes-ready), and an automated unit testing suite using `pytest`.

---

## Directory Structure

```text
devops-automation-platform/
├── app/
│   ├── __init__.py           # Application Factory (create_app), Blueprint registration, Error handlers
│   ├── config.py             # Environment configurations (Development, Testing, Production)
│   └── routes/
│       ├── __init__.py
│       ├── api.py            # API routes: index (/), /api/v1/ping, /api/v1/info
│       └── health.py         # DevOps probes: /health, /healthz (liveness), /ready (readiness)
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Pytest test fixtures (isolated test client, test app)
│   ├── test_api.py           # Unit tests for root, ping, info, and 404 handlers
│   └── test_health.py        # Unit tests for /health, /healthz, and /ready probes
├── .dockerignore             # Prevents build cache, venv, and secrets from entering Docker images
├── .gitignore                # Excludes virtualenvs, cache, credentials, logs from Git
├── requirements.txt          # Production dependencies (Flask, Gunicorn, Werkzeug)
├── requirements-dev.txt      # Testing and development dependencies (pytest, pytest-cov)
├── wsgi.py                   # Production WSGI entry point for Gunicorn
└── README.md                 # Complete documentation, run guides, and interview prep
```

---

## Endpoints

| Endpoint | Method | Purpose | DevOps Context |
| :--- | :--- | :--- | :--- |
| `/` | `GET` | API Root / Service Index | Route discovery and welcome banner |
| `/health` | `GET` | Health Status & Metadata | Load balancer checks, uptime, version, and metadata |
| `/healthz` | `GET` | Liveness Probe | Kubernetes liveness probe (restarts pod if failed) |
| `/ready` | `GET` | Readiness Probe | Kubernetes readiness probe (removes pod from service traffic if failed) |
| `/api/v1/ping` | `GET` | Latency / Connectivity Test | Rapid network connectivity check |
| `/api/v1/info` | `GET` | Host & Runtime Info | Multi-node cluster debugging & OS/runtime visibility |

---

## Local Setup & Execution

### 1. Prerequisites
- Linux OS (Ubuntu / Debian / CentOS / RHEL)
- Python 3.10+ (tested on Python 3.12)
- Git

### 2. Create and Activate Virtual Environment
```bash
# Create an isolated Python environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Install development and testing dependencies
pip install -r requirements-dev.txt
```

### 4. Run Unit Tests
```bash
# Run pytest with verbose output
pytest -v

# Run pytest with code coverage
pytest --cov=app tests/
```

### 5. Run Application Locally

#### Development Mode (Flask built-in server):
```bash
export FLASK_ENV=development
python3 -m app
```
The server will start at `http://127.0.0.1:5000`.

#### Production Mode (Gunicorn WSGI Server):
```bash
export FLASK_ENV=production
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

---

## Core DevOps Concepts Explained

### 1. Application Factory Pattern (`create_app`)
- **What it is**: A design pattern where the Flask application is created inside a function (`create_app()`) rather than as a global singleton.
- **Why it matters in DevOps**: Enables passing different configurations (`TestingConfig`, `ProductionConfig`, `DevelopmentConfig`) during automated tests, CI pipelines, and production deployments without modifying application code.

### 2. Liveness vs. Readiness Probes
- **Liveness Probe (`/healthz`)**: Checks if the container process is alive and responsive. If it fails, Kubernetes kills and restarts the container.
- **Readiness Probe (`/ready`)**: Checks if the application is ready to accept incoming user requests (e.g., database connections ready). If it fails, Kubernetes temporarily cuts traffic to that pod without killing it.

### 3. WSGI vs. Development HTTP Server
- **Development Server (`flask run`)**: Single-threaded or basic multi-threaded, not optimized for concurrent connections, lacks process management.
- **WSGI Server (`gunicorn`)**: Production-grade Web Server Gateway Interface that spawns pre-fork worker processes, efficiently handles concurrency, request queueing, and worker crashes.

### 4. Importance of `.dockerignore` and `.gitignore`
- `.dockerignore` prevents accidental inclusion of local virtual environments, `.git` history, and sensitive files (`.env`, `*.key`) into Docker images, keeping container layers slim and secure.
- `.gitignore` ensures secrets, runtime logs, and cache never leak into public/private git repositories.

---

## Troubleshooting Guide

### Issue 1: `command not found: pytest`
- **Cause**: Pytest is either not installed or the virtual environment is not activated.
- **Fix**:
  ```bash
  source .venv/bin/activate
  pip install -r requirements-dev.txt
  ```

### Issue 2: `Address already in use: Port 5000`
- **Cause**: Another service or previous Flask/Gunicorn process is bound to port 5000.
- **Troubleshooting command**:
  ```bash
  # Identify process listening on port 5000
  ss -tulpn | grep 5000
  # Or with lsof
  lsof -i :5000
  # Terminate process if appropriate
  kill -9 <PID>
  ```

### Issue 3: `ModuleNotFoundError: No module named 'app'`
- **Cause**: Python does not have the current directory in its `PYTHONPATH`.
- **Fix**: Run `pytest` or `python3` from the repository root directory, or set `export PYTHONPATH=.`.

---

## Common DevOps Interview Questions (Phase 1)

#### Q1: Why should an application have both a liveness probe and a readiness probe?
> **Answer**: If a service only has a liveness probe and experiences temporary overload or database latency, the probe might fail and cause Kubernetes to restart the container, which worsens the issue (causing a cascading restart storm). A readiness probe stops traffic from being routed to the container until it catches up, without restarting the process.

#### Q2: Why shouldn't you run `flask run` or `python app.py` in production?
> **Answer**: Flask's built-in development server is not hardened for production. It lacks robust connection pooling, process recycling, security controls, and resource management. In production, a WSGI application server like Gunicorn or uWSGI is used behind a reverse proxy like Nginx.

#### Q3: How do you prevent sensitive credentials from ever being committed to Git?
> **Answer**: 
> 1. Use `.gitignore` to explicitly ignore `.env`, `*.pem`, `*.key`, and secret files.
> 2. Use environment variables injected at runtime via orchestration tools (e.g., Kubernetes Secrets, HashiCorp Vault, AWS Secrets Manager).
> 3. Implement pre-commit hooks (e.g., `git-secrets`, `gitleaks`) and CI/CD secret scanning stages (e.g., Trivy).
