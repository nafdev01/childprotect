# Generated by Django 4.2.5 on 2023-09-18 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('safesearch', '0003_flaggedalert'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchphrase',
            name='no_of_results',
            field=models.IntegerField(default=4),
        ),
    ]