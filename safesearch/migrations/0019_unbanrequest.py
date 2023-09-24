# Generated by Django 4.2.5 on 2023-09-24 16:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('safesearch', '0018_bannedword_default_ban'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnbanRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('been_reviewed', models.BooleanField(default=False)),
                ('banned_word', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='safesearch.bannedword')),
                ('requested_by', models.OneToOneField(limit_choices_to={'user_type': 'CH'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Unban Request',
                'verbose_name_plural': 'Unban Requests',
            },
        ),
    ]
