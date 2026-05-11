from django.shortcuts import render
from .models import *
from rest_framework.response import Response 
from rest_framework.decorators import api_view 
from .serializers import *
from rest_framework import status, viewsets 
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.db.models.deletion import ProtectedError
from users.serializers import *
from .permissions import *

# Create your views here.

User = get_user_model()


# 1. User API: 
class UserView(viewsets.ModelViewSet):
     serializer_class = UserSerializer
     permission_classes = [IsAdminOrOwner]
     
     
     def get_queryset(self):
        user = self.request.user
        
        #here admin can see everyone
        if user.is_authenticated and user.role == 'admin':
            return User.objects.all()
        
        #other user can see only themselves
        return User.objects.filter(id=user.id)
    
     def get_serializer_class(self):
        # When creating a user (POST), use the RegisterSerializer
        # because it contains the create_user() logic to hash passwords.
        if self.action == 'create':
            return RegisterSerializer
        return UserSerializer
      
      
     def destroy(self, request, pk=None):
        user = self.get_object()
        sponsor_count = Sponsorship.objects.filter(sponsor = user).count()
        student_count = Sponsorship.objects.filter(student = user).count()
        
        if sponsor_count >0:
            return Response({"detail":"Sponsor cannot be deleted. Related to sponshorship."})
        elif student_count>0:
            return Response({"detail": "Student cannot be deleted. Related to sponsorship"})

        try:
            user.delete()
        except ProtectedError:
            return Response(
                {"detail": "User cannot be deleted because it is related to protected data."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"detail": "User has been deleted."}, status=status.HTTP_204_NO_CONTENT)
    
    
 
# 2. Course API:
class CourseView(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    
    # override destroy method to validate deleting 
    def destroy(self, request, pk=None):
        course = self.get_object()
        enrollment_count = Enrollment.objects.filter(course = course).count()
        sponsorship_count = Sponsorship.objects.filter(course = course).count()
        
        if enrollment_count >0:
            return Response({"detail":"Course cannot be deleted. Related to Enrollments."})
        elif sponsorship_count>0:
            return Response({"detail": "Course cannot be deleted. Related to Sponsorships"})
        try:
            course.delete()
        except ProtectedError:
            return Response(
                {"detail": "Course cannot be deleted because it is related to protected data."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"datail": "Course has been deleted."}, status = status.HTTP_204_NO_CONTENT)
    
    
 # 3. Enrollment API: 
class EnrollmentView(viewsets.ModelViewSet):
     queryset = Enrollment.objects.all()
     serializer_class = EnrollmentSerializer
     permission_classes = [IsAdminOrStudentEnrollment]
     instructor_update_fields = {'status', 'progress'}

     def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.role == 'AD':
            return Enrollment.objects.all()

        if user.is_authenticated and user.role == 'ST':
            return Enrollment.objects.filter(student=user)

        if user.is_authenticated and user.role == 'IN':
            return Enrollment.objects.filter(course__instructor=user)

        if user.is_authenticated and user.role == 'SP':
            return Enrollment.objects.all()

        return Enrollment.objects.none()

     def update(self, request, *args, **kwargs):
        if request.user.role == 'IN':
            invalid_fields = set(request.data.keys()) - self.instructor_update_fields
            if invalid_fields:
                return Response(
                    {"detail": "Instructor can only update status and progress."},
                    status=status.HTTP_403_FORBIDDEN
                )

        return super().update(request, *args, **kwargs)
 
 
 # 4. Assignment API: 
class AssignmentView(viewsets.ModelViewSet):
     queryset = Assignment.objects.all()
     serializer_class = AssignmentSerializer
     permission_classes = [IsAdminOrInstructorAssignment]

     def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.role == 'AD':
            return Assignment.objects.all()

        if user.is_authenticated and user.role == 'IN':
            return Assignment.objects.filter(course__instructor=user)

        if user.is_authenticated and user.role == 'ST':
            return Assignment.objects.filter(course__enrollment__student=user).distinct()

        return Assignment.objects.none()

     def perform_create(self, serializer):
        course = serializer.validated_data.get('course')

        if self.request.user.role == 'IN' and course.instructor != self.request.user:
            raise PermissionDenied("Instructor can create assignments only for their own course.")

        serializer.save()

     def perform_update(self, serializer):
        course = serializer.validated_data.get('course', serializer.instance.course)

        if self.request.user.role == 'IN' and course.instructor != self.request.user:
            raise PermissionDenied("Instructor can update assignments only for their own course.")

        serializer.save()
     


# 5. Submission API: 
class SubmissionView(viewsets.ModelViewSet):
     queryset = Submission.objects.all()
     serializer_class = SubmissionSerializer
     permission_classes = [IsSubmissionPermission]
     student_update_fields = {'answer_text', 'file'}

     def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.role == 'AD':
            return Submission.objects.all()

        if user.is_authenticated and user.role == 'IN':
            return Submission.objects.filter(assignment__course__instructor=user)

        if user.is_authenticated and user.role == 'ST':
            return Submission.objects.filter(student=user)

        return Submission.objects.none()

     def perform_create(self, serializer):
        serializer.save(student=self.request.user)

     def update(self, request, *args, **kwargs):
        user = request.user

        if user.role == 'ST':
            invalid_fields = set(request.data.keys()) - self.student_update_fields
            if invalid_fields:
                return Response(
                    {"detail": "Student can only update answer_text and file."},
                    status=status.HTTP_403_FORBIDDEN
                )

        return super().update(request, *args, **kwargs)
     


# 6. Evaluation API:
class EvaluationView(viewsets.ModelViewSet):
     queryset = Evaluation.objects.all()
     serializer_class = EvaluationSerializer
     permission_classes = [IsEvaluationPermission]

     def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.role == 'AD':
            return Evaluation.objects.all()

        if user.is_authenticated and user.role == 'IN':
            return Evaluation.objects.filter(submission__assignment__course__instructor=user)

        if user.is_authenticated and user.role == 'ST':
            return Evaluation.objects.filter(submission__student=user)

        return Evaluation.objects.none()

     def perform_create(self, serializer):
        submission = serializer.validated_data.get('submission')

        if submission.assignment.course.instructor != self.request.user:
            raise PermissionDenied("Instructor can evaluate only submissions for their own course.")

        serializer.save()

     def perform_update(self, serializer):
        submission = serializer.validated_data.get('submission', serializer.instance.submission)

        if submission.assignment.course.instructor != self.request.user:
            raise PermissionDenied("Instructor can update only evaluations for their own course.")

        serializer.save()


# 7. Sponsorship API:
class SponsorshipView(viewsets.ModelViewSet):
     queryset = Sponsorship.objects.all()
     serializer_class = SponsorshipSerializer
     permission_classes = [IsSponsorshipPermission]

     def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.role == 'AD':
            return Sponsorship.objects.all()

        if user.is_authenticated and user.role == 'SP':
            return Sponsorship.objects.filter(sponsor=user)

        if user.is_authenticated and user.role == 'IN':
            return Sponsorship.objects.filter(course__instructor=user)

        if user.is_authenticated and user.role == 'ST':
            return Sponsorship.objects.filter(student=user)

        return Sponsorship.objects.none()

     def perform_create(self, serializer):
        serializer.save(sponsor=self.request.user)

     def perform_update(self, serializer):
        serializer.save(sponsor=self.request.user)
     


# 8. Notification API:
class NotificationView(viewsets.ModelViewSet):
     queryset = Notification.objects.all()
     serializer_class = NotificationSerializer
     
