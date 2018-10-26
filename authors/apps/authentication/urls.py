from django.conf.urls import url
from rest_framework_swagger.views import get_swagger_view

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView
)

schema_view = get_swagger_view(title='Authors Haven SealTeam API')
app_name = "authentication"

urlpatterns = [
    url(r'^$', schema_view),
    url(r'^user/?$', UserRetrieveUpdateAPIView.as_view(), name='update_user'),
    url(r'^users/?$', RegistrationAPIView.as_view(), name='register'),
    url(r'^users/login/?$', LoginAPIView.as_view(), name='login'),
]
