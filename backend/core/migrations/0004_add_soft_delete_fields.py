# Generated manually for soft delete implementation

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_endpointuser_networkdevice_peripheral_server'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add soft delete fields to Organization
        migrations.AddField(
            model_name='organization',
            name='deleted_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='deleted_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='organization_deleted',
                to=settings.AUTH_USER_MODEL
            ),
        ),

        # Add soft delete fields to Location
        migrations.AddField(
            model_name='location',
            name='deleted_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='deleted_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='location_deleted',
                to=settings.AUTH_USER_MODEL
            ),
        ),

        # Add soft delete fields to Contact
        migrations.AddField(
            model_name='contact',
            name='deleted_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='deleted_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='contact_deleted',
                to=settings.AUTH_USER_MODEL
            ),
        ),

        # Add soft delete fields to Documentation
        migrations.AddField(
            model_name='documentation',
            name='deleted_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='documentation',
            name='deleted_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='documentation_deleted',
                to=settings.AUTH_USER_MODEL
            ),
        ),

        # Add soft delete fields to PasswordEntry
        migrations.AddField(
            model_name='passwordentry',
            name='deleted_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='passwordentry',
            name='deleted_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='passwordentry_deleted',
                to=settings.AUTH_USER_MODEL
            ),
        ),

        # Add soft delete fields to Configuration
        migrations.AddField(
            model_name='configuration',
            name='deleted_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='configuration',
            name='deleted_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='configuration_deleted',
                to=settings.AUTH_USER_MODEL
            ),
        ),

        # Add soft delete fields to NetworkDevice
        migrations.AddField(
            model_name='networkdevice',
            name='deleted_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='networkdevice',
            name='deleted_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='networkdevice_deleted',
                to=settings.AUTH_USER_MODEL
            ),
        ),

        # Add soft delete fields to EndpointUser
        migrations.AddField(
            model_name='endpointuser',
            name='deleted_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='endpointuser',
            name='deleted_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='endpointuser_deleted',
                to=settings.AUTH_USER_MODEL
            ),
        ),

        # Add soft delete fields to Server
        migrations.AddField(
            model_name='server',
            name='deleted_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='server',
            name='deleted_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='server_deleted',
                to=settings.AUTH_USER_MODEL
            ),
        ),

        # Add soft delete fields to Peripheral
        migrations.AddField(
            model_name='peripheral',
            name='deleted_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='peripheral',
            name='deleted_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='peripheral_deleted',
                to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
