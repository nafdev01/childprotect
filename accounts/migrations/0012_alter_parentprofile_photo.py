# Generated by Django 5.0a1 on 2023-10-05 20:24

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_alter_parentprofile_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parentprofile',
            name='photo',
            field=models.ImageField(blank=True, default='default.png', upload_to=accounts.models.parent_profile_photo_path),
        ),
    ]
