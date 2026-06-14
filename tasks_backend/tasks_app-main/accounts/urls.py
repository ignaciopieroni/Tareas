# accounts/urls.py
from django.urls import path
from .views import RegisterView, LoginView, RefreshTokenView, MeView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/token/', LoginView.as_view(), name='auth-token'),
    path('auth/token/refresh/', RefreshTokenView.as_view(), name='auth-token-refresh'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
]