# Generated by Django 4.2.5 on 2023-09-20 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_user_managers_and_more'),
        ('safesearch', '0010_flaggedalert_reviewed_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bannedword',
            name='word',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterUniqueTogether(
            name='bannedword',
            unique_together={('word', 'banned_by')},
        ),
    ]
