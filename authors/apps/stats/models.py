import datetime

from django.db import models

from authors.apps.articles.models import Article
from authors.apps.authentication.models import User


class ReadingStatistics(models.Model):
    """This is the model representation to track how the user is reading"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, blank=True,
                                null=True, related_name="article_read")
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="article_reader")
    read_last_at = models.DateTimeField(auto_now=True)
    no_read = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ('-read_last_at',)
        unique_together = ("article", "user")

    def time_since_last_read(self):
        """This will return number of seconds
        since last read"""
        from django.utils.timezone import utc
        return datetime.datetime.utcnow().replace(
            tzinfo=utc) - self.read_last_at
