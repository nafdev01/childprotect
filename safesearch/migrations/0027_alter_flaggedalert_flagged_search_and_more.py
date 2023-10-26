# Generated by Django 5.0a1 on 2023-10-25 03:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('safesearch', '0026_remove_searchphrase_allowed_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flaggedalert',
            name='flagged_search',
            field=models.OneToOneField(limit_choices_to={'search_status': 'FL'}, on_delete=django.db.models.deletion.CASCADE, to='safesearch.searchphrase'),
        ),
        migrations.AlterField(
            model_name='flaggedword',
            name='flagged_search',
            field=models.ForeignKey(limit_choices_to={'search_status': 'FL'}, null=True, on_delete=django.db.models.deletion.CASCADE, to='safesearch.searchphrase'),
        ),
        migrations.DeleteModel(
            name='FlaggedSearch',
        ),
    ]