# Generated by Django 5.0a1 on 2023-10-31 20:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0028_childprofile_search_frequency_limit_and_more'),
        ('safesearch', '0035_remove_bannedword_banned_for_bannedword_banned_for'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='bannedword',
            unique_together={('word', 'banned_for')},
        ),
    ]