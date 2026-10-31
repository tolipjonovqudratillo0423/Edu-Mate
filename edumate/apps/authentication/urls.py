from django.urls import path

from apps.authentication.views import (
    LoginView,
    RegisterView,
    SendCodeToEmail,
    VerifyCode,
    RefreshView,
    LogoutView,
    ResendVerificationCode
    )

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    
    path('send-code/', SendCodeToEmail.as_view(), name='send-code'),
    path('resend-code/', ResendVerificationCode.as_view(), name='resend-code'),
    path('verify/', VerifyCode.as_view(), name='verify'),
    path('refresh-token/', RefreshView.as_view(), name='refresh-token'),
]   