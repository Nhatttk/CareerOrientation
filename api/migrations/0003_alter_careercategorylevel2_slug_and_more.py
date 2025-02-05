# Generated by Django 4.2.11 on 2024-07-30 01:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_careercategorylevel1_careercategorylevel2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='careercategorylevel2',
            name='slug',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='careerprofile',
            name='birthday',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='careerprofile',
            name='facebook',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='careerprofile',
            name='twitter',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='careerprofile',
            name='youtube',
            field=models.URLField(blank=True, null=True),
        ),
    ]
