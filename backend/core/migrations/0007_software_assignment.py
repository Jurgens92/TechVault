# Generated manually for software assignment feature

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_backup'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='software',
            name='assigned_to',
        ),
        migrations.CreateModel(
            name='SoftwareAssignment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='software_assignments', to='core.contact')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_deleted', to=settings.AUTH_USER_MODEL)),
                ('software', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='software_assignments', to='core.software')),
            ],
            options={
                'db_table': 'software_assignments',
                'unique_together': {('software', 'contact')},
            },
        ),
    ]
