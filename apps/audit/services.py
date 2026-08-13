from apps.audit.models import AuditLog


class AuditService:
    """Service for creating audit logs"""
    
    @staticmethod
    def log_action(user, action, entity_name=None, entity_id=None, details=None, request=None):
        """Create an audit log entry"""
        ip_address = None
        if request:
            ip_address = request.META.get('REMOTE_ADDR', None)
        
        AuditLog.objects.create(
            user=user,
            action=action,
            entity_name=entity_name,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address,
        )