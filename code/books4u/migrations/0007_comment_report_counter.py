# Generated by Django 2.0.2 on 2018-03-25 01:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books4u', '0006_comment_modified'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='report_counter',
            field=models.IntegerField(default=0),
        ),
    ]