# Generated by Django 5.0a1 on 2023-10-09 08:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('safesearch', '0022_rename_request_timestamp_unbanrequest_requested_on_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flaggedsearch',
            name='search_phrase',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='safesearch.searchphrase'),
        ),
    ]
