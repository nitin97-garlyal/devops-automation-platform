import os
from flask import Flask, jsonify
from app.config import config_by_name


def create_app(config_name=None):
    """
    Application factory pattern.
    Allows easy instantiation of the app with different configs (e.g. testing vs production).
    """
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    
    # Load configuration
    config_obj = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_obj)

    # Register Blueprints
    from app.routes.health import health_bp
    from app.routes.api import api_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(api_bp)

    # Global Error Handlers (JSON responses)
    @app.errorhandler(404)
    def resource_not_found(e):
        return jsonify({
            "error": "Not Found",
            "message": "The requested resource was not found on this server."
        }), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred on the server."
        }), 500

    return app


# WSGI application instance for gunicorn and development server
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    app.run(host=host, port=port)
