from django.apps import AppConfig
from django.conf import settings

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        from django.contrib.sites.models import Site

        site_domain = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else "stayease.site"
        if site_domain in {"127.0.0.1", "localhost"} and len(settings.ALLOWED_HOSTS) > 2:
            site_domain = settings.ALLOWED_HOSTS[2]

        Site.objects.update_or_create(
            pk=settings.SITE_ID,
            defaults={
                "domain": site_domain,
                "name": "Stayease",
            },
        )