from django.apps import AppConfig


class RmsConfig(AppConfig):
    name = 'lms'
    
    def ready(self):
        import lms.signals
