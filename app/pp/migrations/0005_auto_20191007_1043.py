# Generated by Django 2.2.6 on 2019-10-07 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pp', '0004_auto_20191005_1710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='jpg',
            field=models.CharField(blank=True, default='', help_text='relative file path to root directory containing all images', max_length=2000),
        ),
        migrations.AlterField(
            model_name='image',
            name='jpg_md5',
            field=models.UUIDField(help_text='md5 hash of the jpg file (as hex digest)', null=True),
        ),
    ]
