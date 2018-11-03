from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView, ResetPasswordAPIView, ForgotPasswordAPIView
)

app_name = "authentication"

urlpatterns = [
    path('user', UserRetrieveUpdateAPIView.as_view(), name='update_user'),
    path('users', RegistrationAPIView.as_view(), name='register'),
    path('users/login', LoginAPIView.as_view(), name='login'),
    path('users/forgotpassword/', ForgotPasswordAPIView.as_view(), name='forgot_password'),
    path('users/resetpassword/', ResetPasswordAPIView.as_view(), name='reset_password'),
]
