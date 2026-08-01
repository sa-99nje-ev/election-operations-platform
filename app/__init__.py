"""
Flask application factory module.

This module implements the application factory pattern, allowing for
multiple app instances with different configurations (dev, test, prod).
"""

from flask import Flask, jsonify
from sqlalchemy import text

from flask import Flask, jsonify
from sqlalchemy import text

from app.config.settings import get_config
from app.extensions import db, jwt
from app.auth import auth_bp


def create_app(config_name=None):
    """
    Application factory for creating Flask app instances.
    
    Args:
        config_name: Configuration environment name (development/testing/production).
                    If None, reads from FLASK_ENV environment variable.
    
    Returns:
        Configured Flask application instance.
    
    Example:
        >>> app = create_app('testing')
        >>> app.run()
    """
    # Create Flask application instance
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    
    # Register health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """
        Health check endpoint that verifies database connectivity.
        
        Returns:
            JSON response with status and database connection state.
            - 200: Service is healthy and database is connected
            - 503: Service is unhealthy (database connection failed)
        """
        try:
            # Test database connection
            with db.engine.connect() as connection:
                connection.execute(text('SELECT 1'))
            
            return jsonify({
                'status': 'healthy',
                'database': 'connected'
            }), 200
        
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': 'Database connection failed'
            }), 503
    
    return app
