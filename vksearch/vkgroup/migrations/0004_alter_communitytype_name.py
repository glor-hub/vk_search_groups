# Generated by Django 4.1.3 on 2022-11-02 22:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vkgroup", "0003_alter_community_type_alter_communitytype_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="communitytype",
            name="name",
            field=models.TextField(unique=True),
        ),
    ]