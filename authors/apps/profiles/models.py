from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save


class Profile(models.Model):
    bio = models.CharField(max_length=255, default='')
    image = models.ImageField(blank=True, upload_to='avatars/')
    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = Profile.objects.create(user=kwargs['instance'])


post_save.connect(create_profile, sender=get_user_model())
