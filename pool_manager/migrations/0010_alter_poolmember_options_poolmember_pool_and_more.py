# Generated by Django 4.2.6 on 2023-11-08 07:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pool_manager', '0009_alter_poolmember_options_remove_poolmember_lease_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='poolmember',
            options={'ordering': ('pool', 'range_number')},
        ),
        migrations.AddField(
            model_name='poolmember',
            name='pool',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='members', to='pool_manager.pool'),
        ),
        migrations.AlterUniqueTogether(
            name='poolmember',
            unique_together={('pool', 'range_number')},
        ),
    ]
