"""
Role-Based Access Control (RBAC) decorators and utilities.

This module provides decorators for enforcing role-based access control
on Flask routes and API endpoints.
"""

from functools import wraps
from typing import List, Optional, Callable, Any
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt
import uuid

from .tokens import TokenError


class RBACError(Exception):
    """Base exception for RBAC-related errors."""
    pass


class PermissionDeniedError(RBACError):
    """Raised when a user lacks required permissions."""
    pass


class InvalidRoleError(RBACError):
    """Raised when an invalid role is specified."""
    pass


# Role definitions
ROLES = {
    'ADMIN': 'Administrator',
    'ELECTION_OFFICER': 'Election_Officer',
    'POLLING_OFFICER': 'Polling_Officer',
    'CANDIDATE': 'Candidate',
    'VOTER': 'Voter'
}

# Role hierarchy (higher roles have more permissions)
ROLE_HIERARCHY = [
    'VOTER',
    'CANDIDATE',
    'POLLING_OFFICER',
    'ELECTION_OFFICER',
    'ADMIN'
]


def role_required(required_role: str, allow_higher: bool = True):
    """
    Decorator to require a specific role or higher.
    
    Args:
        required_role: Minimum role required (case-insensitive)
        allow_higher: If True, users with higher roles are also allowed
        
    Returns:
        Decorator function
        
    Raises:
        InvalidRoleError: If required_role is not a valid role
    """
    # Normalize role name
    required_role_upper = required_role.upper()
    
    # Validate role
    if required_role_upper not in ROLES:
        valid_roles = ', '.join(ROLES.keys())
        raise InvalidRoleError(
            f"Invalid role '{required_role}'. Valid roles are: {valid_roles}"
        )
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verify JWT is present
            verify_jwt_in_request()
            
            # Get JWT claims
            jwt_data = get_jwt()
            
            # Extract user role from JWT
            user_role = jwt_data.get('role', '').upper()
            
            # Check if user has required role
            if not has_role_permission(user_role, required_role_upper, allow_higher):
                current_app.logger.warning(
                    f"Permission denied: User role '{user_role}' "
                    f"does not meet required role '{required_role_upper}' "
                    f"(allow_higher={allow_higher})"
                )
                return jsonify({
                    'error': {
                        'code': 'PERMISSION_DENIED',
                        'message': f"Role '{ROLES.get(user_role, user_role)}' "
                                 f"does not have permission to access this resource"
                    }
                }), 403
            
            # Check resource ownership for certain endpoints
            # This is a simplified example - actual implementation would be more specific
            try:
                check_resource_ownership(jwt_data, request, *args, **kwargs)
            except PermissionDeniedError as e:
                current_app.logger.warning(
                    f"Resource ownership check failed: {e}"
                )
                return jsonify({
                    'error': {
                        'code': 'RESOURCE_OWNERSHIP_DENIED',
                        'message': str(e)
                    }
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def has_role_permission(
    user_role: str,
    required_role: str,
    allow_higher: bool = True
) -> bool:
    """
    Check if a user role meets permission requirements.
    
    Args:
        user_role: User's role (case-insensitive)
        required_role: Minimum required role (case-insensitive)
        allow_higher: If True, higher roles are allowed
        
    Returns:
        bool: True if user has permission, False otherwise
    """
    # Normalize roles
    user_role_upper = user_role.upper()
    required_role_upper = required_role.upper()
    
    # Check if roles are valid
    if user_role_upper not in ROLES:
        return False
    
    if required_role_upper not in ROLES:
        return False
    
    # Get role indices in hierarchy
    try:
        user_index = ROLE_HIERARCHY.index(user_role_upper)
        required_index = ROLE_HIERARCHY.index(required_role_upper)
    except ValueError:
        return False
    
    if allow_higher:
        # User must have required role or higher
        return user_index >= required_index
    else:
        # User must have exactly the required role
        return user_index == required_index


def admin_required(f):
    """Decorator to require ADMIN role."""
    return role_required('ADMIN')(f)


def election_officer_required(f):
    """Decorator to require ELECTION_OFFICER role or higher."""
    return role_required('ELECTION_OFFICER')(f)


def polling_officer_required(f):
    """Decorator to require POLLING_OFFICER role or higher."""
    return role_required('POLLING_OFFICER')(f)


def candidate_required(f):
    """Decorator to require CANDIDATE role or higher."""
    return role_required('CANDIDATE')(f)


def voter_required(f):
    """Decorator to require VOTER role or higher."""
    return role_required('VOTER')(f)


def check_resource_ownership(
    jwt_data: dict,
    request_obj: Any,
    *args,
    **kwargs
) -> None:
    """
    Check if user owns or has access to the requested resource.
    
    This is a simplified implementation. In a real application, you would
    have more specific checks based on resource types and relationships.
    
    Args:
        jwt_data: JWT claims dictionary
        request_obj: Flask request object
        *args: Route arguments
        **kwargs: Route keyword arguments
        
    Raises:
        PermissionDeniedError: If user doesn't own the resource
    """
    # Extract user information from JWT
    user_id = jwt_data.get('sub')
    user_role = jwt_data.get('role', '').upper()
    
    if not user_id:
        raise PermissionDeniedError("User ID not found in token")
    
    # Try to parse user ID as UUID
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise PermissionDeniedError(f"Invalid user ID format: {user_id}")
    
    # Check specific resource ownership based on route
    # This is a placeholder - actual implementation would be more comprehensive
    
    # Example: Check if user is accessing their own profile
    if request_obj.endpoint and 'profile' in request_obj.endpoint.lower():
        # Get resource ID from request
        resource_id = kwargs.get('user_id') or request_obj.args.get('user_id')
        
        if resource_id:
            try:
                resource_uuid = uuid.UUID(resource_id)
                if resource_uuid != user_uuid and user_role != 'ADMIN':
                    raise PermissionDeniedError(
                        f"User {user_id} does not own resource {resource_id}"
                    )
            except ValueError:
                # If resource ID is not a UUID, we can't compare
                pass
    
    # Example: Check constituency access for candidates/election officers
    if user_role in ['CANDIDATE', 'ELECTION_OFFICER', 'POLLING_OFFICER']:
        # These roles may have constituency-based restrictions
        # In a real implementation, you would check database relationships
        pass


def get_allowed_roles(user_role: str) -> List[str]:
    """
    Get all roles that a user with the given role can manage/access.
    
    Args:
        user_role: User's role (case-insensitive)
        
    Returns:
        List[str]: List of role names the user can manage
    """
    user_role_upper = user_role.upper()
    
    if user_role_upper not in ROLE_HIERARCHY:
        return []
    
    # Get user's position in hierarchy
    try:
        user_index = ROLE_HIERARCHY.index(user_role_upper)
    except ValueError:
        return []
    
    # Admin can manage all roles
    if user_role_upper == 'ADMIN':
        return list(ROLES.keys())
    
    # Election officers can manage lower roles
    if user_role_upper == 'ELECTION_OFFICER':
        return [role for role in ROLE_HIERARCHY if role in ['VOTER', 'CANDIDATE', 'POLLING_OFFICER']]
    
    # Polling officers can only manage voters
    if user_role_upper == 'POLLING_OFFICER':
        return ['VOTER']
    
    # Candidates and voters cannot manage any roles
    return []


def can_manage_role(manager_role: str, target_role: str) -> bool:
    """
    Check if a manager can manage users with the target role.
    
    Args:
        manager_role: Manager's role (case-insensitive)
        target_role: Target role to manage (case-insensitive)
        
    Returns:
        bool: True if manager can manage target role, False otherwise
    """
    manager_role_upper = manager_role.upper()
    target_role_upper = target_role.upper()
    
    # Check if roles are valid
    if manager_role_upper not in ROLES or target_role_upper not in ROLES:
        return False
    
    # Get allowed roles for manager
    allowed_roles = get_allowed_roles(manager_role_upper)
    
    return target_role_upper in allowed_roles