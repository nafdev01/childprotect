# Generated by Django 5.0a1 on 2023-10-20 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_alter_parentprofile_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='childprofile',
            name='date_of_birth',
            field=models.DateField(help_text='Only children beween the ages of 9 and 15 are allowed to register.'),
        ),
    ]