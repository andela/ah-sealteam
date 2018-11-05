"""
Imports
"""
from django.contrib import admin

from .models import Article, TaggedItem


class ArticleAdmin(admin.ModelAdmin):
    """
    Class to define fields to display on admin page
    """
    list_display = ('title', 'description', 'body')


admin.site.register(Article, ArticleAdmin)
admin.site.register(TaggedItem)
