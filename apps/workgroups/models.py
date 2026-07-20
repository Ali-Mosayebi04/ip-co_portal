from django.db import models
from django.urls import reverse


class WorkGroup(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Work Group"
        verbose_name_plural = "Work Groups"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("workgroups:detail", kwargs={"slug": self.slug})
