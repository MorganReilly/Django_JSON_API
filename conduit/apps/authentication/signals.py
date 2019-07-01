from django.db.models.signals import post_save
from django.dispatch import receiver

from conduit.apps.profiles.models import Profile

from .models import User


@receiver(post_save, sender=User)
def create_related_profile(sender, instance, created, *args, **kwargs):
    # Checking for 'created', only do this first time 'User' is created.
    # If save that caused signal to be run was update action, we know user
    # has a profile
    if instance and created:
        instance.profile = Profile.objects.create(user=instance)
