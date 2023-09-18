# Generated by Django 4.2.5 on 2023-09-18 20:13

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('safesearch', '0006_remove_searchphrase_searched_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchphrase',
            name='searched_on',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
