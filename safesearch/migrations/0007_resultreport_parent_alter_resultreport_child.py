# Generated by Django 5.0a1 on 2023-11-05 05:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('safesearch', '0006_sitevisit_parent_alter_sitevisit_child'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='resultreport',
            name='parent',
            field=models.ForeignKey(limit_choices_to={'user_type': 'CH'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reportedhildrenresults', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='resultreport',
            name='child',
            field=models.ForeignKey(limit_choices_to={'user_type': 'CH'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reportedhildresults', to=settings.AUTH_USER_MODEL),
        ),
    ]