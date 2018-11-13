"""
app config module
"""

from django.apps import AppConfig

class BookmarksConfig(AppConfig):
    name = 'authors.apps.bookmarks'

    def ready(self):
        from authors.apps.usernotifications import handlers