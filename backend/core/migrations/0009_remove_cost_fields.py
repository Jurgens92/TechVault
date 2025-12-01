# Generated migration to remove all cost-related fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_voip_voipassignment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='software',
            name='cost',
        ),
        migrations.RemoveField(
            model_name='backup',
            name='cost',
        ),
        migrations.RemoveField(
            model_name='backup',
            name='cost_period',
        ),
        migrations.RemoveField(
            model_name='voip',
            name='cost',
        ),
    ]
