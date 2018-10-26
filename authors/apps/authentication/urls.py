from django.conf.urls import url

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView, ResetPasswordAPIView
)

app_name = "authentication"
urlpatterns = [
    url(r'^user/?$', UserRetrieveUpdateAPIView.as_view(), name='update_user'),
    url(r'^users/?$', RegistrationAPIView.as_view(), name='register'),
    url(r'^users/login/?$', LoginAPIView.as_view(), name='login'),
    url(r'^users/resetpassword/?$', ResetPasswordAPIView.as_view(), name='reset_password'),
]
