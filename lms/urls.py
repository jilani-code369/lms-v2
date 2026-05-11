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
router.register('manage_user',UserView, basename='manage_user')

urlpatterns = [
  
]+router.urls
