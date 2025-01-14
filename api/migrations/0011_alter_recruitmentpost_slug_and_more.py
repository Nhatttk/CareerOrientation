# Generated by Django 4.2.11 on 2024-08-21 02:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0010_alter_careerprofile_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recruitmentpost',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='recruitmentpost',
            name='user_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_w_recruitment_post', to=settings.AUTH_USER_MODEL),
        ),
    ]
