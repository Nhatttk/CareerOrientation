# Generated by Django 4.2.11 on 2024-07-30 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_remove_careerprofile_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='careerprofile',
            name='is_teacher_mentor',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
