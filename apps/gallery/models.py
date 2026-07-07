from django.db import models

from apps.core.models import TimeStampedModel


class InstagramPost(TimeStampedModel):
    """A photo shown in the 'On Instagram' section of the homepage.

    Uploaded and hosted on our own server, rather than linking directly to
    Instagram's CDN, since those links expire and can break silently.
    """

    image = models.ImageField(upload_to="gallery/%Y/%m/")
    link = models.URLField(
        blank=True,
        help_text="Optional: the actual Instagram post URL, opened when the photo is clicked.",
    )
    caption = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        return self.caption or f"Gallery photo #{self.pk}"
