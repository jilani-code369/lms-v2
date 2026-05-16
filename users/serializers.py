from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


# to handle the registeration of the user, serialization is needed. 
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='ST')

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'phone_no', 'address', 'photo', 'gender']

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        
        # Remove role field completely for non-admin users
        if request and request.user.is_authenticated and request.user.role != 'AD':
            fields.pop('role', None)
        
        return fields

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        if value and User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate_phone_no(self, value):
        # Only check for duplicate if phone number is provided (not empty)
        if value and value.strip() and User.objects.filter(phone_no=value).exists():
            raise serializers.ValidationError("Phone number already exists.")
        return value

    def validate_role(self, value):
        # Only allow admins to set role during updates
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.role != 'AD':
            # For non-admin users, don't allow role changes
            if hasattr(self.instance, 'role') and self.instance.role != value:
                raise serializers.ValidationError("Only administrators can change user roles.")
        return value

    def create(self, validated_data):
        # this will create user and handle password handling automatically 
        user = User.objects.create_user(**validated_data)
        return user
