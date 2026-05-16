
from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# 1. UserSerializer: 
class UserSerializer(serializers.ModelSerializer):
    class Meta: 
        model = User
        fields = ['id', 'username', 'password', 'role', 'phone_no', 'address', 'photo', 'gender']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        # 1. Get the new role from data (if provided)
        new_role = validated_data.get('role')
        request = self.context.get('request')

        # 2. Check if the role is present AND if it actually changed
        if new_role is not None and new_role != instance.role:
            if request and request.user.is_authenticated and request.user.role != 'AD':
                raise serializers.ValidationError({"role": "Only admin can change user roles."})
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance
    


# 2. Course serialzer: 
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')

        if request and request.user.is_authenticated and request.user.role == 'IN':
            fields.pop('instructor', None)

        return fields

    def validate_title(self, value):
        course = Course.objects.filter(title__iexact=value)

        if self.instance:
            course = course.exclude(id=self.instance.id)

        if course.exists():
            raise serializers.ValidationError("Course already exists.")

        return value
    


# 3. Enrollment serialzer: 
class EnrollmentSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Enrollment
        fields = '__all__'

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')

        if request and request.user.is_authenticated:
            if request.user.role == 'ST':
                fields.pop('student', None)
                if request.method in ['POST', 'PUT', 'PATCH']:
                    fields.pop('status', None)
                    fields.pop('progress', None)
            elif request.user.role == 'IN' and request.method in ['PUT', 'PATCH']:
                fields = {
                    name: field for name, field in fields.items()
                    if name in ['status', 'progress']
                }
            elif 'student' in fields:
                fields['student'].queryset = User.objects.filter(role='ST')

        return fields

    def validate(self, attrs):
        student = attrs.get('student', getattr(self.instance, 'student', None))
        request = self.context.get('request')
        course = attrs.get('course', getattr(self.instance, 'course', None))

        if student is None and request and request.user.role == 'ST':
            student = request.user

        enrollment = Enrollment.objects.filter(student=student, course=course)

        if self.instance:
            enrollment = enrollment.exclude(id=self.instance.id)

        if enrollment.exists():
            raise serializers.ValidationError({"detail": "Student is already enrolled in this course."})

        return attrs
    



# 4. Assignment serialzer: 
class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')

        if request and request.user.is_authenticated and request.user.role == 'IN':
            fields['course'].queryset = Course.objects.filter(instructor_id=request.user.id)

        return fields

    def validate_deadline(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError("Deadline cannot be in the past.")

        return value



# 5. Submission serialzer: 
class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ['student']

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')

        if request and request.user.is_authenticated and request.user.role == 'ST':
            # Filter assignments to show only those from courses the student is enrolled in
            fields['assignment'].queryset = Assignment.objects.filter(
                course__enrollment__student=request.user
            ).distinct()

        return fields

    def validate(self, attrs):
        assignment = attrs.get('assignment', getattr(self.instance, 'assignment', None))
        request = self.context.get('request')
        student = attrs.get('student', getattr(self.instance, 'student', None))

        if student is None and request:
            student = request.user

        submission = Submission.objects.filter(assignment=assignment, student=student)

        if self.instance:
            submission = submission.exclude(id=self.instance.id)

        if submission.exists():
            raise serializers.ValidationError({"detail": "Student has already submitted this assignment."})

        return attrs


# 6. Evaluation serialzer:
class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = '__all__'

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')

        if request and request.user.is_authenticated and request.user.role == 'IN':
            # Filter submissions to show only those from instructor's own courses
            fields['submission'].queryset = Submission.objects.filter(
                assignment__course__instructor=request.user
            )

        return fields

    def validate(self, attrs):
        submission = attrs.get('submission', getattr(self.instance, 'submission', None))
        marks_obtained = attrs.get('marks_obtained', getattr(self.instance, 'marks_obtained', None))

        # Only check for duplicate evaluation during creation, not update
        if not self.instance:
            evaluation = Evaluation.objects.filter(submission=submission)
            if evaluation.exists():
                raise serializers.ValidationError({"submission": "evaluation with this submission already exists."})

        # Validate marks don't exceed total marks
        if marks_obtained is not None and submission:
            if marks_obtained > submission.assignment.total_marks:
                raise serializers.ValidationError({
                    "marks_obtained": f"Marks obtained ({marks_obtained}) cannot exceed total marks ({submission.assignment.total_marks})."
                })

        return attrs
 


# 7. Sponsorship serialzer:
class SponsorshipSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='ST'))
    
    class Meta:
        model = Sponsorship
        fields = '__all__'
        read_only_fields = ['sponsor']

    def validate(self, attrs):
        student = attrs.get('student', getattr(self.instance, 'student', None))
        course = attrs.get('course', getattr(self.instance, 'course', None))

        # Check for duplicate sponsorship only if same student AND same course
        sponsorship = Sponsorship.objects.filter(student=student, course=course)

        if self.instance:
            sponsorship = sponsorship.exclude(id=self.instance.id)

        if sponsorship.exists():
            raise serializers.ValidationError({"student": f"Student {student.username} already has sponsorship in this course ({course.title})."})

        # Validate student is enrolled in the selected course
        if student and course:
            enrollment = Enrollment.objects.filter(student=student, course=course)
            if not enrollment.exists():
                raise serializers.ValidationError({
                    "detail": f"Student {student.username} is not enrolled in course {course.title}."
                })

        return attrs


# 8. Notification serialzer:
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'



