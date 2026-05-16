from django.db.models.signals import post_save
from django.dispatch import receiver 
from .models import *
from django.core.mail import send_mail

@receiver(post_save, sender=Assignment)
def notify(sender, instance, created, **kwargs):
    if created:
        print(f"New Assignment: '{instance.title}' has been created.")
        print(f"Deadline: '{instance.deadline}'")
        
        # Create notifications for students enrolled in the course
        for enrollment in Enrollment.objects.filter(course=instance.course):
            Notification.objects.create(
                sender=instance.course.instructor,
                receiver=enrollment.student,
                message=f"New Assignment: {instance.title}. Deadline: {instance.deadline}",
                type="IN"
            )
    else:
        print("Assignment couldn't be created")
        
    send_mail(
        "Assignment creation",
        f"New assigment created:  {instance.title}. Deadline: {instance.deadline}",
        "rms@gmail.com",
        ['maxhn6@gmail.com'],
        fail_silently = False
    )

@receiver(post_save, sender=Evaluation)
def evaluation_notify(sender, instance, created, **kwargs):
    send_mail(
        "Assignment Evaluated",
        f"Your assignment has been evaluated. Marks obtained: {instance.marks_obtained}/{instance.submission.assignment.total_marks} for {instance.submission.assignment.title}.",
        "rms@gmail.com",
        ['maxhn6@gmail.com'],
        fail_silently = False
    )
