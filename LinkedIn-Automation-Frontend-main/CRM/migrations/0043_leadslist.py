# Generated by Django 4.2.3 on 2024-04-29 20:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0042_alter_profile_about'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeadsList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.TextField()),
                ('name', models.TextField()),
                ('linkedinuser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CRM.linkedin_user')),
            ],
        ),
    ]
