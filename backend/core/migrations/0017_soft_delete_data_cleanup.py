"""
Data clean-up ahead of the integrity constraints added in 0018.

1. Organizations that were soft-deleted before delete cascaded to their children
   left those children visible. Soft-delete them with the organization's timestamp
   (so restoring the organization brings them back).
2. License quantities become non-negative; clamp any existing negative values.
"""
from django.db import migrations

OWNED_MODELS = [
    'Location', 'Contact', 'Documentation', 'PasswordEntry', 'Configuration',
    'NetworkDevice', 'EndpointUser', 'Server', 'Peripheral', 'Software', 'VoIP', 'Backup',
]


def forwards(apps, schema_editor):
    Organization = apps.get_model('core', 'Organization')
    for org in Organization.objects.filter(deleted_at__isnull=False).iterator():
        for model_name in OWNED_MODELS:
            model = apps.get_model('core', model_name)
            model.objects.filter(organization_id=org.pk, deleted_at__isnull=True).update(
                deleted_at=org.deleted_at, deleted_by_id=org.deleted_by_id
            )

    for model_name in ('Software', 'VoIP'):
        apps.get_model('core', model_name).objects.filter(quantity__lt=0).update(quantity=0)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auditlog_changes'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
