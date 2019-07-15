# Generated by Django 2.2.3 on 2019-07-15 20:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pp', '0002_auto_20190715_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='character',
            name='primary_image',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='depicts_image', to='pp.Image'),
        ),
        migrations.AlterField(
            model_name='line',
            name='primary_image',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='depicts_line', to='pp.Image'),
        ),
        migrations.AlterField(
            model_name='page',
            name='primary_image',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='depicts_page', to='pp.Image'),
        ),
        migrations.AlterField(
            model_name='spread',
            name='primary_image',
            field=models.ForeignKey(blank=True, help_text='Image depicting this spread', on_delete=django.db.models.deletion.CASCADE, related_name='depicts_spreads', to='pp.Image'),
        ),
    ]
