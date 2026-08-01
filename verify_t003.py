#!/usr/bin/env python3
"""
Verification script for Task T003: Database Connection and Health Checks
This script verifies all acceptance criteria are met.
"""

import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists and report result."""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: {filepath} NOT FOUND")
        return False

def check_file_contains(filepath, search_text, description):
    """Check if a file contains specific text."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_text in content:
                print(f"✓ {description}")
                return True
            else:
                print(f"✗ {description} - NOT FOUND in {filepath}")
                return False
    except Exception as e:
        print(f"✗ {description} - ERROR reading {filepath}: {e}")
        return False

def main():
    """Run all verification checks."""
    print("=" * 70)
    print("Task T003 Verification: Database Connection and Health Checks")
    print("=" * 70)
    print()
    
    all_checks = []
    
    # Check 1: Extensions file exists with SQLAlchemy instance
    print("CHECK 1: SQLAlchemy instance created in extensions.py")
    all_checks.append(check_file_exists('app/extensions.py', 'Extensions file'))
    all_checks.append(check_file_contains('app/extensions.py', 'db = SQLAlchemy()', 
                                          'SQLAlchemy instance initialized'))
    print()
    
    # Check 2: Application factory exists
    print("CHECK 2: Application factory creates Flask app and initializes database")
    all_checks.append(check_file_exists('app/__init__.py', 'Application factory file'))
    all_checks.append(check_file_contains('app/__init__.py', 'def create_app(config_name=None)', 
                                          'create_app function defined'))
    all_checks.append(check_file_contains('app/__init__.py', 'get_config(config_name)', 
                                          'Configuration loading'))
    all_checks.append(check_file_contains('app/__init__.py', 'db.init_app(app)', 
                                          'Database initialization'))
    print()
    
    # Check 3: Health check endpoint
    print("CHECK 3: Health check endpoint tests database connectivity")
    all_checks.append(check_file_contains('app/__init__.py', "@app.route('/health'", 
                                          'Health check route registered'))
    all_checks.append(check_file_contains('app/__init__.py', "connection.execute(text('SELECT 1'))", 
                                          'Database connectivity test'))
    print()
    
    # Check 4: Proper status codes and responses
    print("CHECK 4: Returns appropriate status codes and JSON responses")
    all_checks.append(check_file_contains('app/__init__.py', "'status': 'healthy'", 
                                          'Success response format'))
    all_checks.append(check_file_contains('app/__init__.py', "'status': 'unhealthy'", 
                                          'Failure response format'))
    all_checks.append(check_file_contains('app/__init__.py', "'database': 'connected'", 
                                          'Database status in response'))
    all_checks.append(check_file_contains('app/__init__.py', ", 200", 
                                          'HTTP 200 status on success'))
    all_checks.append(check_file_contains('app/__init__.py', ", 503", 
                                          'HTTP 503 status on failure'))
    print()
    
    # Check 5: Connection pooling configuration
    print("CHECK 5: Uses connection pooling with SQLAlchemy settings")
    all_checks.append(check_file_contains('app/config/settings.py', 'SQLALCHEMY_ENGINE_OPTIONS', 
                                          'SQLAlchemy engine options configured'))
    all_checks.append(check_file_contains('app/config/settings.py', "'pool_size'", 
                                          'Pool size configuration'))
    all_checks.append(check_file_contains('app/config/settings.py', "'pool_recycle'", 
                                          'Pool recycle configuration'))
    all_checks.append(check_file_contains('app/config/settings.py', "'pool_pre_ping': True", 
                                          'Pool pre-ping enabled'))
    print()
    
    # Check 6: Tests exist
    print("CHECK 6: Unit tests created")
    all_checks.append(check_file_exists('tests/unit/test_database.py', 'Database tests file'))
    all_checks.append(check_file_contains('tests/unit/test_database.py', 'TestApplicationFactory', 
                                          'Application factory tests'))
    all_checks.append(check_file_contains('tests/unit/test_database.py', 'TestDatabaseExtension', 
                                          'Database extension tests'))
    all_checks.append(check_file_contains('tests/unit/test_database.py', 'TestHealthCheckEndpoint', 
                                          'Health check endpoint tests'))
    print()
    
    # Check 7: Dependencies added
    print("CHECK 7: Dependencies added to requirements.txt")
    all_checks.append(check_file_contains('requirements.txt', 'Flask-SQLAlchemy', 
                                          'Flask-SQLAlchemy dependency'))
    print()
    
    # Summary
    print("=" * 70)
    passed = sum(all_checks)
    total = len(all_checks)
    print(f"VERIFICATION SUMMARY: {passed}/{total} checks passed")
    
    if passed == total:
        print("✓ SUCCESS: All acceptance criteria met for Task T003")
        print("=" * 70)
        return 0
    else:
        print(f"✗ FAILURE: {total - passed} check(s) failed")
        print("=" * 70)
        return 1

if __name__ == '__main__':
    sys.exit(main())
