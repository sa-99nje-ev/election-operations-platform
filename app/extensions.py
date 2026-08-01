"""
Flask extensions module.

This module initializes and exports Flask extensions that can be imported
and used throughout the application. Extensions are initialized here but
configured in the application factory (app/__init__.py).
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Initialize SQLAlchemy extension
# This will be configured with the Flask app in the application factory
db = SQLAlchemy()

# Initialize JWT extension
# This will be configured with the Flask app in the application factory
jwt = JWTManager()
