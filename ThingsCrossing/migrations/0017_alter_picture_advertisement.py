# Generated by Django 4.1.7 on 2023-04-03 15:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        (
            "ThingsCrossing",
            "0016_rename_advertisement_id_category_advertisement_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="picture",
            name="advertisement",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="images",
                to="ThingsCrossing.advertisement",
            ),
        ),
    ]
