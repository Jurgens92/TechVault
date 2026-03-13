from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_audit_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditlog',
            name='changes',
            field=models.JSONField(
                blank=True,
                help_text='Structured change data: field-level diffs for updates, field values for creates/deletes',
                null=True,
            ),
        ),
    ]
