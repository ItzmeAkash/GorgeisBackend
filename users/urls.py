
from django.urls import path
from .views import UserRegisterView,ViewProfile, LoginUserView, LogoutView
urlpatterns = [
    path('register/',UserRegisterView.as_view(),name='signup'),
    path('login/',LoginUserView.as_view(),name='login'),
    path('logout/',LogoutView.as_view(), name='logout'),
     path('profile',ViewProfile.as_view()),

]