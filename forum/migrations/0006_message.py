# Generated by Django 5.0a1 on 2023-10-30 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0005_contact_contactresponse'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]