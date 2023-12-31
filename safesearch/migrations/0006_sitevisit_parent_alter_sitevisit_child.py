# Generated by Django 5.0a1 on 2023-11-05 05:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('safesearch', '0005_sitevisit_delete_sitevisite'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='sitevisit',
            name='parent',
            field=models.ForeignKey(limit_choices_to={'user_type': 'CH'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='siteschildrenvisited', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='sitevisit',
            name='child',
            field=models.ForeignKey(limit_choices_to={'user_type': 'CH'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='siteschildvisited', to=settings.AUTH_USER_MODEL),
        ),
    ]
