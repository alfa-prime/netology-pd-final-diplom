# Generated by Django 4.0.4 on 2022-05-22 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_backend', '0008_rename_link_shop_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='xurl',
            field=models.URLField(blank=True, null=True, verbose_name='xurl'),
        ),
        migrations.AlterField(
            model_name='shop',
            name='url',
            field=models.URLField(blank=True, null=True, verbose_name='url'),
        ),
    ]