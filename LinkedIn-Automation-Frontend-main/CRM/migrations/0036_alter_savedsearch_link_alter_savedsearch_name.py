# Generated by Django 5.0.3 on 2024-04-04 21:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("CRM", "0035_rename_linkedin_user_savedsearch_linkedinuser"),
    ]

    operations = [
        migrations.AlterField(
            model_name="savedsearch",
            name="link",
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="savedsearch",
            name="name",
            field=models.TextField(),
        ),
    ]
