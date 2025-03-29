from django.urls import path
from .views import (
    UserRegisterView,
    UserProfileView,
    UserListView,
    UserDetailView,
    UserUpdateView,
    LoginUserView,
    LogoutView,
    PasswordResetRequestView,
    PasswordResetConfirmView
)

urlpatterns = [
    # Authentication endpoints
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # User profile endpoints
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('', UserListView.as_view(), name='user_list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('<int:pk>/update/', UserUpdateView.as_view(), name='user_update'),
    
    # Password reset endpoints
    path('password/reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]