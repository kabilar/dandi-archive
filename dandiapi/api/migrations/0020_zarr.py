# Generated by Django 3.2.8 on 2021-10-29 17:21

import uuid

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields

import dandiapi.api.models.asset
import dandiapi.api.storage


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0019_usermetadata'),
    ]

    operations = [
        migrations.CreateModel(
            name='ZarrArchive',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name='modified'
                    ),
                ),
                ('zarr_id', models.UUIDField(db_index=True, default=uuid.uuid4, unique=True)),
                ('name', models.CharField(max_length=512)),
                ('file_count', models.IntegerField(default=0)),
                ('size', models.IntegerField(default=0)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ZarrUploadFile',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name='modified'
                    ),
                ),
                ('path', models.CharField(max_length=512)),
                (
                    'blob',
                    models.FileField(
                        blank=True,
                        storage=dandiapi.api.storage.get_storage,
                        upload_to='',
                    ),
                ),
                (
                    'etag',
                    models.CharField(
                        max_length=40,
                        validators=[
                            django.core.validators.RegexValidator('^[0-9a-f]{32}(-[1-9][0-9]*)?$')
                        ],
                    ),
                ),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='asset',
            options={},
        ),
        migrations.AlterField(
            model_name='asset',
            name='blob',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='assets',
                to='api.assetblob',
            ),
        ),
        migrations.AddField(
            model_name='zarruploadfile',
            name='zarr_archive',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='active_uploads',
                to='api.zarrarchive',
            ),
        ),
        migrations.AddField(
            model_name='asset',
            name='zarr',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='assets',
                to='api.zarrarchive',
            ),
        ),
        migrations.AddConstraint(
            model_name='asset',
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(('blob__isnull', True), ('zarr__isnull', False)),
                    models.Q(('blob__isnull', False), ('zarr__isnull', True)),
                    _connector='OR',
                ),
                name='exactly-one-blob',
            ),
        ),
    ]
