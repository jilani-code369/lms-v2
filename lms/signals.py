from django.db.models.signals import post_save
from django.dispatch import receiver 
from .models import *
from django.core.mail import send_mail

@receiver(post_save, sender = Assignment)
def notify(sender, instance, created, **kwargs):
    if created:
        print(f"New Assignemt: '{instance.title}' has been created.")
        print(f"Deadline: '{instance.deadline}'")
    else:
        print("Assignment couldn't be created")
        
    send_mail(
        "order creation",
        f"New assigment created:  {instance.title}.",
        "rms@gmail.com",
        ['maxhn6@gmail.com'],
        fail_silently = False
    )