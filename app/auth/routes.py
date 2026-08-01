"""
Authentication API routes.

This module defines Flask routes for authentication operations including
login, logout, token refresh, and password management.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt
)
import uuid

from app.utils.password import (
    verify_encoded_password,
    validate_password_strength,
    PasswordTooWeakError,
    PasswordVerificationError
)
from app.utils.tokens import (
    create_tokens,
    create_access_token_from_refresh,
    revoke_token,
    TokenError,
    TokenExpiredError,
    TokenInvalidError
)
from app.utils.rbac import role_required

from .schemas import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    LogoutRequest,
    LogoutResponse,
    PasswordChangeRequest,
    PasswordChangeResponse,
    create_error_response
)

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT tokens.
    
    Request body should contain username and password.
    Returns access token (15 min expiry) and refresh token (7 day expiry).
    
    Example request:
    {
        "username": "admin",
        "password": "SecurePassword123!"
    }
    
    Example response:
    {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "bearer",
        "expires_in": 900
    }
    """
    try:
        # Parse and validate request
        data = request.get_json()
        if not data:
            return jsonify(create_error_response(
                "INVALID_CREDENTIALS",
                "Request body is required"
            )), 400
        
        # In a real application, you would validate with Pydantic/marshmallow
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify(create_error_response(
                "INVALID_CREDENTIALS",
                "Username and password are required"
            )), 400
        
        # Validate username format
        if not username.strip():
            return jsonify(create_error_response(
                "INVALID_CREDENTIALS",
                "Username cannot be empty"
            )), 400
        
        # TODO: In a real application, query database for user
        # user = User.query.filter_by(username=username).first()
        
        # For now, create mock user data
        # In production, you would:
        # 1. Query the database for the user
        # 2. Check if user exists and is active
        # 3. Verify password hash
        # 4. Implement account lockout for failed attempts
        
        # Mock user validation
        valid_users = {
            'admin': {
                'id': '11111111-1111-1111-1111-111111111111',
                'password_hash': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  # "secret"
                'role': 'ADMIN'
            },
            'election_officer': {
                'id': '22222222-2222-2222-2222-222222222222',
                'password_hash': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
                'role': 'ELECTION_OFFICER'
            },
            'voter': {
                'id': '33333333-3333-3333-3333-333333333333',
                'password_hash': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
                'role': 'VOTER'
            }
        }
        
        if username not in valid_users:
            current_app.logger.warning(f"Login attempt with unknown username: {username}")
            return jsonify(create_error_response(
                "INVALID_CREDENTIALS",
                "Invalid username or password"
            )), 401
        
        user_data = valid_users[username]
        
        # Verify password
        try:
            is_valid = verify_encoded_password(password, user_data['password_hash'])
        except PasswordVerificationError as e:
            current_app.logger.warning(f"Password verification error for user {username}: {e}")
            return jsonify(create_error_response(
                "INVALID_CREDENTIALS",
                "Invalid username or password"
            )), 401
        
        if not is_valid:
            current_app.logger.warning(f"Failed login attempt for user: {username}")
            return jsonify(create_error_response(
                "INVALID_CREDENTIALS",
                "Invalid username or password"
            )), 401
        
        # Create tokens
        try:
            user_id = uuid.UUID(user_data['id'])
            access_token, refresh_token = create_tokens(
                user_id=user_id,
                username=username,
                role=user_data['role']
            )
        except TokenError as e:
            current_app.logger.error(f"Token creation failed for user {username}: {e}")
            return jsonify(create_error_response(
                "TOKEN_INVALID",
                "Failed to create authentication tokens"
            )), 500
        
        # Log successful login
        current_app.logger.info(f"Successful login for user: {username}")
        
        # Create response
        response_data = LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=900
        )
        
        return jsonify(response_data.dict()), 200
        
    except Exception as e:
        current_app.logger.error(f"Unexpected error in login endpoint: {e}")
        return jsonify(create_error_response(
            "TOKEN_INVALID",
            "Internal server error"
        )), 500


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """
    Refresh access token using a valid refresh token.
    
    Request body should contain a refresh token.
    Returns a new access token.
    
    Example request:
    {
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
    
    Example response:
    {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "bearer",
        "expires_in": 900
    }
    """
    try:
        # Parse request
        data = request.get_json()
        if not data:
            return jsonify(create_error_response(
                "REFRESH_TOKEN_INVALID",
                "Request body is required"
            )), 400
        
        refresh_token = data.get('refresh_token')
        if not refresh_token:
            return jsonify(create_error_response(
                "REFRESH_TOKEN_INVALID",
                "Refresh token is required"
            )), 400
        
        # Create new access token from refresh token
        try:
            access_token = create_access_token_from_refresh(refresh_token)
        except TokenExpiredError:
            return jsonify(create_error_response(
                "REFRESH_TOKEN_EXPIRED",
                "Refresh token has expired"
            )), 401
        except TokenInvalidError:
            return jsonify(create_error_response(
                "REFRESH_TOKEN_INVALID",
                "Invalid refresh token"
            )), 401
        except TokenError as e:
            current_app.logger.error(f"Token refresh failed: {e}")
            return jsonify(create_error_response(
                "TOKEN_INVALID",
                "Failed to refresh token"
            )), 500
        
        # Create response
        response_data = RefreshTokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=900
        )
        
        return jsonify(response_data.dict()), 200
        
    except Exception as e:
        current_app.logger.error(f"Unexpected error in refresh endpoint: {e}")
        return jsonify(create_error_response(
            "TOKEN_INVALID",
            "Internal server error"
        )), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user and invalidate refresh token.
    
    Requires a valid access token in Authorization header.
    Request body should contain the refresh token to invalidate.
    
    Example request:
    {
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
    
    Example response:
    {
        "message": "Successfully logged out"
    }
    """
    try:
        # Parse request
        data = request.get_json()
        if not data:
            return jsonify(create_error_response(
                "REFRESH_TOKEN_INVALID",
                "Request body is required"
            )), 400
        
        refresh_token = data.get('refresh_token')
        if not refresh_token:
            return jsonify(create_error_response(
                "REFRESH_TOKEN_INVALID",
                "Refresh token is required"
            )), 400
        
        # Get current JWT claims
        jwt_data = get_jwt()
        token_id = jwt_data.get('jti')
        
        if token_id:
            # Revoke the current access token
            revoke_token(token_id)
            current_app.logger.info(f"Access token revoked: {token_id}")
        
        # TODO: In a real application, you would also:
        # 1. Decode the refresh token to get its jti
        # 2. Add it to a token blacklist in database/Redis
        # 3. Remove any associated session data
        
        # For now, just log the logout
        user_id = get_jwt_identity()
        current_app.logger.info(f"User {user_id} logged out")
        
        # Create response
        response_data = LogoutResponse(
            message="Successfully logged out"
        )
        
        return jsonify(response_data.dict()), 200
        
    except Exception as e:
        current_app.logger.error(f"Unexpected error in logout endpoint: {e}")
        return jsonify(create_error_response(
            "TOKEN_INVALID",
            "Internal server error"
        )), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Change user's password.
    
    Requires a valid access token in Authorization header.
    Request body should contain current and new password.
    
    Example request:
    {
        "current_password": "OldPassword123!",
        "new_password": "NewSecurePassword456!"
    }
    
    Example response:
    {
        "message": "Password successfully changed"
    }
    """
    try:
        # Parse and validate request
        data = request.get_json()
        if not data:
            return jsonify(create_error_response(
                "PASSWORD_MISMATCH",
                "Request body is required"
            )), 400
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify(create_error_response(
                "PASSWORD_MISMATCH",
                "Current password and new password are required"
            )), 400
        
        # Validate new password strength
        try:
            validate_password_strength(new_password)
        except PasswordTooWeakError as e:
            return jsonify(create_error_response(
                "PASSWORD_TOO_WEAK",
                str(e)
            )), 400
        
        # Get current user identity
        user_id = get_jwt_identity()
        
        # TODO: In a real application, you would:
        # 1. Query the database for the user
        # 2. Verify current password against stored hash
        # 3. Hash new password
        # 4. Update user record with new password hash
        # 5. Invalidate all existing tokens for security
        
        # For now, just return success
        current_app.logger.info(f"Password change requested for user: {user_id}")
        
        # Create response
        response_data = PasswordChangeResponse(
            message="Password successfully changed"
        )
        
        return jsonify(response_data.dict()), 200
        
    except Exception as e:
        current_app.logger.error(f"Unexpected error in change-password endpoint: {e}")
        return jsonify(create_error_response(
            "PASSWORD_MISMATCH",
            "Internal server error"
        )), 500


@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """
    Verify that a token is valid.
    
    Requires a valid access token in Authorization header.
    Returns basic token information.
    
    Example response:
    {
        "user_id": "11111111-1111-1111-1111-111111111111",
        "username": "admin",
        "role": "ADMIN",
        "issued_at": 1700000000,
        "expires_at": 1700000900
    }
    """
    try:
        # Get JWT claims
        jwt_data = get_jwt()
        
        # Extract information
        token_info = {
            'user_id': get_jwt_identity(),
            'username': jwt_data.get('username'),
            'role': jwt_data.get('role'),
            'issued_at': jwt_data.get('iat'),
            'expires_at': jwt_data.get('exp')
        }
        
        return jsonify(token_info), 200
        
    except Exception as e:
        current_app.logger.error(f"Unexpected error in verify endpoint: {e}")
        return jsonify(create_error_response(
            "TOKEN_INVALID",
            "Internal server error"
        )), 500


@auth_bp.route('/protected-test', methods=['GET'])
@jwt_required()
@role_required('ADMIN')
def protected_test():
    """
    Test endpoint for RBAC-protected routes.
    
    Requires ADMIN role.
    """
    return jsonify({
        'message': 'You have accessed an admin-protected endpoint',
        'user': get_jwt_identity()
    }), 200