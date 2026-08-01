"""
Unit tests for database connection and health check functionality.

Tests the application factory, database initialization, and health check endpoint.
"""

import pytest
from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    """
    Create and configure a test application instance.
    
    Uses testing configuration which may use a separate test database.
    """
    app = create_app('testing')
    
    # Create application context
    with app.app_context():
        # Create tables for testing
        db.create_all()
        yield app
        
        # Cleanup
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """
    Create a test client for the Flask application.
    
    Args:
        app: Flask application instance from app fixture.
    
    Returns:
        Flask test client for making requests.
    """
    return app.test_client()


class TestApplicationFactory:
    """Tests for the Flask application factory."""
    
    def test_create_app_with_testing_config(self):
        """Test that create_app creates a Flask app with testing configuration."""
        app = create_app('testing')
        
        assert app is not None
        assert app.config['TESTING'] is True
        assert app.config['DEBUG'] is True
    
    def test_create_app_with_development_config(self):
        """Test that create_app creates a Flask app with development configuration."""
        app = create_app('development')
        
        assert app is not None
        assert app.config['DEBUG'] is True
        assert app.config['TESTING'] is False
    
    def test_create_app_with_default_config(self):
        """Test that create_app uses default config when no environment specified."""
        app = create_app()
        
        assert app is not None
        # Default should be development
        assert app.config['DEBUG'] is True


class TestDatabaseExtension:
    """Tests for database extension initialization."""
    
    def test_db_extension_initialized(self, app):
        """Test that SQLAlchemy extension is properly initialized."""
        with app.app_context():
            assert db.engine is not None
            assert db.session is not None
    
    def test_database_connection(self, app):
        """Test that database connection can be established."""
        with app.app_context():
            # Should not raise exception
            result = db.session.execute(db.text('SELECT 1')).scalar()
            assert result == 1


class TestHealthCheckEndpoint:
    """Tests for the /health endpoint."""
    
    def test_health_check_success(self, client, app):
        """Test health check returns 200 when database is connected."""
        with app.app_context():
            response = client.get('/health')
            
            assert response.status_code == 200
            
            data = response.get_json()
            assert data['status'] == 'healthy'
            assert data['database'] == 'connected'
    
    def test_health_check_json_response(self, client, app):
        """Test health check returns proper JSON content type."""
        with app.app_context():
            response = client.get('/health')
            
            assert response.content_type == 'application/json'
    
    def test_health_check_database_error(self, app, monkeypatch):
        """Test health check returns 503 when database connection fails."""
        client = app.test_client()
        
        def mock_execute(*args, **kwargs):
            raise Exception("Database connection failed")
        
        with app.app_context():
            # Mock database connection to raise exception
            monkeypatch.setattr('app.extensions.db.engine.connect', 
                              lambda: MockConnection(mock_execute))
            
            response = client.get('/health')
            
            assert response.status_code == 503
            
            data = response.get_json()
            assert data['status'] == 'unhealthy'
            assert data['error'] == 'Database connection failed'


class MockConnection:
    """Mock database connection for testing error scenarios."""
    
    def __init__(self, execute_func):
        self.execute = execute_func
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass
