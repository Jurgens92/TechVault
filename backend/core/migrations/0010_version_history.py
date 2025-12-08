# Generated migration for version history models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_remove_cost_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentationVersion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('version_number', models.IntegerField()),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('category', models.CharField(max_length=50)),
                ('tags', models.CharField(blank=True, max_length=500)),
                ('is_published', models.BooleanField(default=False)),
                ('change_note', models.TextField(blank=True, help_text='Optional description of what changed in this version')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='documentation_versions_created', to=settings.AUTH_USER_MODEL)),
                ('documentation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='core.documentation')),
            ],
            options={
                'db_table': 'documentation_versions',
                'ordering': ['-version_number'],
                'unique_together': {('documentation', 'version_number')},
            },
        ),
        migrations.CreateModel(
            name='PasswordEntryVersion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('version_number', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
                ('username', models.CharField(blank=True, max_length=255)),
                ('password', models.TextField()),
                ('url', models.URLField(blank=True)),
                ('notes', models.TextField(blank=True)),
                ('category', models.CharField(max_length=50)),
                ('is_encrypted', models.BooleanField(default=False)),
                ('change_note', models.TextField(blank=True, help_text='Optional description of what changed in this version')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='password_versions_created', to=settings.AUTH_USER_MODEL)),
                ('password_entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='core.passwordentry')),
            ],
            options={
                'db_table': 'password_entry_versions',
                'ordering': ['-version_number'],
                'unique_together': {('password_entry', 'version_number')},
            },
        ),
        migrations.CreateModel(
            name='ConfigurationVersion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('version_number', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
                ('config_type', models.CharField(max_length=50)),
                ('content', models.TextField()),
                ('description', models.TextField(blank=True)),
                ('version', models.CharField(blank=True, max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('change_note', models.TextField(blank=True, help_text='Optional description of what changed in this version')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='configuration_versions_created', to=settings.AUTH_USER_MODEL)),
                ('configuration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='core.configuration')),
            ],
            options={
                'db_table': 'configuration_versions',
                'ordering': ['-version_number'],
                'unique_together': {('configuration', 'version_number')},
            },
        ),
    ]
