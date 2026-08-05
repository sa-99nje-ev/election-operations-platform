"""
Role-Based Access Control (RBAC) dependencies and permission helpers for FastAPI.
"""

from typing import List, Callable
from fastapi import HTTPException, status, Depends
from app.models.user import User
from app.api.deps import get_current_user

ROLES = {
    'ADMIN': 'Administrator',
    'ELECTION_OFFICER': 'Election_Officer',
    'POLLING_OFFICER': 'Polling_Officer',
    'CANDIDATE': 'Candidate',
    'VOTER': 'Voter'
}

ROLE_HIERARCHY = [
    'VOTER',
    'CANDIDATE',
    'POLLING_OFFICER',
    'ELECTION_OFFICER',
    'ADMIN'
]


def has_role_permission(user_role: str, required_role: str, allow_higher: bool = True) -> bool:
    user_role_upper = user_role.upper()
    required_role_upper = required_role.upper()

    if user_role_upper not in ROLES or required_role_upper not in ROLES:
        return False

    try:
        user_index = ROLE_HIERARCHY.index(user_role_upper)
        required_index = ROLE_HIERARCHY.index(required_role_upper)
    except ValueError:
        return False

    if allow_higher:
        return user_index >= required_index
    return user_index == required_index


def require_roles(allowed_roles: List[str]) -> Callable:
    """
    FastAPI dependency enforcing that current_user has one of allowed_roles.
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{current_user.role}' lacks permission for this operation"
            )
        return current_user
    return role_checker


# Shortcuts expected by domain.py
admin_required = require_roles(["ADMIN"])
officer_required = require_roles(["ADMIN", "ELECTION_OFFICER", "POLLING_OFFICER"])
election_officer_required = require_roles(["ADMIN", "ELECTION_OFFICER"])
polling_officer_required = require_roles(["ADMIN", "POLLING_OFFICER"])
candidate_required = require_roles(["ADMIN", "CANDIDATE"])
voter_required = require_roles(["ADMIN", "VOTER"])