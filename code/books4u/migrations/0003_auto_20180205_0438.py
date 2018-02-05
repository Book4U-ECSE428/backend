# Generated by Django 2.0.1 on 2018-02-05 04:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books4u', '0002_auto_20180204_0509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='books4u.BookCategory'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='index',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Unknown', 'Unknown')], default='Male', max_length=20),
        ),
        migrations.AlterField(
            model_name='vote',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books4u.User'),
        ),
    ]
