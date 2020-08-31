# Generated by Django 3.0.6 on 2020-06-02 07:21
import uuid

from django.conf import settings
import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion

import dandi.publish.models
import dandi.publish.storage


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Dandiset',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'draft_folder_id',
                    models.CharField(
                        max_length=24,
                        validators=[django.core.validators.RegexValidator('^[0-9a-f]{24}$')],
                    ),
                ),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['id']},
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'version',
                    models.CharField(
                        default=dandi.publish.models.version._get_default_version,
                        max_length=13,
                        validators=[django.core.validators.RegexValidator('^0\\.\\d{6}\\.\\d{4}$')],
                    ),
                ),
                (
                    'metadata',
                    django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
                ),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                (
                    'dandiset',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='versions',
                        to='publish.Dandiset',
                    ),
                ),
            ],
            options={'ordering': ['dandiset', 'version'], 'get_latest_by': 'created'},
        ),
        migrations.CreateModel(
            name='Asset',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('path', models.CharField(max_length=512)),
                ('size', models.BigIntegerField()),
                (
                    'sha256',
                    models.CharField(
                        max_length=64,
                        validators=[django.core.validators.RegexValidator('^[0-9a-f]{64}$')],
                    ),
                ),
                (
                    'metadata',
                    django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
                ),
                (
                    'blob',
                    models.FileField(
                        blank=True,
                        storage=dandi.publish.storage.create_s3_storage(
                            settings.DANDI_DANDISETS_BUCKET_NAME
                        ),
                        upload_to=dandi.publish.models.asset._get_asset_blob_prefix,
                    ),
                ),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                (
                    'version',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='assets',
                        to='publish.Version',
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name='version',
            index=models.Index(
                fields=['dandiset', 'version'], name='publish_ver_dandise_5d36c6_idx'
            ),
        ),
        migrations.AlterUniqueTogether(name='version', unique_together={('dandiset', 'version')}),
        migrations.AddIndex(
            model_name='asset',
            index=models.Index(fields=['uuid'], name='publish_ass_uuid_94d83f_idx'),
        ),
        migrations.AddIndex(
            model_name='asset',
            index=models.Index(fields=['version', 'path'], name='publish_ass_version_eea2b3_idx'),
        ),
    ]