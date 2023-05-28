# Generated by Django 4.2 on 2023-05-21 18:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ThingsCrossing', '0004_message_room'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='last_message_datetime',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='participant',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='ThingsCrossing.room'),
        ),
    ]