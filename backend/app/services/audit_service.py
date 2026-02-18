"""
Security audit logging service for tracking authentication and authorization events.

This module provides comprehensive audit logging for security-critical operations
including authentication attempts, authorization failures, data access, and
permission violations. All logs are structured for easy parsing and analysis.

Audit logs are written to the application logger with WARNING level for failures
and INFO level for successful operations.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


# Configure logger for audit events
logger = logging.getLogger("security_audit")


class AuditEventType(str, Enum):
    """Types of security audit events."""

    # Authentication events
    AUTH_LOGIN_SUCCESS = "auth_login_success"
    AUTH_LOGIN_FAILURE = "auth_login_failure"
    AUTH_LOGOUT = "auth_logout"
    AUTH_TOKEN_EXPIRED = "auth_token_expired"
    AUTH_TOKEN_INVALID = "auth_token_invalid"
    AUTH_SIGNUP_SUCCESS = "auth_signup_success"
    AUTH_SIGNUP_FAILURE = "auth_signup_failure"

    # Authorization events
    AUTHZ_ACCESS_GRANTED = "authz_access_granted"
    AUTHZ_ACCESS_DENIED = "authz_access_denied"
    AUTHZ_PERMISSION_DENIED = "authz_permission_denied"
    AUTHZ_OWNERSHIP_VIOLATION = "authz_ownership_violation"

    # Data access events
    DATA_ACCESS_TASK = "data_access_task"
    DATA_ACCESS_TEAM = "data_access_team"
    DATA_ACCESS_DASHBOARD = "data_access_dashboard"
    DATA_ACCESS_CONVERSATION = "data_access_conversation"

    # Data modification events
    DATA_CREATE_TASK = "data_create_task"
    DATA_UPDATE_TASK = "data_update_task"
    DATA_DELETE_TASK = "data_delete_task"
    DATA_SHARE_TASK = "data_share_task"

    # Team events
    TEAM_CREATE = "team_create"
    TEAM_DELETE = "team_delete"
    TEAM_MEMBER_ADD = "team_member_add"
    TEAM_MEMBER_REMOVE = "team_member_remove"
    TEAM_ROLE_CHANGE = "team_role_change"

    # Security violations
    SECURITY_SQL_INJECTION_ATTEMPT = "security_sql_injection_attempt"
    SECURITY_XSS_ATTEMPT = "security_xss_attempt"
    SECURITY_RATE_LIMIT_EXCEEDED = "security_rate_limit_exceeded"
    SECURITY_SUSPICIOUS_ACTIVITY = "security_suspicious_activity"


class AuditResult(str, Enum):
    """Result of an audited operation."""
    SUCCESS = "success"
    FAILURE = "failure"
    DENIED = "denied"
    ERROR = "error"


class AuditService:
    """
    Service for logging security audit events.

    This service provides structured logging for all security-critical operations
    in the application. All audit logs include timestamp, user, action, resource,
    and result information.

    Example:
        ```python
        audit = AuditService()

        # Log successful authentication
        audit.log_authentication(
            user_id="user123",
            email="user@example.com",
            success=True
        )

        # Log authorization failure
        audit.log_authorization_failure(
            user_id="user123",
            action="delete_task",
            resource_type="task",
            resource_id="task456",
            reason="not_owner"
        )
        ```
    """

    def __init__(self):
        """Initialize audit service."""
        self.logger = logger

    # ========================================================================
    # Authentication Audit Logging
    # ========================================================================

    def log_authentication(
        self,
        user_id: Optional[str],
        email: str,
        success: bool,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> None:
        """
        Log authentication attempt (login).

        Args:
            user_id: User ID if authentication succeeded
            email: Email address used for login
            success: Whether authentication succeeded
            reason: Reason for failure (if applicable)
            ip_address: Client IP address (if available)
        """
        event_type = (
            AuditEventType.AUTH_LOGIN_SUCCESS if success
            else AuditEventType.AUTH_LOGIN_FAILURE
        )
        result = AuditResult.SUCCESS if success else AuditResult.FAILURE

        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type.value,
            "result": result.value,
            "user_id": user_id or "unknown",
            "email": email,
            "ip_address": ip_address or "unknown",
            "reason": reason or "N/A"
        }

        if success:
            self.logger.info(self._format_log(log_data))
        else:
            self.logger.warning(self._format_log(log_data))

    def log_signup(
        self,
        user_id: Optional[str],
        email: str,
        success: bool,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> None:
        """
        Log user signup attempt.

        Args:
            user_id: User ID if signup succeeded
            email: Email address used for signup
            success: Whether signup succeeded
            reason: Reason for failure (if applicable)
            ip_address: Client IP address (if available)
        """
        event_type = (
            AuditEventType.AUTH_SIGNUP_SUCCESS if success
            else AuditEventType.AUTH_SIGNUP_FAILURE
        )
        result = AuditResult.SUCCESS if success else AuditResult.FAILURE

        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type.value,
            "result": result.value,
            "user_id": user_id or "unknown",
            "email": email,
            "ip_address": ip_address or "unknown",
            "reason": reason or "N/A"
        }

        if success:
            self.logger.info(self._format_log(log_data))
        else:
            self.logger.warning(self._format_log(log_data))

    def log_token_validation(
        self,
        user_id: Optional[str],
        success: bool,
        reason: Optional[str] = None
    ) -> None:
        """
        Log JWT token validation attempt.

        Args:
            user_id: User ID from token (if valid)
            success: Whether token validation succeeded
            reason: Reason for failure (expired, invalid, etc.)
        """
        if success:
            event_type = AuditEventType.AUTHZ_ACCESS_GRANTED
            result = AuditResult.SUCCESS
        elif reason == "expired":
            event_type = AuditEventType.AUTH_TOKEN_EXPIRED
            result = AuditResult.FAILURE
        else:
            event_type = AuditEventType.AUTH_TOKEN_INVALID
            result = AuditResult.FAILURE

        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type.value,
            "result": result.value,
            "user_id": user_id or "unknown",
            "reason": reason or "N/A"
        }

        if success:
            self.logger.info(self._format_log(log_data))
        else:
            self.logger.warning(self._format_log(log_data))

    # ========================================================================
    # Authorization Audit Logging
    # ========================================================================

    def log_authorization_success(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        access_type: Optional[str] = None
    ) -> None:
        """
        Log successful authorization check.

        Args:
            user_id: User who performed the action
            action: Action performed (e.g., "access_task", "edit_task")
            resource_type: Type of resource (e.g., "task", "team")
            resource_id: Resource identifier
            access_type: Type of access granted (owner, team_member, etc.)
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": AuditEventType.AUTHZ_ACCESS_GRANTED.value,
            "result": AuditResult.SUCCESS.value,
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id or "N/A",
            "access_type": access_type or "N/A"
        }

        self.logger.info(self._format_log(log_data))

    def log_authorization_failure(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        reason: str = "permission_denied"
    ) -> None:
        """
        Log failed authorization check.

        Args:
            user_id: User who attempted the action
            action: Action attempted (e.g., "access_task", "edit_task")
            resource_type: Type of resource (e.g., "task", "team")
            resource_id: Resource identifier
            reason: Reason for denial
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": AuditEventType.AUTHZ_ACCESS_DENIED.value,
            "result": AuditResult.DENIED.value,
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id or "N/A",
            "reason": reason
        }

        self.logger.warning(self._format_log(log_data))

    def log_permission_violation(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        required_permission: Optional[str] = None
    ) -> None:
        """
        Log permission violation attempt.

        Args:
            user_id: User who attempted the action
            action: Action attempted
            resource_type: Type of resource
            resource_id: Resource identifier
            required_permission: Permission that was required
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": AuditEventType.AUTHZ_PERMISSION_DENIED.value,
            "result": AuditResult.DENIED.value,
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id or "N/A",
            "required_permission": required_permission or "N/A"
        }

        self.logger.warning(self._format_log(log_data))

    # ========================================================================
    # Data Access Audit Logging
    # ========================================================================

    def log_data_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str = "read"
    ) -> None:
        """
        Log data access event.

        Args:
            user_id: User who accessed the data
            resource_type: Type of resource (task, team, dashboard, etc.)
            resource_id: Resource identifier
            action: Action performed (read, list, query)
        """
        event_type_map = {
            "task": AuditEventType.DATA_ACCESS_TASK,
            "team": AuditEventType.DATA_ACCESS_TEAM,
            "dashboard": AuditEventType.DATA_ACCESS_DASHBOARD,
            "conversation": AuditEventType.DATA_ACCESS_CONVERSATION
        }

        event_type = event_type_map.get(
            resource_type,
            AuditEventType.DATA_ACCESS_TASK
        )

        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type.value,
            "result": AuditResult.SUCCESS.value,
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id
        }

        self.logger.info(self._format_log(log_data))

    def log_data_modification(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        changes: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log data modification event.

        Args:
            user_id: User who modified the data
            action: Action performed (create, update, delete)
            resource_type: Type of resource
            resource_id: Resource identifier
            changes: Dictionary of changes made (optional)
        """
        event_type_map = {
            "create": AuditEventType.DATA_CREATE_TASK,
            "update": AuditEventType.DATA_UPDATE_TASK,
            "delete": AuditEventType.DATA_DELETE_TASK
        }

        event_type = event_type_map.get(action, AuditEventType.DATA_UPDATE_TASK)

        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type.value,
            "result": AuditResult.SUCCESS.value,
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "changes": str(changes) if changes else "N/A"
        }

        self.logger.info(self._format_log(log_data))

    # ========================================================================
    # Security Violation Logging
    # ========================================================================

    def log_security_violation(
        self,
        user_id: Optional[str],
        violation_type: str,
        details: str,
        ip_address: Optional[str] = None
    ) -> None:
        """
        Log security violation attempt.

        Args:
            user_id: User who attempted the violation (if known)
            violation_type: Type of violation (sql_injection, xss, etc.)
            details: Details about the violation
            ip_address: Client IP address (if available)
        """
        violation_map = {
            "sql_injection": AuditEventType.SECURITY_SQL_INJECTION_ATTEMPT,
            "xss": AuditEventType.SECURITY_XSS_ATTEMPT,
            "rate_limit": AuditEventType.SECURITY_RATE_LIMIT_EXCEEDED,
            "suspicious": AuditEventType.SECURITY_SUSPICIOUS_ACTIVITY
        }

        event_type = violation_map.get(
            violation_type,
            AuditEventType.SECURITY_SUSPICIOUS_ACTIVITY
        )

        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type.value,
            "result": AuditResult.DENIED.value,
            "user_id": user_id or "unknown",
            "violation_type": violation_type,
            "details": details,
            "ip_address": ip_address or "unknown"
        }

        self.logger.error(self._format_log(log_data))

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _format_log(self, log_data: Dict[str, Any]) -> str:
        """
        Format log data as structured string.

        Args:
            log_data: Dictionary of log data

        Returns:
            Formatted log string
        """
        parts = [f"{key}={value}" for key, value in log_data.items()]
        return " ".join(parts)


# Global audit service instance
audit_service = AuditService()


# Convenience functions for common audit operations
def log_auth_success(user_id: str, email: str, ip_address: Optional[str] = None):
    """Log successful authentication."""
    audit_service.log_authentication(user_id, email, True, ip_address=ip_address)


def log_auth_failure(email: str, reason: str, ip_address: Optional[str] = None):
    """Log failed authentication."""
    audit_service.log_authentication(None, email, False, reason, ip_address)


def log_authz_success(user_id: str, action: str, resource_type: str, resource_id: Optional[str] = None):
    """Log successful authorization."""
    audit_service.log_authorization_success(user_id, action, resource_type, resource_id)


def log_authz_failure(user_id: str, action: str, resource_type: str, resource_id: Optional[str] = None, reason: str = "permission_denied"):
    """Log failed authorization."""
    audit_service.log_authorization_failure(user_id, action, resource_type, resource_id, reason)


def log_data_access(user_id: str, resource_type: str, resource_id: str):
    """Log data access."""
    audit_service.log_data_access(user_id, resource_type, resource_id)


def log_security_violation(user_id: Optional[str], violation_type: str, details: str):
    """Log security violation."""
    audit_service.log_security_violation(user_id, violation_type, details)
