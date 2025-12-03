# Generated migration for 2FA fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='twofa_secret',
            field=models.CharField(blank=True, help_text='TOTP secret key for 2FA', max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='twofa_enabled',
            field=models.BooleanField(default=False, help_text='Whether 2FA is enabled for this user'),
        ),
        migrations.AddField(
            model_name='user',
            name='twofa_backup_codes',
            field=models.JSONField(blank=True, default=list, help_text='Backup codes for 2FA recovery (hashed)'),
        ),
    ]
