from django.db import models

from conduit.apps.core.models import TimestampedModel


class Profile(TimestampedModel):
    user = models.OneToOneField(
        'authentication.User', on_delete=models.CASCADE
    )

    # Description field for user, initially empty
    bio = models.TextField(blank=True)

    # Profile pic/avatar for user
    image = models.URLField(blank=True)

    def __str__(self):
        return self.user.username
