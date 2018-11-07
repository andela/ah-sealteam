from django.db import models
from django.contrib.auth import get_user_model


class Friend(models.Model):
    """This is an itermediary model to build relationship between users"""

    # the user that creates the relationship
    user_from = models.ForeignKey(get_user_model(),
                                related_name='rel_from_set',
                                on_delete=models.CASCADE)
    # the user being followed
    user_to = models.ForeignKey(get_user_model(),
                                related_name='rel_to_set',
                                on_delete=models.CASCADE)
    # timestamps associated with
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        unique_together = ('user_from', 'user_to')

    def __str__(self):
        return '{} follows {}'.format(self.user_from.username,
                                    self.user_to.username)


# Add following field to User dynamically
get_user_model().add_to_class('following',
                              models.ManyToManyField('self',
                                                    through=Friend,
                                                    related_name='followers',
                                                    symmetrical=False))
