# Generated by Django 4.2.3 on 2024-05-04 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0047_profile_lead_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='lead_last_contact',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
