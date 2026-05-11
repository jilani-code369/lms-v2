
from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model

User = get_user_model()

# 1. UserSerializer: 
class UserSerializer(serializers.ModelSerializer):
    class Meta: 
        model = User
        fields = ['username', 'password', 'role', 'phone_no', 'address', 'photo', 'gender']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def update(self, instance, validated_data):
        
        # pop the password out of the data so it's not saved as plain text
        password = validated_data.pop('password', None)
        
        # update the other fields (username, email, etc.)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # if a password was provided, hash it correctly
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance
    


# 2. Course serialzer: 
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

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

    def validate(self, attrs):
        student = attrs.get('student', getattr(self.instance, 'student', None))
        course = attrs.get('course', getattr(self.instance, 'course', None))

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

    def validate(self, attrs):
        course = attrs.get('course', getattr(self.instance, 'course', None))
        title = attrs.get('title', getattr(self.instance, 'title', None))

        assignment = Assignment.objects.filter(course=course, title__iexact=title)

        if self.instance:
            assignment = assignment.exclude(id=self.instance.id)

        if assignment.exists():
            raise serializers.ValidationError({"detail": "Assignment already exists for this course."})

        return attrs



# 5. Submission serialzer: 
class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ['student']

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

    def validate(self, attrs):
        submission = attrs.get('submission', getattr(self.instance, 'submission', None))

        evaluation = Evaluation.objects.filter(submission=submission)

        if self.instance:
            evaluation = evaluation.exclude(id=self.instance.id)

        if evaluation.exists():
            raise serializers.ValidationError({"detail": "Submission already has an evaluation."})

        return attrs
 


# 7. Sponsorship serialzer:
class SponsorshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sponsorship
        fields = '__all__'
        read_only_fields = ['sponsor']

    def validate(self, attrs):
        student = attrs.get('student', getattr(self.instance, 'student', None))

        sponsorship = Sponsorship.objects.filter(student=student)

        if self.instance:
            sponsorship = sponsorship.exclude(id=self.instance.id)

        if sponsorship.exists():
            raise serializers.ValidationError({"detail": "Student already has a sponsorship."})

        return attrs


# 8. Notification serialzer:
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

