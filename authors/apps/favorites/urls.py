from django.urls import path
from .views import FavoriteArticle, FavoriteArticleRetrieve



app_name = 'favorites'

urlpatterns = [

    path('<slug:slug>/favorite/', FavoriteArticle.as_view(), name='article_favorite'),
    path('favorites/', FavoriteArticleRetrieve.as_view(), name='all_favorites')
]