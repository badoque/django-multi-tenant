from braces.views._access import AccessMixin
from .exceptions import IncorrectTenantException
from rest_framework.views import APIView
from .permissions import IsRequiredTenant
from django.core.exceptions import ImproperlyConfigured

def belongs_to_tenant(username, tenant):
    """
    This function checks if the user belongs to the given Tenant.
    """
    user_exists = tenant.users.filter(username=username).exists()
    if not user_exists:
        raise IncorrectTenantException()

class TenantRequiredMixin(AccessMixin):
    """
    View mixin which verifies that there is a tenant in the request, that the
    user is authenticated and that the user belongs to the tenant.

    NOTE:
        This should be the left-most mixin of a view, except when
        combined with Django-Braces CsrfExemptMixin - which in that case
        should be the left-most mixin.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.tenant:
            return self.handle_no_permission(request)

        if not request.user.is_authenticated():
            return self.handle_no_permission(request)

        try:
            belongs_to_tenant(request.user.username, request.tenant)
        except IncorrectTenantException:
            return self.handle_no_permission(request)

        return super(TenantRequiredMixin, self).dispatch(
            request, *args, **kwargs)

class APITenantRequiredMixin():

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        self.permission_classes = [IsRequiredTenant] + list(self.permission_classes)
        return [permission() for permission in self.permission_classes]

class APITenantQuerysetMixin(object):

    def get_queryset(self):
        from django.db.models.query import QuerySet

        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        ret = queryset.filter(tenant=self.request.tentant)
        return ret