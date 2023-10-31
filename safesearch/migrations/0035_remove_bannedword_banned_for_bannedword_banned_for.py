# Generated by Django 5.0a1 on 2023-10-31 18:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0028_childprofile_search_frequency_limit_and_more'),
        ('safesearch', '0034_alter_banneddefault_unique_together'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bannedword',
            name='banned_for',
        ),
        migrations.AddField(
            model_name='bannedword',
            name='banned_for',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.childprofile'),
        ),
    ]
