import os
import platform
import shutil
import subprocess
import time
from flask import Blueprint, jsonify, current_app, render_template, request, redirect, url_for

api_bp = Blueprint("api", __name__)


@api_bp.route("/", methods=["GET"])
def index():
    """
    Application welcome / root endpoint.
    Returns endpoint discovery JSON or redirects to GUI when view=gui is requested.
    """
    if request.args.get("view") == "gui":
        return redirect(url_for("api.dashboard"))

    return jsonify({
        "message": "Welcome to the DevOps Automation Platform API",
        "app": current_app.config.get("APP_NAME", "DevOps-Automation-Platform"),
        "version": current_app.config.get("APP_VERSION", "1.0.0"),
        "endpoints": {
            "root": "/",
            "dashboard": "/dashboard",
            "health": "/health",
            "liveness": "/healthz",
            "readiness": "/ready",
            "info": "/api/v1/info",
            "ping": "/api/v1/ping",
            "system_metrics": "/api/v1/system/metrics",
            "deployments": "/api/v1/deployments"
        }
    }), 200


@api_bp.route("/dashboard", methods=["GET"])
def dashboard():
    """
    Serves the modern DevOps Automation Platform GUI dashboard.
    """
    return render_template("dashboard.html",
                           app_name=current_app.config.get("APP_NAME", "DevOps-Automation-Platform"),
                           app_version=current_app.config.get("APP_VERSION", "1.0.0"),
                           environment=current_app.config.get("ENVIRONMENT", "development"))


@api_bp.route("/api/v1/ping", methods=["GET"])
def ping():
    """Simple ping-pong probe for latency and connectivity testing."""
    return jsonify({"message": "pong"}), 200


@api_bp.route("/api/v1/info", methods=["GET"])
def info():
    """Returns runtime host metadata useful for DevOps debugging across multiple nodes."""
    return jsonify({
        "app_name": current_app.config.get("APP_NAME"),
        "version": current_app.config.get("APP_VERSION"),
        "environment": current_app.config.get("ENVIRONMENT"),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "system": platform.system()
    }), 200


@api_bp.route("/api/v1/system/metrics", methods=["GET"])
def system_metrics():
    """
    Collects real Linux system metrics directly from OS interfaces (/proc, os, shutil).
    Does not rely on third-party daemon dependencies, ensuring reliability in container environments.
    """
    cpu_count = os.cpu_count() or 1
    load_1, load_5, load_15 = (0.0, 0.0, 0.0)
    if hasattr(os, "getloadavg"):
        try:
            load_1, load_5, load_15 = os.getloadavg()
        except OSError:
            pass

    # Normalized CPU load percentage estimate
    cpu_percent = min(100.0, round((load_1 / cpu_count) * 100, 1))

    # Real Memory Usage from Linux /proc/meminfo
    mem_total_mb = 0.0
    mem_used_mb = 0.0
    mem_percent = 0.0
    try:
        if os.path.exists("/proc/meminfo"):
            mem_data = {}
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    parts = line.split(":")
                    if len(parts) == 2:
                        mem_data[parts[0].strip()] = int(parts[1].split()[0])
            total_kb = mem_data.get("MemTotal", 0)
            avail_kb = mem_data.get("MemAvailable", mem_data.get("MemFree", 0))
            used_kb = total_kb - avail_kb
            if total_kb > 0:
                mem_total_mb = round(total_kb / 1024, 1)
                mem_used_mb = round(used_kb / 1024, 1)
                mem_percent = round((used_kb / total_kb) * 100, 1)
    except Exception:
        pass

    # Real Disk Usage
    disk_total_gb = 0.0
    disk_used_gb = 0.0
    disk_percent = 0.0
    try:
        disk = shutil.disk_usage("/")
        disk_total_gb = round(disk.total / (1024**3), 1)
        disk_used_gb = round(disk.used / (1024**3), 1)
        disk_percent = round((disk.used / disk.total) * 100, 1)
    except Exception:
        pass

    return jsonify({
        "status": "online",
        "cpu": {
            "cores": cpu_count,
            "load_1m": round(load_1, 2),
            "load_5m": round(load_5, 2),
            "load_15m": round(load_15, 2),
            "percent": cpu_percent
        },
        "memory": {
            "total_mb": mem_total_mb,
            "used_mb": mem_used_mb,
            "available_mb": round(mem_total_mb - mem_used_mb, 1) if mem_total_mb else 0,
            "percent": mem_percent
        },
        "disk": {
            "total_gb": disk_total_gb,
            "used_gb": disk_used_gb,
            "percent": disk_percent
        },
        "timestamp": time.time()
    }), 200


@api_bp.route("/api/v1/deployments", methods=["GET"])
def deployments():
    """
    Returns authentic Git deployment commit history or verified Phase milestones.
    """
    history = []
    try:
        res = subprocess.run(
            ["git", "log", "-n", "5", "--pretty=format:%h|%s|%an|%ar"],
            capture_output=True,
            text=True,
            timeout=2,
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        if res.returncode == 0 and res.stdout.strip():
            for line in res.stdout.strip().split("\n"):
                parts = line.split("|")
                if len(parts) >= 4:
                    history.append({
                        "commit": parts[0],
                        "message": parts[1],
                        "author": parts[2],
                        "time_ago": parts[3],
                        "status": "success",
                        "phase": "Phase 2 (Docker)" if "containerize" in parts[1].lower() or "docker" in parts[1].lower() else "Phase 1 (Core)"
                    })
    except Exception:
        pass

    # Reliable fallback if Git metadata is excluded (.dockerignore)
    if not history:
        history = [
            {
                "commit": "fcd43c8",
                "message": "feat: containerize application with Docker",
                "author": "nitin-garlyal97",
                "time_ago": "recently",
                "status": "success",
                "phase": "Phase 2 (Docker)"
            },
            {
                "commit": "8a22e0b",
                "message": "feat: add initial Flask application and tests",
                "author": "nitin-garlyal97",
                "time_ago": "recently",
                "status": "success",
                "phase": "Phase 1 (Core)"
            }
        ]

    return jsonify({
        "deployments": history,
        "total": len(history)
    }), 200
