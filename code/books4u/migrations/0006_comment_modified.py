# Generated by Django 2.0.3 on 2018-03-17 03:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books4u', '0005_auto_20180307_1458'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='modified',
            field=models.BooleanField(default=False),
        ),
    ]
