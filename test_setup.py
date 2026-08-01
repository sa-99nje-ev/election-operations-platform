#!/usr/bin/env python3
"""
Quick test script to verify database setup works correctly.
"""

import os
import sys

# Set environment variables for testing
os.environ['FLASK_ENV'] = 'testing'
os.environ['SECRET_KEY'] = 'test-secret-key'
os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret'
os.environ['DATABASE_URL'] = 'sqlite:///test.db'
os.environ['REDIS_URL'] = 'redis://localhost:6379/0'

try:
    from app import create_app
    from app.extensions import db
    
    print("✓ Successfully imported app modules")
    
    # Create test app
    app = create_app('testing')
    print("✓ Application factory created app successfully")
    
    # Test app context
    with app.app_context():
        print("✓ App context created successfully")
        
        # Initialize database
        db.create_all()
        print("✓ Database tables created successfully")
        
        # Test database connection
        result = db.session.execute(db.text('SELECT 1')).scalar()
        assert result == 1
        print("✓ Database connection test passed")
        
        # Clean up
        db.session.remove()
        db.drop_all()
        print("✓ Database cleanup successful")
    
    # Test health check endpoint
    client = app.test_client()
    response = client.get('/health')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['database'] == 'connected'
    print("✓ Health check endpoint test passed")
    
    print("\n" + "=" * 60)
    print("SUCCESS: All database setup tests passed!")
    print("=" * 60)
    sys.exit(0)

except Exception as e:
    print(f"\n✗ ERROR: {str(e)}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
