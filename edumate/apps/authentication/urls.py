from django.urls import path

from apps.authentication.views import (
    LoginView,
    RegisterView,
    SendCodeToEmail,
    VerifyCode
    )

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    # path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    
    path('send-code/', SendCodeToEmail.as_view(), name='send-code'),
    path('verify/', VerifyCode.as_view(), name='verify'),
]   