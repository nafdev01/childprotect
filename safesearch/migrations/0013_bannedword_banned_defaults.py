# Generated by Django 4.2.5 on 2023-09-22 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('safesearch', '0012_remove_searchphrase_no_of_results'),
    ]

    operations = [
        migrations.AddField(
            model_name='bannedword',
            name='banned_defaults',
            field=models.BooleanField(default=False),
        ),
    ]
