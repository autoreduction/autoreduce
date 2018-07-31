"""
Custom manage.py command to add a super user to the database
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Adds a super user to the database
    """
    help = 'Creates a super user in the database'

    def handle(self, *args, **options):
        """
        (THIS SHOULD ONLY BE USED FOR DEVELOPMENT)
        handler to add super user to database
        """
        from django.contrib.auth.models import User
        User.objects.filter(username='super').delete()
        User.objects.create_superuser('super', '', 'super')
