# Generated by Django 5.0a1 on 2023-10-13 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0002_comment_type_of_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='posted_on',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='updated_on',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
