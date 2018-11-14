from django.urls import path

from . import views

app_name = "stats"

urlpatterns = [
    path('', views.MyArticlesReadingStacsView.as_view(),
         name='my_article_stacs'),
    path('readings', views.ReadingStatisticsView.as_view(),
         name='my_reading_stacs'),
]
