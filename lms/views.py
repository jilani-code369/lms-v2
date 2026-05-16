from .models import *
from rest_framework.response import Response 
from rest_framework.decorators import api_view 
from django.db.models import Q
from .serializers import *
from rest_framework import status, viewsets 
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.db.models.deletion import ProtectedError
from users.serializers import *
from .permissions import *
from .pagination import PaginationOfTen, PaginationOfFifty
from rest_framework import filters 
from .filters import CourseFilter
from django_filters.rest_framework import DjangoFilterBackend


# Create your views here.

User = get_user_model()


# 1. User API: 
class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrOwner]
    pagination_class = PaginationOfTen
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email']
    ordering_fields = ['username', 'role'] 


    
    def get_queryset(self):
        user = self.request.user
        
        #here admin can see everyone
        if user.is_authenticated and user.role == 'AD':
            return User.objects.all()
        
        #other user can see only themselves
        return User.objects.filter(id=user.id)
    
    def get_serializer_class(self):
        # When creating a user (POST), use the RegisterSerializer
        # because it contains the create_user() logic to hash passwords.
        if self.action == 'create':
            return RegisterSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            if 'duplicate key' in str(e).lower() and 'phone_no' in str(e):
                return Response(
                    {"detail": "Phone number already exists. Please use a different phone number."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            if 'duplicate key' in str(e).lower() and 'phone_no' in str(e):
                return Response(
                    {"detail": "Phone number already exists. Please use a different phone number."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Extract clean message from Django validation errors
            error_str = str(e)
            if "Only admin can change user roles" in error_str:
                return Response(
                    {"detail": "Only admin can change user roles."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if "user with this phone no already exists" in error_str:
                return Response(
                    {"detail": "user with this phone no already exists."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
      
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
    permission_classes = [IsAdminOrInstructorCourseCreate]
    pagination_class = PaginationOfFifty
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CourseFilter
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'price', 'created_at']

    def perform_create(self, serializer):
        if self.request.user.role == 'IN':
            serializer.save(instructor=self.request.user)
            return

        serializer.save()
    
    
    # override destroy method to validate deleting 
    def destroy(self, request, pk=None):
        course = self.get_object()
        enrollment_count = Enrollment.objects.filter(course = course).count()
        sponsorship_count = Sponsorship.objects.filter(course = course).count()
        
        if enrollment_count >0:
            return Response({"detail":"Course cannot be deleted. Related to Enrollments."})
        elif sponsorship_count>0:
            return Response({"detail": "Course cannot be deleted. Related to Sponsorships"})

        course.delete()
        return Response({"detail": "Course has been deleted."}, status = status.HTTP_204_NO_CONTENT)
    
    
 # 3. Enrollment API: 
class EnrollmentView(viewsets.ModelViewSet):
     queryset = Enrollment.objects.all()
     serializer_class = EnrollmentSerializer
     pagination_class = PaginationOfTen
     permission_classes = [IsAdminOrStudentEnrollment]
     instructor_update_fields = {'status', 'progress'}
     filter_backends = [filters.SearchFilter, filters.OrderingFilter]
     search_fields = ['student__username', 'course__title']
     ordering_fields = ['enrollment_date', 'status']

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

     def perform_create(self, serializer):
        if self.request.user.role == 'ST':
            serializer.save(student=self.request.user)
            return

        serializer.save()

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
     pagination_class = PaginationOfTen
     permission_classes = [IsAdminOrInstructorAssignment]
     filter_backends = [filters.SearchFilter, filters.OrderingFilter]
     search_fields = ['title', 'description']
     ordering_fields = ['title', 'deadline', 'created_at']

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
     pagination_class = PaginationOfTen 
     permission_classes = [IsSubmissionPermission]
     student_update_fields = {'answer_text', 'file'}
     filter_backends = [filters.SearchFilter, filters.OrderingFilter]
     search_fields = ['assignment__title', 'student__username']
     ordering_fields = ['submitted_at']

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
        return super().update(request, *args, **kwargs)
     


# 6. Evaluation API:
class EvaluationView(viewsets.ModelViewSet):
     queryset = Evaluation.objects.all()
     serializer_class = EvaluationSerializer
     pagination_class = PaginationOfTen 
     permission_classes = [IsEvaluationPermission]
     filter_backends = [filters.SearchFilter, filters.OrderingFilter]
     search_fields = ['submission__assignment__title', 'student__username']
     ordering_fields = ['marks_obtained', 'created_at']

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

        if self.request.user.role != 'AD' and submission.assignment.course.instructor != self.request.user:
            raise PermissionDenied("Instructor can evaluate only submissions for their own course.")

        serializer.save()

     def perform_update(self, serializer):
        submission = serializer.validated_data.get('submission', serializer.instance.submission)

        if self.request.user.role != 'AD' and submission.assignment.course.instructor != self.request.user:
            raise PermissionDenied("Instructor can update only evaluations for their own course.")

        serializer.save()


# 7. Sponsorship API:
class SponsorshipView(viewsets.ModelViewSet):
     queryset = Sponsorship.objects.all()
     serializer_class = SponsorshipSerializer
     pagination_class = PaginationOfTen 
     permission_classes = [IsSponsorshipPermission]
     filter_backends = [filters.SearchFilter, filters.OrderingFilter]
     search_fields = ['sponsor__username', 'student__username', 'course__title']
     ordering_fields = ['status', 'created_at']

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
    serializer_class = NotificationSerializer
    pagination_class = PaginationOfTen 
    permission_classes = [IsAdminOrNotificationView]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['message', 'type']
    ordering_fields = ['created_at', 'is_read']
    
    def get_queryset(self):
        user = self.request.user
        
        if not user.is_authenticated:
            return Notification.objects.none()
        
        # All authenticated users can see all notifications
        return Notification.objects.all()
     

# 9. Admin Dashboard API
@api_view(['GET'])
def admin_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'AD':
        return Response({"detail": "Only administrators can access admin dashboard."}, status=403)
    
    # Calculate metrics
    total_users = User.objects.count()
    total_students = User.objects.filter(role='ST').count()
    total_instructors = User.objects.filter(role='IN').count()
    total_sponsors = User.objects.filter(role='SP').count()
    
    active_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.count()
    
    # Recent enrollments
    recent_enrollments = Enrollment.objects.order_by('-enrollment_date')[:5]
    recent_enrollment_data = []
    for enrollment in recent_enrollments:
        recent_enrollment_data.append({
            'student': enrollment.student.username,
            'course': enrollment.course.title,
            'enrolled_at': enrollment.enrollment_date
        })
    
    dashboard_data = {
        'user_metrics': {
            'total_users': total_users,
            'total_students': total_students,
            'total_instructors': total_instructors,
            'total_sponsors': total_sponsors
        },
        'course_metrics': {
            'active_courses': active_courses,
            'total_enrollments': total_enrollments
        },
        'recent_enrollments': recent_enrollment_data
    }
    
    return Response(dashboard_data)

# 10. Sponsor Dashboard API
@api_view(['GET'])
def sponsor_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'SP':
        return Response({"detail": "Only sponsors can access sponsor dashboard."}, status=403)
    
    sponsor = request.user
    
    # Sponsorship metrics
    total_sponsorships = Sponsorship.objects.filter(sponsor=sponsor).count()
    active_sponsorships = Sponsorship.objects.filter(sponsor=sponsor, status='AC').count()
    
    # Student progress - students sponsored by this sponsor
    sponsored_students = Sponsorship.objects.filter(sponsor=sponsor, status='AC')
    student_progress = []
    
    for sponsorship in sponsored_students:
        student = sponsorship.student
        # Get student's course enrollments and progress
        enrollments = Enrollment.objects.filter(student=student)
        total_courses = enrollments.count()
        
        # Calculate average marks from evaluations
        evaluations = Evaluation.objects.filter(submission__student=student)
        total_evaluations = evaluations.count()
        avg_marks = 0
        if total_evaluations > 0:
            total_marks = sum(eval.marks_obtained for eval in evaluations if eval.marks_obtained)
            possible_marks = sum(eval.submission.assignment.total_marks for eval in evaluations if eval.marks_obtained)
            if possible_marks > 0:
                avg_marks = round((total_marks / possible_marks) * 100, 2)
        
        student_progress.append({
            'student_name': student.username,
            'course': sponsorship.course.title,
            'total_courses': total_courses,
            'average_marks': avg_marks,
            'evaluations_count': total_evaluations
        })
    
    # Fund utilization
    total_sponsored_amount = 10000 * total_sponsorships  # Assuming 10000 per sponsorship
    active_sponsored_amount = 10000 * active_sponsorships
    
    dashboard_data = {
        'sponsorship_metrics': {
            'total_sponsorships': total_sponsorships,
            'active_sponsorships': active_sponsorships,
            'total_sponsored_amount': total_sponsored_amount,
            'active_sponsored_amount': active_sponsored_amount
        },
        'student_progress': student_progress,
        'fund_utilization': {
            'utilization_rate': round((active_sponsored_amount / total_sponsored_amount) * 100, 2) if total_sponsored_amount > 0 else 0
        }
    }
    
    return Response(dashboard_data)
     


   