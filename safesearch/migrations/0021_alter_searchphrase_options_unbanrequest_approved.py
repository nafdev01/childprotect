# Generated by Django 5.0a1 on 2023-10-09 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('safesearch', '0020_alter_bannedword_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='searchphrase',
            options={'ordering': ['searched_on'], 'verbose_name': 'Search Phrase', 'verbose_name_plural': 'Search Phrases'},
        ),
        migrations.AddField(
            model_name='unbanrequest',
            name='approved',
            field=models.BooleanField(default=False),
        ),
    ]