from django.urls import path
from rest_framework_swagger.views import get_swagger_view

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView, ResetPasswordAPIView, ForgotPasswordAPIView
)

schema_view = get_swagger_view(title='Authors Haven SealTeam API')
app_name = "authentication"

urlpatterns = [
    path('', schema_view),
    path('user', UserRetrieveUpdateAPIView.as_view(), name='update_user'),
    path('users', RegistrationAPIView.as_view(), name='register'),
    path('login', LoginAPIView.as_view(), name='login'),
    path('forgotpassword', ForgotPasswordAPIView.as_view(), name='forgot_password'),
    path('resetpassword', ResetPasswordAPIView.as_view(), name='reset_password'),
]
