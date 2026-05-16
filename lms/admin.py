from django.contrib import admin
from .models import Assignment, Course, Enrollment, Evaluation, Notification, Sponsorship, Submission

# Register your models here.


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "instructor", "price", "difficulty_level", "created_at"]
    list_display_links = ["id", "title"]
    list_filter = ["difficulty_level", "created_at"]
    search_fields = ["title", "description", "instructor__username"]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ["id", "student", "course", "status", "progress", "enrollment_date"]
    list_display_links = ["id", "student"]
    list_filter = ["status", "enrollment_date"]
    search_fields = ["student__username", "course__title"]


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "course", "total_marks", "deadline", "created_at"]
    list_display_links = ["id", "title"]
    list_filter = ["deadline", "created_at"]
    search_fields = ["title", "course__title"]


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ["id", "assignment", "student", "submitted_at"]
    list_display_links = ["id", "assignment"]
    list_filter = ["submitted_at"]
    search_fields = ["assignment__title", "student__username"]


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ["id", "submission", "marks_obtained", "status", "created_at"]
    list_display_links = ["id", "submission"]
    list_filter = ["status", "created_at"]
    search_fields = ["submission__assignment__title", "submission__student__username"]


@admin.register(Sponsorship)
class SponsorshipAdmin(admin.ModelAdmin):
    list_display = ["id", "sponsor", "student", "course", "organization_name", "status", "funded_at"]
    list_display_links = ["id", "sponsor"]
    list_filter = ["status", "funded_at"]
    search_fields = ["sponsor__username", "student__username", "course__title", "organization_name"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "sender", "receiver","message", "type", "is_read", "created_at"]
    list_display_links = ["id", "sender"]
    list_filter = ["type", "is_read", "created_at"]
    search_fields = ["sender__username", "receiver__username", "message"]

