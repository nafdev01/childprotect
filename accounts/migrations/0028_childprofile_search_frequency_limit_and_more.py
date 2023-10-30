# Generated by Django 5.0a1 on 2023-10-30 06:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0027_remove_childprofile_search_frequency_limit_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='childprofile',
            name='search_frequency_limit',
            field=models.PositiveIntegerField(blank=True, help_text='Maximum number of searches allowed within the time period', null=True),
        ),
        migrations.AddField(
            model_name='childprofile',
            name='search_time_end',
            field=models.TimeField(blank=True, default=datetime.time(18, 30), null=True),
        ),
        migrations.AddField(
            model_name='childprofile',
            name='search_time_start',
            field=models.TimeField(blank=True, default=datetime.time(8, 30), null=True),
        ),
    ]