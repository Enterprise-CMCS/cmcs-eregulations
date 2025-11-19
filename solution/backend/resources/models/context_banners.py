from django.db import models

from resources.models import AbstractCitation


class SectionContextBanner(models.Model):
    """Optional per-citation contextual banner content displayed in the right sidebar."""

    citation = models.ForeignKey(
        AbstractCitation,
        on_delete=models.CASCADE,
        related_name="context_banners",
        help_text="Select a Section or Subpart to attach this banner to.",
    )
    banner_html = models.TextField(
        verbose_name="Banner HTML",
        help_text="Optional HTML allowed. Keep it brief.",
        blank=True,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Context Banner"
        verbose_name_plural = "Context Banners"

    def __str__(self):
        return f"Banner for {self.citation.display_name}"
