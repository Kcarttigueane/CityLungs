from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView, UserDetailView,
    PasswordChangeView, PasswordResetRequestView, PasswordResetConfirmView
)

app_name = 'user_auth'  # Add namespace to avoid URL name conflicts

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile endpoints
    path('user/profile/', UserDetailView.as_view(), name='user_profile'),
    path('user/password/change/', PasswordChangeView.as_view(), name='password_change'),
    path('user/password/reset/request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('user/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]