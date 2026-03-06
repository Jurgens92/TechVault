import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    """
    Custom createsuperuser command that works with email-based User model.
    Supports DJANGO_SUPERUSER_PASSWORD env var for non-interactive use.
    """

    help = 'Create a superuser with email-based authentication'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            dest='email',
            help='Specifies the email for the superuser.',
        )
        parser.add_argument(
            '--first_name',
            dest='first_name',
            help='Specifies the first name for the superuser.',
        )
        parser.add_argument(
            '--last_name',
            dest='last_name',
            help='Specifies the last name for the superuser.',
        )
        parser.add_argument(
            '--noinput', '--no-input',
            action='store_false',
            dest='interactive',
            help='Tells Django to NOT prompt the user for input of any kind.',
        )
        parser.add_argument(
            '--database',
            default='default',
            help='Specifies the database to use. Default is "default".',
        )

    def handle(self, *args, **options):
        email = options.get('email')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        first_name = options.get('first_name', 'Admin')
        last_name = options.get('last_name', 'User')

        if not email:
            if not options.get('interactive', True):
                self.stderr.write('Error: --email is required for non-interactive mode.')
                return
            email = input('Email: ')
            if not email or '@' not in email:
                self.stderr.write('Error: A valid email address is required.')
                return

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(f'Error: User with email "{email}" already exists.')
            )
            return

        if not password:
            if not options.get('interactive', True):
                self.stderr.write(
                    'Error: You must set DJANGO_SUPERUSER_PASSWORD env var '
                    'for non-interactive superuser creation.'
                )
                return
            import getpass
            password = getpass.getpass('Password: ')
            if not password or len(password) < 8:
                self.stderr.write('Error: Password must be at least 8 characters.')
                return

        if not first_name:
            first_name = input('First name [Admin]: ') or 'Admin'

        if not last_name:
            last_name = input('Last name [User]: ') or 'User'

        User.objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Superuser created successfully. Email: {email}'
            )
        )
