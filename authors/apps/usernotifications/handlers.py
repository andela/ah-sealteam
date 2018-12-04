"""

user notification handlers

"""
# standard lib imports
import os
from datetime import datetime
import jwt
# third party imports
from django.db import models
from django.contrib.auth import get_user_model # user model
from django.db.models.signals import post_save, pre_delete
from notifications.signals import notify
from notifications.models import Notification
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

# local imports
from authors.apps.articles.models import Article, ArticleRating
from authors.apps.friends.models import Friend
from authors.apps.comments.models import Comment
from authors.apps.profiles.models import Profile
from authors.apps.bookmarks.models import BookmarkArticle
from authors.apps.favorites.models import Favorite
from . import verbs

def follow_handler(sender, instance, created, **kwargs):
    """
    notification handler for friends (following)
    """
    # get the user that has been followed
    follower = instance.user_from
    followed = instance.user_to
    recipients = followed
    resource_url = "{}/api/profiles/{}".format(settings.DOMAIN, follower.username)
    notify.send(follower,
                recipient=recipients,
                description="{} followed you on {}".format(follower.username, 
                                                instance.created_at.strftime('%d-%B-%Y %H:%M')),
                verb=verbs.USER_FOLLOWING,
                action_object=instance,
                target=followed,
                resource_url=resource_url)

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
    desc_string = "{} posted a comment to {} on {}"
    if article:
        # get users who have favourited the article.
        favorited_users = [fav.user for fav in Favorite.objects.filter(object_id=article.id)]
        recipients += favorited_users
        article_author = article.author
        if article_author.id != comment_author.id:
            recipients.append(article_author)
    resource_url = "{}".format(settings.DOMAIN)
    notify.send(comment_author,
                recipient=recipients,
                description=desc_string.format(comment_author.username,
                                               article or instance,
                                               instance.createdAt.strftime('%d-%B-%Y %H:%M')),
                verb=verbs.COMMENT_CREATED, 
                target=article or instance,
                action_object=instance,
                resource_url=resource_url)

def article_handler(sender, instance, created, **kwargs):
    """
    notification handler for articles
    """
    article_author = instance.author
    # add the user's followers to the recipients list
    followers_qs = Friend.objects.select_related('user_from', 'user_to').filter(
                                                user_to=article_author.id).all()
    recipients = [get_user_model().objects.get(id=u.user_from_id) for u in list(followers_qs)]
    resource_url = "{}/api/articles/{}".format(settings.DOMAIN, instance.slug)
    notify.send(article_author,
                recipient=recipients,
                description="{} posted an article on {}".format(article_author.username, 
                                                instance.createdAt.strftime('%d-%B-%Y %H:%M')),
                verb=verbs.ARTICLE_CREATION,
                action_object=instance,
                resource_url=resource_url
                )

def ratings_handler(sender, instance, created, **kwargs):
    """
    notification handler for article rating
    """
    article = instance.article
    article_author = article.author
    rating_author = instance.user
    desc_string = "{} rated your article ({}) and gave it {} on {}."
    resource_url = "{}/api/articles/{}".format(settings.DOMAIN,
                                               instance.article.slug)
    notify.send(rating_author,
                recipient=article_author,
                description=desc_string.format(rating_author.username,
                                               article.title,
                                               instance.rate,
                                               instance.rated_at.strftime('%d-%B-%Y %H:%M')),
                verb=verbs.ARTICLE_RATING,
                target=article,
                action_object=instance,
                resource_url=resource_url)

def bookmark_handler(sender, instance, created=None, **kwargs):
    """
    notification handler for when a bookmarked article is deleted
    """
    recipients = [mark.user for mark in BookmarkArticle.objects.filter(article=instance)]
    description = "The article you bookmarked - {} - has been deleted".format(instance.title)
    resource_url = settings.DOMAIN
    notify.send(instance.author,
            recipient=recipients,
            description=description,
            verb=verbs.BOOKMARK_DELETE,
            resource_url=resource_url)


def notification_handler(sender, instance, created, **kwargs):
    """
    email handler for notifications
    """
    recipient = instance.recipient
    if not recipient.email_notification_subscription:
        # user has unsubscribed from email notifications
        return
    description = instance.description
    token = recipient.token()
    opt_out_link = "{}/api/notifications/unsubscribe/{}".format(settings.DOMAIN, token)
    try: 
        resource_url = instance.data['resource_url']
    except TypeError:
        resource_url = settings.DOMAIN
    html_content = render_to_string('notification_email.html', 
                                    context={
                                            "unsub_link": opt_out_link,
                                            "username": recipient.username,
                                            "description":description,
                                            "resource_url":resource_url
                                        })
    send_mail("User Notification", '',
              "simplysealteam@gmail.com",
              [recipient.email],
              html_message=html_content)



post_save.connect(article_handler, sender=Article, weak=False)
post_save.connect(comment_handler, sender=Comment, weak=False)
post_save.connect(follow_handler, sender=Friend, weak=False)
post_save.connect(ratings_handler, sender=ArticleRating, weak=False)
pre_delete.connect(bookmark_handler, sender=Article, weak=False)
post_save.connect(notification_handler, sender=Notification)
