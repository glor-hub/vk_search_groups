# Generated by Django 4.1.3 on 2022-11-13 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vkgroup", "0017_alter_community_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="community",
            name="description",
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name="community",
            name="name",
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name="community",
            name="site",
            field=models.CharField(max_length=128, null=True),
        ),
    ]
