# Generated by Django 4.2.6 on 2023-11-07 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pool_manager', '0005_alter_poollease_options_rename_pool3_poollease_pool_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='poollease',
            old_name='pool_member2',
            new_name='pool_member',
        ),
        migrations.AlterField(
            model_name='poollease',
            name='app_type',
            field=models.CharField(max_length=30),
        ),
    ]
