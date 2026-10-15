import platform
from flask import Blueprint, jsonify, current_app

api_bp = Blueprint("api", __name__)


@api_bp.route("/", methods=["GET"])
def index():
    """Application welcome / root endpoint."""
    return jsonify({
        "message": "Welcome to the DevOps Automation Platform API",
        "app": current_app.config.get("APP_NAME", "DevOps-Automation-Platform"),
        "version": current_app.config.get("APP_VERSION", "1.0.0"),
        "endpoints": {
            "root": "/",
            "health": "/health",
            "liveness": "/healthz",
            "readiness": "/ready",
            "info": "/api/v1/info",
            "ping": "/api/v1/ping"
        }
    }), 200


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
