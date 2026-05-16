from rest_framework import permissions


# Admin can manage courses. Instructors can manage only their own courses.
# Everyone can view.
class IsAdminOrInstructorCourseCreate(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        if request.user.role == 'AD':
            return True

        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return request.user.role == 'IN'

        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.role == 'AD':
            return True

        return request.user.role == 'IN' and obj.instructor == request.user


# Admin can do everything. Students, instructors, and sponsors can only view notifications
class IsAdminOrNotificationView(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Admin can do everything
        if request.user.role == 'AD':
            return True

        # Only allow safe methods (GET, HEAD, OPTIONS) for other users
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user.role in ['ST', 'IN', 'SP']

        # Block POST, PUT, DELETE for non-admin users
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'AD':
            return True

        # Only allow safe methods for other users
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        return False




# Admin can do everything. Students can create and view. Instructors can update
# status/progress for their own course enrollments. Sponsors can view only.
class IsAdminOrStudentEnrollment(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role == 'AD':
            return True

        if request.method in permissions.SAFE_METHODS:
            return request.user.role in ['ST', 'IN', 'SP']

        if request.method == 'POST':
            return request.user.role == 'ST'

        if request.method in ['PUT', 'PATCH']:
            return request.user.role == 'IN'

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'AD':
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method in ['PUT', 'PATCH']:
            return request.user.role == 'IN' and obj.course.instructor == request.user

        return False


# Admin can do everything. Instructors can manage assignments for their own
# courses. Students can view related course assignments. Sponsors cannot access.
class IsAdminOrInstructorAssignment(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role == 'AD':
            return True

        if request.method in permissions.SAFE_METHODS:
            return request.user.role in ['IN', 'ST']

        return request.user.role == 'IN'

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'AD':
            return True

        if request.method in permissions.SAFE_METHODS:
            return request.user.role in ['IN', 'ST']

        return request.user.role == 'IN' and obj.course.instructor == request.user

class IsSubmissionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return request.user.role in ['AD', 'IN', 'ST']

        if request.method == 'POST':
            return request.user.role == 'ST'

        if request.method in ['PUT', 'PATCH']:
            return request.user.role == 'ST'

        if request.method == 'DELETE':
            return request.user.role in ['AD', 'IN']

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'AD':
            return request.method in permissions.SAFE_METHODS or request.method == 'DELETE'

        if request.user.role == 'IN':
            return request.method in [*permissions.SAFE_METHODS, 'DELETE'] and obj.assignment.course.instructor == request.user

        if request.user.role == 'ST':
            return obj.student == request.user and request.method != 'DELETE'

        return False


class IsEvaluationPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return request.user.role in ['AD', 'IN', 'ST']

        if request.method in ['POST', 'PUT', 'PATCH']:
            return request.user.role in ['AD', 'IN']

        if request.method == 'DELETE':
            return request.user.role in ['AD', 'IN']

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'AD':
            return True

        if request.user.role == 'IN':
            return obj.submission.assignment.course.instructor == request.user

        if request.user.role == 'ST':
            return request.method in permissions.SAFE_METHODS and obj.submission.student == request.user

        return False


class IsSponsorshipPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return request.user.role in ['AD', 'SP', 'IN', 'ST']

        if request.method == 'POST':
            return request.user.role == 'SP'

        if request.method in ['PUT', 'PATCH']:
            return request.user.role == 'SP'

        if request.method == 'DELETE':
            return request.user.role in ['AD', 'SP']

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'AD':
            return request.method in permissions.SAFE_METHODS or request.method == 'DELETE'

        if request.user.role == 'SP':
            return obj.sponsor == request.user

        if request.user.role == 'IN':
            return request.method in permissions.SAFE_METHODS and obj.course.instructor == request.user

        if request.user.role == 'ST':
            return request.method in permissions.SAFE_METHODS and obj.student == request.user

        return False


# Custom permission to allow admin full access and users to manage their own accounts
class IsAdminOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        # Admin can do everything - view all, edit all, delete all
        if request.user.is_authenticated and request.user.role == 'AD':
            return True
        
        # Other users can view, edit, delete their own
        if request.user.is_authenticated and view.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            return True
        
        # Other users cannot create new users
        return False

    def has_object_permission(self, request, view, obj):
        # Admin can do everything
        if request.user.role == 'AD':
            return True
        
        # Users can only manage their own accounts
        return obj == request.user

