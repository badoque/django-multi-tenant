from django.conf import settings
from django.apps import apps


class SubdomainMiddleware(object):
    """
    Adds a ``subdomain`` attribute to the ``request`` parameter.
    """

    def process_request(self, request):
        domain = request.META.get('HTTP_HOST')
        pieces = domain.split('.')
        try:
            request.subdomain = pieces[-2]
        except IndexError:
            request.subdomain = None

class TenantMiddleware(object):

    def process_request(self, request):
        """
        Adds a ``tenant`` attribute to the ``request`` parameter.
        
        It gets the tenant slug from the request header.

        It will try to find a TENANT_MODEL on the settings, if it can't find
        the specified model, it will user the multi_tenant.Tenant model.
        """
        tenant_slug = request.META.get('HTTP_APPLICATION')
        model_path = getattr(settings, 'TENANT_MODEL', 'multi_tenant.Tenant')
        tenant_model = apps.get_model(*tuple(model_path.split('.')))
        try:
            tenant = tenant_model.objects.get(slug=tenant_slug)
        except tenant_model.DoesNotExist:
            tenant = None

        request.tenant = tenant