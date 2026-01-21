# Generated migration for server storage details and host linking

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_internetconnection'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='storage_drives',
            field=models.CharField(blank=True, help_text='e.g., 4x 1TB SSD, 8x 2TB HDD', max_length=255),
        ),
        migrations.AddField(
            model_name='server',
            name='raid_configuration',
            field=models.CharField(blank=True, help_text='e.g., RAID 5, RAID 10, ZFS Mirror', max_length=100),
        ),
        migrations.AddField(
            model_name='server',
            name='host_server',
            field=models.ForeignKey(
                blank=True,
                help_text='Physical host server for virtual machines',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='virtual_machines',
                to='core.server',
            ),
        ),
    ]
