"""
Imports
"""
from django.contrib import admin
from .models import Article

# Register your models here.

class ArticleAdmin(admin.ModelAdmin):
    """
    Class to define fields to display on admin page
    """
    list_display = ('title', 'description', 'body')

admin.register(Article, ArticleAdmin)
