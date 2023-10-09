# Generated by Django 5.0a1 on 2023-10-09 15:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_alter_parentprofile_photo'),
        ('safesearch', '0023_alter_flaggedsearch_search_phrase'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='unbanrequest',
            options={'ordering': ['-requested_on'], 'verbose_name': 'Unban Request', 'verbose_name_plural': 'Unban Requests'},
        ),
        migrations.AlterUniqueTogether(
            name='unbanrequest',
            unique_together={('banned_word', 'requested_by')},
        ),
    ]
