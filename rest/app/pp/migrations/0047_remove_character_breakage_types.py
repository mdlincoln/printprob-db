# Generated by Django 3.2.14 on 2022-11-01 20:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pp', '0046_alter_character_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='character',
            name='breakage_types',
        ),
    ]
