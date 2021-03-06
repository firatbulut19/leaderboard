# Generated by Django 3.1.7 on 2021-03-10 17:32

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('display_name', models.CharField(max_length=255)),
                ('country', models.CharField(default='tr', max_length=255)),
                ('points', models.IntegerField(default=0)),
                ('rank', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['points'],
            },
        ),
    ]
