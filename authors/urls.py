"""authors URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from rest_framework_swagger.views import get_swagger_view
from django.conf import settings
from django.conf.urls.static import static
import notifications.urls
schema_view = get_swagger_view(title='Authors Haven SealTeam API')

urlpatterns = [
    path('', schema_view),
    path('admin/', admin.site.urls),
    path('api/', include('authors.apps.authentication.urls')),
    path('api/notifications/', include('authors.apps.usernotifications.urls', namespace="notifications")),
    path('api/profiles/', include('authors.apps.profiles.urls')),
    path('api/articles/', include('authors.apps.articles.urls')),
    path('api/articles/', include('authors.apps.favorites.urls')),
    path('api/articles/<slug:slug>/', include('authors.apps.comments.urls')),
    path('api/articles/', include('authors.apps.bookmarks.urls')),
    path('api/articles/', include('authors.apps.highlight.urls')),
    path('accounts/', include('allauth.urls')),
    path('api/profiles/<username>/', include('authors.apps.friends.urls')),
    path('api/statistics/', include('authors.apps.stats.urls')),

    path('api/', include('authors.apps.reports.urls'))
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
