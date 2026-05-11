from rest_framework import permissions


# Custom permission to only allow admins to edit/create. Everyone else can just view.
class IsAdminOrReadOnly(permissions.BasePermission):
    
    def has_permission(self, request, view):
        
        if request.method in permissions.SAFE_METHODS:
            return True

      
        return request.user.is_authenticated and request.user.role == 'AD'


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
            return request.user.role == 'AD'

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'AD':
            return request.method in permissions.SAFE_METHODS or request.method == 'DELETE'

        if request.user.role == 'IN':
            return request.method in permissions.SAFE_METHODS and obj.assignment.course.instructor == request.user

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
            return request.user.role == 'IN'

        if request.method == 'DELETE':
            return request.user.role == 'AD'

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'AD':
            return request.method in permissions.SAFE_METHODS or request.method == 'DELETE'

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


# Custom permission to allow only admin or owner to edit. Other can just view it.
class IsAdminOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
     
        if view.action == 'create':
            return request.user.is_authenticated and request.user.role == 'admin'
        

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):

        return request.user.role == 'admin' or obj == request.user
    
    
    
# Permission to only allow Author or Admin to create post. 

class IsAuthorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        #allow everyone to view post
        if request.method in permissions.SAFE_METHODS:
            return True
        
        #checking if admin or authro to create post
        if request.method == 'POST':
            return (
                request.user.is_authenticated and 
                (request.user.role == 'admin' or request.user.role == 'author')
            )
            
        #check the ownership of the post to edit or delete post
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        #always allow viewing 
        if request.method in permissions.SAFE_METHODS:
            return True

        # checking the origional author or admin 
        return obj.author == request.user or request.user.role == 'admin'
    
    

