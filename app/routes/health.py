import time
from datetime import datetime, timezone
from flask import Blueprint, jsonify, current_app

health_bp = Blueprint("health", __name__)

# Track process start time for uptime calculation
START_TIME = time.time()


@health_bp.route("/health", methods=["GET"])
def health():
    """
    General Health Check Endpoint.
    Returns status 200 with application metadata, uptime, and system time.
    Suitable for load balancers and monitoring dashboards.
    """
    uptime_seconds = int(time.time() - START_TIME)
    return jsonify({
        "status": "healthy",
        "app": current_app.config.get("APP_NAME", "DevOps-Automation-Platform"),
        "version": current_app.config.get("APP_VERSION", "1.0.0"),
        "environment": current_app.config.get("ENVIRONMENT", "unknown"),
        "uptime_seconds": uptime_seconds,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200


@health_bp.route("/healthz", methods=["GET"])
def liveness():
    """
    Kubernetes Liveness Probe.
    Indicates whether the container is running.
    If this fails, the container orchestrator (e.g., K8s kubelet) will restart the pod.
    """
    return jsonify({"status": "alive"}), 200


@health_bp.route("/ready", methods=["GET"])
def readiness():
    """
    Kubernetes Readiness Probe.
    Indicates whether the application is ready to receive network traffic.
    If this fails, K8s removes the pod from service endpoints until it recovers.
    """
    # In future phases, check downstream dependencies (DB, Redis, etc.)
    return jsonify({"status": "ready"}), 200
