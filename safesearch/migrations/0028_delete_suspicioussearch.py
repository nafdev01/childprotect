# Generated by Django 5.0a1 on 2023-10-26 06:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('safesearch', '0027_alter_flaggedalert_flagged_search_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SuspiciousSearch',
        ),
    ]
