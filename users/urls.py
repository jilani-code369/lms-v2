from django.urls import path 
from .views import LoginAPIView, RegisterAPIView, LogoutAPIView

urlpatterns = [
    path('login/', LoginAPIView.as_view()),
    path('register/', RegisterAPIView.as_view()),
    path('logout/', LogoutAPIView.as_view()),
]  