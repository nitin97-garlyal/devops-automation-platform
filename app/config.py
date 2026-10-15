import os

class Config:
    """Base application configuration."""
    APP_NAME = os.getenv("APP_NAME", "DevOps-Automation-Platform")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    ENVIRONMENT = os.getenv("FLASK_ENV", "development")
    TESTING = False
    DEBUG = False


class DevelopmentConfig(Config):
    """Development environment specific configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing environment specific configuration."""
    TESTING = True
    DEBUG = True


class ProductionConfig(Config):
    """Production environment specific configuration."""
    DEBUG = False
    TESTING = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
