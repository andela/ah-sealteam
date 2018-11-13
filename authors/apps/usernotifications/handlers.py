"""

user notification models

"""

from django.db import models
from django.contrib.auth import get_user_model # user model
from django.db.models.signals import post_save
from actstream import action
from notifications.signals import notify
# local models
from authors.apps.articles.models import Article
from authors.apps.friends.models import Friend
from authors.apps.comments.models import Comment
from authors.apps.profiles.models import Profile

def comment_handler(sender, instance, created, **kwargs):
    """
    notification handler for comments
    """
    recipients = []
    if instance.parent:
        # comment is part of a thread
        parent_comment_author = instance.parent.author
        recipients.append(parent_comment_author)
    comment_author = instance.author
    article = instance.article
    article_author = article.author
    recipients.append(article_author)
    notify.send(sender=comment_author, recepient=recipients, verb="posted a comment", target=article, action_object=instance)

def article_handler(sender, instance, created, **kwargs):
    user = instance.author
    recipients = [user]
    # add the user's followers to the recipients list
    recipients.append(Friend.objects.select_related(
            'user_from', 'user_to').filter(user_to=user.id).all())
    notify.send(user, recipients=recipients, verb="posted an article", action_object=instance)

post_save.connect(article_handler, sender=Article)
post_save.connect(comment_handler, sender=Comment)
