# Generated by Django 5.0a1 on 2023-11-03 00:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0012_delete_message_alter_comment_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='created_by',
            field=models.ForeignKey(limit_choices_to={'user_type': 'PR'}, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username'),
        ),
    ]
