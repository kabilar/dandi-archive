# Generated by Django 4.1.13 on 2024-03-27 18:45
from __future__ import annotations

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('zarr', '0002_null_charfield'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='embargoedzarrarchive',
            options={'get_latest_by': 'modified', 'ordering': ['created']},
        ),
        migrations.AlterModelOptions(
            name='zarrarchive',
            options={'get_latest_by': 'modified', 'ordering': ['created']},
        ),
    ]