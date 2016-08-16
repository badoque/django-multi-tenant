from rest_framework import permissions
from .exceptions import IncorrectTenantException

def belongs_to_tenant(email, tenant):
    """
    This function checks if the user belongs to the given Tenant.
    """
    user_exists = tenant.users.filter(email=email).exists()
    if not user_exists:
        raise IncorrectTenantException()

class IsRequiredTenant(permissions.BasePermission):
    """
    View mixin which verifies that there is a tenant in the request, that the
    user is authenticated and that the user belongs to the tenant.

    NOTE:
        This should be the left-most mixin of a view, except when
        combined with Django-Braces CsrfExemptMixin - which in that case
        should be the left-most mixin.
    """
    def has_permission(self, request, *args, **kwargs):
        if not request.tenant:
            return False

        if not request.user.is_authenticated():
            return False
                        
        try:
            belongs_to_tenant(request.user.email, request.tenant)
        except IncorrectTenantException:
            return False

        return True