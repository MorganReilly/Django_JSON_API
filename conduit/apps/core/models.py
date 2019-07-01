from django.db import models


class TimestampedModel(models.Model):
    # Timestamp representing when object was created
    created_at = models.DateTimeField(auto_now_add=True)

    # Timestamp representing when object was last updated
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

        # By default, any model that inherits from 'TimestampedModel' should
        # be ordered in reverse-chronological order. Can override this on a per-model
        # basis as needed
        ordering = ['-created_at', '-updated_at']
