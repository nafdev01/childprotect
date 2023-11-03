# Generated by Django 5.0a1 on 2023-11-03 01:07

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BannedDefault',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=250)),
                ('slug', models.SlugField(blank=True, editable=False, max_length=250, null=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('category', models.CharField(choices=[('VC', 'Violent and Disturbing Content'), ('OL', 'Offensive Language'), ('DR', 'Drugs'), ('AC', 'Adult Content')], default='OL', max_length=2)),
                ('banned_type', models.CharField(choices=[('P', 'Phrase'), ('W', 'Word')], default='W', max_length=2)),
            ],
            options={
                'verbose_name': 'Banned Default',
                'verbose_name_plural': 'Banned Defaults',
                'unique_together': {('word', 'category')},
            },
        ),
        migrations.CreateModel(
            name='BannedWord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=250)),
                ('slug', models.SlugField(blank=True, editable=False, max_length=250, null=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('reason', models.CharField(choices=[('VC', 'Violent and Disturbing Content'), ('OL', 'Offensive Language'), ('DR', 'Drugs'), ('AC', 'Adult Content')], default='OL', max_length=2)),
                ('is_banned', models.BooleanField(default=True)),
                ('banned_type', models.CharField(choices=[('P', 'Phrase'), ('W', 'Word')], default='W', max_length=2)),
                ('from_default', models.BooleanField(default=False)),
                ('banned_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.parentprofile')),
                ('banned_for', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.childprofile')),
            ],
            options={
                'verbose_name': 'Banned Word',
                'verbose_name_plural': 'Banned Words',
                'ordering': ['word'],
                'unique_together': {('word', 'banned_for')},
            },
        ),
        migrations.CreateModel(
            name='SearchPhrase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phrase', models.CharField(max_length=256)),
                ('slug', models.SlugField(blank=True, editable=False, max_length=250, null=True)),
                ('search_status', models.CharField(choices=[('SF', 'Safe'), ('SP', 'Suspicious'), ('FL', 'Flagged')], default='SF', max_length=2)),
                ('searched_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('searched_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.childprofile')),
            ],
            options={
                'verbose_name': 'Search Phrase',
                'verbose_name_plural': 'Search Phrases',
                'ordering': ['-searched_on'],
            },
        ),
        migrations.CreateModel(
            name='SearchAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flagged_on', models.DateTimeField(editable=False, null=True)),
                ('been_reviewed', models.BooleanField(default=False)),
                ('reviewed_on', models.DateTimeField(null=True)),
                ('reviewed_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.parentprofile')),
                ('searched_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.childprofile')),
                ('flagged_search', models.OneToOneField(limit_choices_to={'search_status': 'FL'}, on_delete=django.db.models.deletion.CASCADE, to='safesearch.searchphrase')),
            ],
            options={
                'verbose_name': 'Flagged Alert',
                'verbose_name_plural': 'Flagged Alerts',
                'ordering': ['been_reviewed', '-flagged_on'],
            },
        ),
        migrations.CreateModel(
            name='FlaggedWord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flagged_on', models.DateTimeField(auto_now_add=True)),
                ('flagged_word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='safesearch.bannedword')),
                ('flagged_search', models.ForeignKey(limit_choices_to={'search_status': 'FL'}, null=True, on_delete=django.db.models.deletion.CASCADE, to='safesearch.searchphrase')),
            ],
            options={
                'verbose_name': 'Flagged Word',
                'verbose_name_plural': 'Flagged Words',
            },
        ),
        migrations.CreateModel(
            name='UnbanRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField(null=True)),
                ('approved', models.BooleanField(default=False)),
                ('requested_on', models.DateTimeField(auto_now_add=True)),
                ('been_reviewed', models.BooleanField(default=False)),
                ('reviewed_on', models.DateTimeField(null=True)),
                ('seen_by_child', models.BooleanField(default=False)),
                ('seen_on', models.DateTimeField(null=True)),
                ('banned_word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='safesearch.bannedword')),
                ('requested_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.childprofile')),
            ],
            options={
                'verbose_name': 'Unban Request',
                'verbose_name_plural': 'Unban Requests',
                'ordering': ['-requested_on'],
                'unique_together': {('banned_word', 'requested_by')},
            },
        ),
    ]
