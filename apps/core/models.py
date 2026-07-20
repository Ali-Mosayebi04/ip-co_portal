from django.db import models


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default="IPCO Portal")
    tagline = models.CharField(max_length=200, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_name
