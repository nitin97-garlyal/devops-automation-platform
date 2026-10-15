# DevOps-Automation-Platform

A production-grade, enterprise-ready DevOps automation platform built incrementally across realistic industry phases.

---

## Phases Overview
- **[Phase 1: Application Foundation & Health Checks](#phase-1-application-foundation--health-checks)**
- **[Phase 2: Docker Containerization & Orchestration](#phase-2-docker-containerization--orchestration)**

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
│   ├── test_api.py           # Unit tests for root, ping, info, and 404/500 handlers
│   └── test_health.py        # Unit tests for /health, /healthz, and /ready probes
├── .dockerignore             # Excludes .git, .venv, cache, tests, keys, secrets from Docker context
├── .gitignore                # Excludes virtualenvs, cache, credentials, logs from Git
├── docker-compose.yml        # Local orchestration service definition
├── Dockerfile                # Production multi-step Docker image definition (non-root, Gunicorn)
├── requirements.txt          # Production runtime dependencies (Flask, Gunicorn, Werkzeug)
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
| `/healthz` | `GET` | Liveness Probe | Kubernetes liveness & Docker HEALTHCHECK (restarts pod/container if failed) |
| `/ready` | `GET` | Readiness Probe | Kubernetes readiness probe (removes pod from service traffic if failed) |
| `/api/v1/ping` | `GET` | Latency / Connectivity Test | Rapid network connectivity check |
| `/api/v1/info` | `GET` | Host & Runtime Info | Multi-node cluster debugging & OS/runtime visibility |

---

## Phase 1: Local Development & Unit Testing

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

### 4. Run Unit Tests & Coverage
```bash
# Run pytest with verbose output
pytest -v

# Run pytest with code coverage report
pytest --cov=app tests/
```

### 5. Run Application Locally

#### Development Mode (Flask built-in server):
```bash
export FLASK_ENV=development
python3 -m app
```

#### Production Mode (Gunicorn WSGI Server):
```bash
export FLASK_ENV=production
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

---

## Phase 2: Docker Containerization & Orchestration

### 1. Docker Architecture & Security Decisions
- **Base Image (`python:3.12-slim`)**: Debian slim provides glibc compatibility without the vulnerability footprint and bloat of full images (~150MB vs ~1GB).
- **Least Privilege (Non-root user `appuser:10001`)**: The container drops root privileges immediately after installing packages. If an attacker discovers an application vulnerability, they cannot easily escape the container or compromise the host kernel.
- **Layer Caching Optimization**: `requirements.txt` is copied and installed before copying application code. Changing application code will NOT invalidate the pip cache layer, keeping build times under 3 seconds.
- **Docker HEALTHCHECK**: Embedded healthcheck queries `http://localhost:5000/healthz` every 30s. Docker marks the container as `(healthy)` or `(unhealthy)`.
- **Gunicorn Production Tuning**: Uses 2 workers, 2 threads, 60s timeout, and forwards access/error logs directly to `stdout`/`stderr` (`-`), adhering to 12-factor application logging principles.

---

### 2. Standalone Docker Commands

#### Build the Image
```bash
docker build -t devops-automation-platform:latest .
```

#### Run Container in Background
```bash
docker run -d \
  --name devops-automation-app \
  -p 5000:5000 \
  devops-automation-platform:latest
```

#### View Running Container & Health Status
```bash
docker ps --filter "name=devops-automation-app"
```
*(Notice the `(healthy)` indicator in the `STATUS` column once the health check runs).*

#### Inspect Container Health Details
```bash
docker inspect --format='{{json .State.Health}}' devops-automation-app | jq
```

#### View Container Logs
```bash
# Stream live logs
docker logs -f devops-automation-app

# View last 50 lines with timestamps
docker logs --tail 50 -t devops-automation-app
```

#### Test Endpoints via cURL
```bash
# Root endpoint
curl -s http://127.0.0.1:5000/ | jq

# Health endpoint
curl -s http://127.0.0.1:5000/health | jq

# Liveness probe
curl -s http://127.0.0.1:5000/healthz | jq
```

#### Verify Non-Root User Execution
```bash
docker exec devops-automation-app whoami
# Output: appuser

docker exec devops-automation-app id
# Output: uid=10001(appuser) gid=10001(appgroup) groups=10001(appgroup)
```

#### Stop and Remove Container
```bash
docker stop devops-automation-app
docker rm devops-automation-app
```

---

### 3. Docker Compose (Recommended Local Workflow)

#### Start Services in Background
```bash
docker compose up -d
```

#### Check Service Status
```bash
docker compose ps
```

#### View Service Logs
```bash
docker compose logs -f app
```

#### Rebuild and Restart after Code Changes
```bash
docker compose up -d --build
```

#### Stop and Clean Up Services
```bash
docker compose down
```

---

## Core DevOps Concepts Explained

### 1. Application Factory Pattern (`create_app`)
- **What it is**: Instantiating the Flask application inside a factory function rather than at global module import.
- **Why it matters in DevOps**: Allows testing suites and production containers to inject configuration dynamically without modifying application code.

### 2. Liveness vs. Readiness Probes
- **Liveness Probe (`/healthz`)**: Used by Kubernetes & Docker `HEALTHCHECK`. If this fails, the container is deadlocked or crashed; the orchestrator terminates and replaces the container.
- **Readiness Probe (`/ready`)**: Determines if the app is ready for client traffic. If failed, traffic is diverted away from the container without killing it.

### 3. WSGI Server vs Development HTTP Server
- Development servers are single-process, blocking, and vulnerable to slowloris attacks.
- WSGI servers like Gunicorn manage pre-forked worker pools, distribute incoming socket connections across workers, and handle timeouts gracefully.

### 4. Why Non-Root User is Crucial in Docker
- By default, a process running as root inside a Docker container shares UID 0 with the host root. If a container breakout vulnerability exists (such as runc CVE-2019-5736 or filesystem escape), the attacker gains full root access to the underlying host. Running as a dedicated UID (e.g. 10001) mitigates this risk entirely.

---

## Troubleshooting Guide

### Issue 1: `port is already allocated` on Host Port 5000
- **Cause**: Another service or container is already bound to port 5000.
- **Troubleshooting command**:
  ```bash
  # Check host processes
  ss -tulpn | grep 5000
  # Check active docker containers
  docker ps --filter "publish=5000"
  ```
- **Fix**: Stop the conflicting container (`docker stop <container_id>`) or change the host port mapping in `docker-compose.yml` (e.g., `"5001:5000"`).

### Issue 2: Container Status Shows `(unhealthy)`
- **Cause**: The `HEALTHCHECK` command failed consecutively 3 times.
- **Troubleshooting command**:
  ```bash
  docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' devops-automation-app
  ```
- **Fix**: Verify Gunicorn is listening on `0.0.0.0:5000` (not `127.0.0.1` inside container) and that the `/healthz` route returns HTTP 200.

### Issue 3: `Permission denied` inside container
- **Cause**: Application tried writing to a directory owned by root.
- **Fix**: Ensure `WORKDIR /app` is owned by `appuser:appgroup` via `COPY --chown=appuser:appgroup`.

---

## Common DevOps Interview Questions (Phase 1 & 2)

#### Q1: Why should an application have both a liveness probe and a readiness probe?
> **Answer**: If a service only has a liveness probe and experiences temporary overload or database latency, the probe might fail and cause Kubernetes to restart the container, which worsens the issue (causing a cascading restart storm). A readiness probe stops traffic from being routed to the container until it catches up, without restarting the process.

#### Q2: Why is it bad practice to run containers as the default root user?
> **Answer**: Running as root violates the Principle of Least Privilege. Because the Linux kernel is shared between the container and host, any container breakout exploit (kernel vulnerabilities, volume mount exploits, or docker socket exposure) could grant an attacker root access to the entire host machine. Non-root users restrict damage to unprivileged space.

#### Q3: Why is `python:3.12-slim` generally preferred over `python:3.12-alpine` in Python production environments?
> **Answer**: While Alpine Linux uses `musl libc` resulting in slightly smaller images, standard Python wheels (packages like `numpy`, `cryptography`, or C-extensions) are compiled against `glibc`. On Alpine, pip often cannot use pre-compiled manylinux wheels and must compile from C source, which requires build dependencies (`gcc`, `make`), significantly increases build time, and can introduce subtle runtime bugs. Debian slim uses `glibc`, ensuring complete compatibility while maintaining a small footprint.

#### Q4: How does Docker build layer caching work, and how did we optimize the Dockerfile?
> **Answer**: Docker executes each instruction in a Dockerfile as a read-only image layer. If an instruction and its context haven't changed, Docker reuses the cached layer. By copying `requirements.txt` and running `pip install` before copying the rest of the application code, dependency installation is cached. Code edits only rebuild the final `COPY app/` layer, reducing build times from minutes to milliseconds.
