# Generated by Django 3.0.5 on 2022-01-15 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(default='User545f51d6-43be-4dd6-ba89-b547c1b32b06', max_length=25, unique=True),
        ),
    ]
