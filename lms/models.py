from django.db import models
from django.conf import settings 
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

# 2. Course
class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ("BG", "Beginner"),
        ("IN", "Intermediate"),
        ("AD", "Advanced")
    ]
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.PROTECT, limit_choices_to={'role': 'IN'})  # dk - import the 'django.conf import settings', use 'settings.AUTH_USER_MODEL'
    course_image = models.ImageField(upload_to='course_img/', blank = True, null = True)
    title = models.CharField(max_length = 50)
    description = models.TextField()
    price = models.DecimalField(max_digits = 10, decimal_places = 2)  # dk - use "DecimalField with 'max_digits' and 'decimal_places' attributes' "
    difficulty_level = models.CharField(max_length=2, choices = DIFFICULTY_CHOICES, default = 'BG')
    created_at = models.DateTimeField(auto_now_add = True) # record the date and time on creation 
    updated_at = models.DateTimeField(auto_now = True)  # update the date/time on every update 
    
    
    def __str__(self):
        return (f"{self.title}")


# 3. Enrollment
class Enrollment(models.Model):
    STATUS_CHOICES = [
        ("AC", "Active"),
        ("CM", "Completed"),
        ("DR", "Dropped")
    ]
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    course = models.ForeignKey(Course, on_delete = models.PROTECT)  # don't allow course to delete if it has enrollments 
    enrollment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length = 2, choices = STATUS_CHOICES, default = "AC")
    progress = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])   #dk - use validators 

    updated_at = models.DateTimeField(auto_now = True)


# 4. Assignment
class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete = models.CASCADE)
    title = models.CharField(max_length = 50)
    description = models.TextField()
    total_marks = models.PositiveIntegerField()
    deadline = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return(f"{self.title} ({self.course})")


# 5. Submission

class Submission(models.Model):
    ## writtable by student: 
    assignment = models.ForeignKey(Assignment, on_delete = models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE) 
    answer_text = models.TextField()
    file = models.FileField(upload_to='submission_files/', blank = True, null = True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return (f"{self.assignment.id} . {self.assignment.title} - ({self.assignment.course.title}) ({self.student.username}) marks: {self.assignment.total_marks}")


# 6. Evaluation
class Evaluation(models.Model):
    STATUS_CHOICES = [
        ("PN", "Pending"),
        ("AP", "Approved"),
        ("RJ", "Rejected")
    ]

    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='evaluation')
    marks_obtained = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="PN")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# 6. Sponsorship
class Sponsorship(models.Model):
    STATUS_CHOICES = [
        ("PN", "Pending"),
        ("AC", "Active"), 
        ("FN", "Finished")
    ]
    
    sponsor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.PROTECT, related_name='sponsored_courses')
    organization_name = models.CharField(max_length = 50)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.PROTECT, related_name='sponsorship_details')
    course = models.ForeignKey(Course, on_delete = models.PROTECT)  #d amount = models.PositiveIntegerField()
    status = models.CharField(max_length = 2, choices = STATUS_CHOICES, default = "PN")

    funded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)


# 7. Notification
class Notification(models.Model):
    TYPE_CHOICES = [
        ("IN","Informative"),
        ("AL", "Alert"),
        ("WR", "Warning")
    ]
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null = True, related_name = 'sent_notifications')
    receiver  =  models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null = True, related_name = 'received_notifications')
    message  = models.TextField()
    type = models.CharField(max_length = 2, choices = TYPE_CHOICES, default = "IN")
    is_read = models.BooleanField(default = False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
