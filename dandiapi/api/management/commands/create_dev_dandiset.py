from __future__ import annotations
import hashlib

from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
import djclick as click

from dandiapi.api.models import AssetBlob
from dandiapi.api.services.asset import add_asset_to_version
from dandiapi.api.services.dandiset import create_dandiset
from dandiapi.api.services.metadata import validate_asset_metadata, validate_version_metadata
from dandiapi.api.tasks import calculate_sha256


@click.command()
@click.option('--name', default='Development Dandiset')
@click.option('--owner', 'email', required=True, help='The email address of the owner')
@click.option('--first_name', default='Randi The Admin')
@click.option('--last_name', default='Dandi')
def create_dev_dandiset(name: str, email: str, first_name: str, last_name: str):
    owner = User.objects.get(email=email)
    owner.first_name = first_name
    owner.last_name = last_name
    owner.save()

    version_metadata = {
        'description': 'An informative description',
        'license': ['spdx:CC0-1.0'],
    }
    _, draft_version = create_dandiset(
        user=owner, embargo=False, version_name=name, version_metadata=version_metadata
    )

    files_names_and_etags = [
        {"etag": "76d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/bar.txt"},
        {"etag": "86d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/buzz.txt"},
        {"etag": "a6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file2.txt"},
        {"etag": "b6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file3.txt"},
        {"etag": "c6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file4.txt"},
        {"etag": "d6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file5.txt"},
        {"etag": "e6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file6.txt"},
        {"etag": "f6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file7.txt"},
        {"etag": "g6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file8.txt"},
        {"etag": "h6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file9.txt"},
        {"etag": "i6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file10.txt"},
        {"etag": "j6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file11.txt"},
        {"etag": "k6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file12.txt"},
        {"etag": "l6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file13.txt"},
        {"etag": "m6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file14.txt"},
        {"etag": "n6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file15.txt"},
        {"etag": "o6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file16.txt"},
        {"etag": "p6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file17.txt"},
        {"etag": "q6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file18.txt"},
        {"etag": "r6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file19.txt"},
        {"etag": "s6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file20.txt"},
        {"etag": "t6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file21.txt"},
        {"etag": "u6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file22.txt"},
        {"etag": "v6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file23.txt"},
        {"etag": "w6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file24.txt"},
        {"etag": "x6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file25.txt"},
        {"etag": "y6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file26.txt"},
        {"etag": "z6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file27.txt"},
        {"etag": "06d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file28.txt"},
        {"etag": "16d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file29.txt"},
        {"etag": "26d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file30.txt"},
        {"etag": "36d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file31.txt"},
        {"etag": "46d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file32.txt"},
        {"etag": "56d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file33.txt"},
        {"etag": "66d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file34.txt"},
        {"etag": "76d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file35.txt"},
        {"etag": "86d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file36.txt"},
        {"etag": "96d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file37.txt"},
        {"etag": "a6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file38.txt"},
        {"etag": "b6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file39.txt"},
        {"etag": "c6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file40.txt"},
        {"etag": "d6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file41.txt"},
        {"etag": "e6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file42.txt"},
        {"etag": "f6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file43.txt"},
        {"etag": "g6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file44.txt"},
        {"etag": "h6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file45.txt"},
        {"etag": "i6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file46.txt"},
        {"etag": "j6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file47.txt"},
        {"etag": "k6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file48.txt"},
        {"etag": "l6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file49.txt"},
        {"etag": "m6d36e98f312e98ff908c8c82c8dd623-0", "file_name": "foo/file50.txt"},
    ]

    for file_name_and_etag in files_names_and_etags:
        file_size = 20
        file_content = b'A' * file_size
        uploaded_file = SimpleUploadedFile(
            name=file_name_and_etag["file_name"],
            content=file_content
        )
        etag = file_name_and_etag["etag"]

        try:
            asset_blob = AssetBlob.objects.get(etag=etag)
        except AssetBlob.DoesNotExist:
            # Since the SimpleUploadedFile is non-zarr asset, validation fails
            # without a sha2_256 initially provided.
            sha256_hash = hashlib.sha256(file_content).hexdigest()
            asset_blob = AssetBlob(
                blob_id=uuid4(), blob=uploaded_file, etag=etag, size=file_size, sha256=sha256_hash
            )
            asset_blob.save()
        asset_metadata = {
            'schemaVersion': settings.DANDI_SCHEMA_VERSION,
            'encodingFormat': 'text/plain',
            'schemaKey': 'Asset',
            'path': file_name_and_etag["file_name"],
        }
        asset = add_asset_to_version(
            user=owner, version=draft_version, asset_blob=asset_blob, metadata=asset_metadata
        )

        calculate_sha256(blob_id=asset_blob.blob_id)
        validate_asset_metadata(asset=asset)
        validate_version_metadata(version=draft_version)
