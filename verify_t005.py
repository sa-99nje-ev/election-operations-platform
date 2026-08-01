"""
Verification script for Task T005: Flask Extensions Registration

This script verifies that:
1. JWTManager instance is created in extensions.py
2. JWT extension is initialized in application factory
3. JWT configuration is loaded from settings
4. Application starts without errors
5. JWT extension is ready for use
"""

import os
import sys

# Set test environment before importing app
os.environ['FLASK_ENV'] = 'testing'

# Ensure required environment variables are set for testing
if not os.getenv('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'sqlite:///test.db'
if not os.getenv('REDIS_URL'):
    os.environ['REDIS_URL'] = 'redis://localhost:6379/0'
if not os.getenv('SECRET_KEY'):
    os.environ['SECRET_KEY'] = 'test-secret-key-for-verification'
if not os.getenv('JWT_SECRET_KEY'):
    os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret-key-for-verification'

def verify_extensions_module():
    """Verify JWTManager is properly created in extensions.py"""
    print("=" * 70)
    print("TEST 1: Verify JWTManager instance in extensions.py")
    print("=" * 70)
    
    try:
        from app.extensions import db, jwt
        from flask_jwt_extended import JWTManager
        
        # Check db exists
        assert db is not None, "SQLAlchemy db instance not found"
        print("✓ SQLAlchemy db instance exists")
        
        # Check jwt exists
        assert jwt is not None, "JWTManager jwt instance not found"
        print("✓ JWTManager jwt instance exists")
        
        # Check jwt is correct type
        assert isinstance(jwt, JWTManager), f"jwt is not JWTManager instance, got {type(jwt)}"
        print("✓ jwt is a JWTManager instance")
        
        print("✓ TEST 1 PASSED: Extensions module properly configured\n")
        return True
        
    except Exception as e:
        print(f"✗ TEST 1 FAILED: {e}\n")
        return False


def verify_app_initialization():
    """Verify JWT extension is initialized in application factory"""
    print("=" * 70)
    print("TEST 2: Verify JWT initialization in application factory")
    print("=" * 70)
    
    try:
        from app import create_app
        
        # Create test app
        app = create_app('testing')
        
        assert app is not None, "Application creation failed"
        print("✓ Application created successfully")
        
        # Check JWT is in extensions
        assert 'jwt' in app.extensions, "JWT extension not registered in app.extensions"
        print("✓ JWT extension registered in app.extensions")
        
        print("✓ TEST 2 PASSED: JWT extension initialized in app factory\n")
        return True
        
    except Exception as e:
        print(f"✗ TEST 2 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def verify_jwt_configuration():
    """Verify JWT configuration is loaded from settings"""
    print("=" * 70)
    print("TEST 3: Verify JWT configuration from settings")
    print("=" * 70)
    
    try:
        from app import create_app
        from datetime import timedelta
        
        # Create test app
        app = create_app('testing')
        
        # Check JWT_SECRET_KEY
        assert app.config.get('JWT_SECRET_KEY') is not None, "JWT_SECRET_KEY not configured"
        print(f"✓ JWT_SECRET_KEY configured: {app.config.get('JWT_SECRET_KEY')[:10]}...")
        
        # Check JWT_ACCESS_TOKEN_EXPIRES
        access_expires = app.config.get('JWT_ACCESS_TOKEN_EXPIRES')
        assert access_expires is not None, "JWT_ACCESS_TOKEN_EXPIRES not configured"
        assert isinstance(access_expires, timedelta), "JWT_ACCESS_TOKEN_EXPIRES must be timedelta"
        print(f"✓ JWT_ACCESS_TOKEN_EXPIRES configured: {access_expires}")
        
        # Check JWT_REFRESH_TOKEN_EXPIRES
        refresh_expires = app.config.get('JWT_REFRESH_TOKEN_EXPIRES')
        assert refresh_expires is not None, "JWT_REFRESH_TOKEN_EXPIRES not configured"
        assert isinstance(refresh_expires, timedelta), "JWT_REFRESH_TOKEN_EXPIRES must be timedelta"
        print(f"✓ JWT_REFRESH_TOKEN_EXPIRES configured: {refresh_expires}")
        
        # Check JWT token location
        token_location = app.config.get('JWT_TOKEN_LOCATION')
        assert token_location is not None, "JWT_TOKEN_LOCATION not configured"
        print(f"✓ JWT_TOKEN_LOCATION configured: {token_location}")
        
        # Check JWT header settings
        header_name = app.config.get('JWT_HEADER_NAME')
        assert header_name == 'Authorization', f"JWT_HEADER_NAME should be 'Authorization', got {header_name}"
        print(f"✓ JWT_HEADER_NAME configured: {header_name}")
        
        header_type = app.config.get('JWT_HEADER_TYPE')
        assert header_type == 'Bearer', f"JWT_HEADER_TYPE should be 'Bearer', got {header_type}"
        print(f"✓ JWT_HEADER_TYPE configured: {header_type}")
        
        print("✓ TEST 3 PASSED: JWT configuration loaded correctly\n")
        return True
        
    except Exception as e:
        print(f"✗ TEST 3 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def verify_app_starts():
    """Verify application starts without errors"""
    print("=" * 70)
    print("TEST 4: Verify application starts without errors")
    print("=" * 70)
    
    try:
        from app import create_app
        
        # Create and test app context
        app = create_app('testing')
        
        with app.app_context():
            print("✓ Application context entered successfully")
            
            # Verify health check endpoint exists
            assert app.url_map is not None, "URL map not created"
            
            # Check if /health route exists
            routes = [str(rule) for rule in app.url_map.iter_rules()]
            assert '/health' in routes, "Health check endpoint not registered"
            print("✓ Health check endpoint registered")
        
        print("✓ TEST 4 PASSED: Application starts without errors\n")
        return True
        
    except Exception as e:
        print(f"✗ TEST 4 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def verify_jwt_ready():
    """Verify JWT extension is ready for use"""
    print("=" * 70)
    print("TEST 5: Verify JWT extension is ready for authentication endpoints")
    print("=" * 70)
    
    try:
        from app import create_app
        from flask_jwt_extended import create_access_token, create_refresh_token
        
        # Create test app
        app = create_app('testing')
        
        with app.app_context():
            # Test creating access token
            identity = {'user_id': 1, 'role': 'admin'}
            access_token = create_access_token(identity=identity)
            assert access_token is not None, "Failed to create access token"
            assert isinstance(access_token, str), "Access token should be string"
            print(f"✓ Successfully created access token: {access_token[:20]}...")
            
            # Test creating refresh token
            refresh_token = create_refresh_token(identity=identity)
            assert refresh_token is not None, "Failed to create refresh token"
            assert isinstance(refresh_token, str), "Refresh token should be string"
            print(f"✓ Successfully created refresh token: {refresh_token[:20]}...")
        
        print("✓ TEST 5 PASSED: JWT extension ready for authentication endpoints\n")
        return True
        
    except Exception as e:
        print(f"✗ TEST 5 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification tests"""
    print("\n" + "=" * 70)
    print("TASK T005 VERIFICATION: Flask Extensions Registration")
    print("=" * 70 + "\n")
    
    results = []
    
    # Run all tests
    results.append(("Extensions Module", verify_extensions_module()))
    results.append(("App Initialization", verify_app_initialization()))
    results.append(("JWT Configuration", verify_jwt_configuration()))
    results.append(("App Startup", verify_app_starts()))
    results.append(("JWT Ready", verify_jwt_ready()))
    
    # Summary
    print("=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:30} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\n✓ ALL TESTS PASSED - Task T005 Implementation Verified\n")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED - Please review errors above\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
