# Generated by Django 3.0.6 on 2020-05-11 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_auto_20200511_1348'),
    ]

    operations = [
        migrations.AddField(
            model_name='ogroupmembers',
            name='date_joined',
            field=models.DateTimeField(auto_now_add=True, default='2019-01-05T05:22', verbose_name='Date joined'),
            preserve_default=False,
        ),
    ]
