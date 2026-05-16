from django.urls import path 
from .views import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register('course',CourseView, basename='course')
router.register('enrollment',EnrollmentView, basename='enrollment')
router.register('assignment',AssignmentView, basename='assignment')
router.register('submission',SubmissionView, basename='submission')
router.register('evaluation',EvaluationView, basename='evaluation')
router.register('sponsorship',SponsorshipView, basename='sponsorship')
router.register('notification',NotificationView, basename='notification')

router.register('profile',UserView, basename='profile')

urlpatterns = [
    path('admin-dashboard/', admin_dashboard, name='admin-dashboard'),
    path('sponsor-dashboard/', sponsor_dashboard, name='sponsor-dashboard'),
] + router.urls
