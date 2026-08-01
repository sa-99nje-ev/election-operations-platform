"""Simple test to verify JWT extension imports and initialization"""

import os
import sys

# Set test environment
os.environ['FLASK_ENV'] = 'testing'
os.environ['DATABASE_URL'] = 'sqlite:///instance/test.db'
os.environ['REDIS_URL'] = 'redis://localhost:6379/0'
os.environ['SECRET_KEY'] = 'test-secret'
os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret'

try:
    print("Testing imports...")
    
    # Test 1: Import extensions
    print("1. Importing extensions module...")
    from app.extensions import db, jwt
    print("   ✓ Successfully imported db and jwt from app.extensions")
    
    # Test 2: Verify JWT type
    print("2. Verifying jwt is JWTManager instance...")
    from flask_jwt_extended import JWTManager
    assert isinstance(jwt, JWTManager), f"jwt is {type(jwt)}, not JWTManager"
    print("   ✓ jwt is a JWTManager instance")
    
    # Test 3: Create app
    print("3. Creating Flask application...")
    from app import create_app
    app = create_app('testing')
    print("   ✓ Application created successfully")
    
    # Test 4: Verify JWT initialization
    print("4. Verifying JWT initialization in app...")
    assert 'jwt' in app.extensions, "JWT not in app.extensions"
    print("   ✓ JWT extension registered in app")
    
    # Test 5: Verify JWT config
    print("5. Verifying JWT configuration...")
    assert app.config.get('JWT_SECRET_KEY') is not None
    assert app.config.get('JWT_ACCESS_TOKEN_EXPIRES') is not None
    assert app.config.get('JWT_REFRESH_TOKEN_EXPIRES') is not None
    print("   ✓ JWT configuration loaded")
    
    # Test 6: Test token creation
    print("6. Testing JWT token creation...")
    with app.app_context():
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity={'user_id': 1})
        assert token is not None
        print(f"   ✓ Successfully created test token")
    
    print("\n✓ ALL TESTS PASSED - JWT Extension Registration Successful!")
    sys.exit(0)
    
except ImportError as e:
    print(f"\n✗ Import Error: {e}")
    print("\nNote: Flask-JWT-Extended may not be installed.")
    print("Run: pip install Flask-JWT-Extended==4.6.0")
    sys.exit(1)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
