# Generated by Django 4.2.6 on 2023-11-07 19:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0098_webhook_custom_field_data_webhook_tags'),
        ('pool_manager', '0007_remove_poollease_pool_member'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PoolMembers',
            new_name='PoolMember',
        ),
    ]
