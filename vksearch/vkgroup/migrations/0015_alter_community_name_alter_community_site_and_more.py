# Generated by Django 4.1.3 on 2022-11-12 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vkgroup", "0014_alter_community_deactivated_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="community",
            name="name",
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="community",
            name="site",
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="community",
            name="status",
            field=models.TextField(null=True),
        ),
    ]