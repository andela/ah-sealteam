"""
Imports
"""
import random
import readtime
import string
import markdown
import cloudinary
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from django.db.models.signals import pre_delete, pre_save
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from cloudinary.models import CloudinaryField
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from ..authentication.models import User
from django.db.models.signals import pre_save


class TaggedItem(models.Model):
    """
    Tags arbitrary model instances using generic relation
    """
    tag_name = models.SlugField()
    content_type = models.ForeignKey(ContentType, blank=True, null=True,
                                     on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    tagged_object = GenericForeignKey('content_type', 'object_id')

    objects = models.Manager()

    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'tags'

    def __str__(self):
        return self.tag_name


def random_string_generator(size=4, chars=string.ascii_lowercase + string.digits):
    """Generate random string for slug"""
    return ''.join(random.choice(chars) for _ in range(size))


class LikeDislikeManager(models.Manager):
    """
    Manager class for like and dislike
    """
    use_for_related_fields = True
 
    def likes(self):
        """
        get all the likes for an object
        """
        return self.get_queryset().filter(vote__gt=0)
 
    def dislikes(self):
        """
        get all the dislikes of an object
        """
        return self.get_queryset().filter(vote__lt=0)
 
    def sum_rating(self):
        """
        obtain the aggregate likes/dislikes
        """
        return self.get_queryset().aggregate(Sum('vote')).get('vote__sum') or 0
    
    def articles(self):
        """
        obtain the votes of a particular user
        """
        return self.get_queryset().filter(content_type__model='article').order_by('-articles__published_at')

class LikeDislike(models.Model):
    """
    Users should be able to like and/or dislike an article or comment.
    This class creates the fields for like/dislike
    """
    LIKE = 1
    DISLIKE = -1
 
    VOTES = (
        (DISLIKE, 'Dislike'),
        (LIKE, 'Like')
    )
 
    vote = models.SmallIntegerField(verbose_name=_("vote"), choices=VOTES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("user"))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    
    objects = LikeDislikeManager()

class Article(models.Model):
    """
    When a user registers in the application, this class create the models for
    what the user will do once they have an account and that is post an article
    The class creates the models for the functionality.
    """
    author = models.ForeignKey(User, related_name='article', blank=True,
                               null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, unique=True)
    body = models.TextField(unique=True)
    tags = GenericRelation(TaggedItem)
    createdAt = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=270, blank=True, null=True)
    updatedAt = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(default=timezone.now)
    read_time = models.CharField(default='0 min read', blank=True, 
            null=True, max_length=20)
    favorited = models.BooleanField(default=False)
    content_html = models.TextField(editable=False)
    votes = GenericRelation(LikeDislike, related_query_name='articles')
    objects = models.Manager()


    class Meta:
        ordering = ('-published_at', '-id')

    def __str__(self):
        return self.title

    def unique_slug_generator(self, new_slug=None):
        """Generate a new slug and check if another exist"""
        if new_slug is not None:
            slug = new_slug
        else:
            slug = slugify(self.title)
        qs_exists = Article.objects.filter(slug=slug).exists()
        if qs_exists:
            new_slug = "{slug}_{randstr}".format(
                slug=slug,
                randstr=random_string_generator()
            )
            return self.unique_slug_generator(new_slug)
        return slug

    def get_markdown(self):
        body = self.body
        content_html = markdown.markdown(body)
        return mark_safe(content_html)

    def save(self, *args, **kwargs):
        """
        Overidding the save to do our own things
        :type kwargs: save object
        """
        self.content_html = self.get_markdown()
        if not self.id:
            # check id to ensure update does not update deadlinks
            self.slug = self.unique_slug_generator()
        super().save(*args, **kwargs)

def article_save(sender, instance, *args, **kwargs):
    """
    Saves the article instance of the read time to the database
    """
    if instance.body:
        markdown_text = instance.get_markdown()
        read_time_str = readtime.of_html(markdown_text)
        instance.read_time = read_time_str

pre_save.connect(article_save, sender=Article)

class Photo(models.Model):
    """
    Users may wish to add images to their article.
    This class creates the power for users to do that
    Can add multiple images

    """
    article = models.ForeignKey(Article, related_name='article_image', on_delete=models.CASCADE)
    image = CloudinaryField('image')
    caption = models.CharField(max_length=100, blank=True)

    def __str__(self):
        if self.caption != "":
            return self.caption
        return "No caption provided"


@receiver(pre_delete, sender=Photo)
def delete_image(sender, instance, **kwargs):
    cloudinary.uploader.destroy(instance.image.public_id)


class ArticleRating(models.Model):
    FIVE_REVIEWS = (
        (5, 5),
        (4, 4),
        (3, 3),
        (2, 2),
        (1, 1),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    rate = models.PositiveIntegerField(choices=FIVE_REVIEWS, default='5')
    rated_at = models.DateTimeField(default=timezone.now)
    comment = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        unique_together = ("user", "article")
        ordering = ('-rated_at', '-id')

        
class Comment(models.Model):
    parent = models.ForeignKey('self', null=True, blank=False, on_delete=models.CASCADE, related_name='thread')
    article = models.ForeignKey(Article, related_name='comment', null=True, blank=True, on_delete=models.CASCADE) 
    author = models.ForeignKey(User, related_name='comment', blank=True, null=True, on_delete=models.CASCADE)
    body = models.CharField(max_length=200)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.body

    


