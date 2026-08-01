"""
Utility modules for common application functionality.

This package contains shared utilities for password hashing, JWT management,
and other cross-cutting concerns.
"""

"""
Utility modules for common application functionality.

This package contains shared utilities for password hashing, JWT management,
and other cross-cutting concerns.
"""

from .password import (
    hash_password,
    verify_password,
    is_password_strong,
    validate_password_strength,
    needs_rehash,
    hash_and_encode_password,
    verify_encoded_password,
    PasswordError,
    PasswordTooWeakError,
    PasswordVerificationError,
)

"""
Utility modules for common application functionality.

This package contains shared utilities for password hashing, JWT management,
and other cross-cutting concerns.
"""

from .password import (
    hash_password,
    verify_password,
    is_password_strong,
    validate_password_strength,
    needs_rehash,
    hash_and_encode_password,
    verify_encoded_password,
    PasswordError,
    PasswordTooWeakError,
    PasswordVerificationError,
)

from .tokens import (
    create_tokens,
    decode_jwt_token,
    get_token_identity,
    get_token_claims,
    get_current_user_role,
    is_token_expired,
    get_token_expiry,
    create_access_token_from_refresh,
    revoke_token,
    is_token_revoked,
    clear_token_blacklist,
    TokenError,
    TokenExpiredError,
    TokenInvalidError,
    TokenRevokedError,
)

from .rbac import (
    role_required,
    admin_required,
    election_officer_required,
    polling_officer_required,
    candidate_required,
    voter_required,
    has_role_permission,
    check_resource_ownership,
    get_allowed_roles,
    can_manage_role,
    RBACError,
    PermissionDeniedError,
    InvalidRoleError,
    ROLES,
    ROLE_HIERARCHY,
)

__all__ = [
    # Password utilities
    'hash_password',
    'verify_password',
    'is_password_strong',
    'validate_password_strength',
    'needs_rehash',
    'hash_and_encode_password',
    'verify_encoded_password',
    'PasswordError',
    'PasswordTooWeakError',
    'PasswordVerificationError',
    
    # Token utilities
    'create_tokens',
    'decode_jwt_token',
    'get_token_identity',
    'get_token_claims',
    'get_current_user_role',
    'is_token_expired',
    'get_token_expiry',
    'create_access_token_from_refresh',
    'revoke_token',
    'is_token_revoked',
    'clear_token_blacklist',
    'TokenError',
    'TokenExpiredError',
    'TokenInvalidError',
    'TokenRevokedError',
    
    # RBAC utilities
    'role_required',
    'admin_required',
    'election_officer_required',
    'polling_officer_required',
    'candidate_required',
    'voter_required',
    'has_role_permission',
    'check_resource_ownership',
    'get_allowed_roles',
    'can_manage_role',
    'RBACError',
    'PermissionDeniedError',
    'InvalidRoleError',
    'ROLES',
    'ROLE_HIERARCHY',
]
