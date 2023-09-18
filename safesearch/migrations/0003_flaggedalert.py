# Generated by Django 4.2.5 on 2023-09-18 16:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_user_managers_and_more'),
        ('safesearch', '0002_rename_flaggedsearches_flaggedsearch'),
    ]

    operations = [
        migrations.CreateModel(
            name='FlaggedAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('been_reviewed', models.BooleanField(default=False)),
                ('reviewed_on', models.DateTimeField(null=True)),
                ('flagged_search', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='safesearch.flaggedsearch')),
                ('reviewed_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.parentprofile')),
            ],
            options={
                'verbose_name': 'Flagged Alert',
                'verbose_name_plural': 'Flagged Alerts',
            },
        ),
    ]
