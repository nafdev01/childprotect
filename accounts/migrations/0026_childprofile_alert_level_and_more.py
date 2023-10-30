# Generated by Django 5.0a1 on 2023-10-30 05:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0025_childsettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='childprofile',
            name='alert_level',
            field=models.CharField(choices=[('S', 'Strict'), ('M', 'Moderate'), ('L', 'Low')], default='M', max_length=10),
        ),
        migrations.AddField(
            model_name='childprofile',
            name='search_frequency_limit',
            field=models.PositiveIntegerField(blank=True, help_text='Maximum number of searches allowed within the time period', null=True),
        ),
        migrations.AddField(
            model_name='childprofile',
            name='search_time_end',
            field=models.TimeField(blank=True, default=datetime.datetime(1, 1, 1, 15, 32, 44, tzinfo=datetime.timezone.utc), null=True),
        ),
        migrations.AddField(
            model_name='childprofile',
            name='search_time_start',
            field=models.TimeField(blank=True, default=datetime.datetime(1, 1, 1, 5, 32, 44, tzinfo=datetime.timezone.utc), null=True),
        ),
        migrations.DeleteModel(
            name='ChildSettings',
        ),
    ]