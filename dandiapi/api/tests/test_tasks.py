import hashlib

from django.conf import settings
from django.core.files.storage import Storage
import pytest

from dandiapi.api import tasks
from dandiapi.api.models import Asset, AssetBlob, Version


@pytest.mark.django_db
def test_calculate_checksum_task(storage: Storage, asset_blob_factory):
    # Pretend like AssetBlob was defined with the given storage
    AssetBlob.blob.field.storage = storage

    asset_blob = asset_blob_factory(sha256=None)

    h = hashlib.sha256()
    h.update(asset_blob.blob.read())
    sha256 = h.hexdigest()

    tasks.calculate_sha256(asset_blob.blob_id)

    asset_blob.refresh_from_db()

    assert asset_blob.sha256 == sha256


@pytest.mark.django_db
def test_write_manifest_files(storage: Storage, version: Version, asset_factory):
    # Pretend like AssetBlob was defined with the given storage
    # The task piggybacks off of the AssetBlob storage to write the yamls
    AssetBlob.blob.field.storage = storage

    # Create a new asset in the version so there is information to write
    version.assets.add(asset_factory())

    # All of these files should be generated by the task
    assets_yaml_path = (
        f'{settings.DANDI_DANDISETS_BUCKET_PREFIX}'
        f'dandisets/{version.dandiset.identifier}/{version.version}/assets.yaml'
    )
    dandiset_yaml_path = (
        f'{settings.DANDI_DANDISETS_BUCKET_PREFIX}'
        f'dandisets/{version.dandiset.identifier}/{version.version}/dandiset.yaml'
    )
    assets_jsonld_path = (
        f'{settings.DANDI_DANDISETS_BUCKET_PREFIX}'
        f'dandisets/{version.dandiset.identifier}/{version.version}/assets.jsonld'
    )
    dandiset_jsonld_path = (
        f'{settings.DANDI_DANDISETS_BUCKET_PREFIX}'
        f'dandisets/{version.dandiset.identifier}/{version.version}/dandiset.jsonld'
    )
    collection_jsonld_path = (
        f'{settings.DANDI_DANDISETS_BUCKET_PREFIX}'
        f'dandisets/{version.dandiset.identifier}/{version.version}/collection.jsonld'
    )

    tasks.write_manifest_files(version.id)

    assert storage.exists(assets_yaml_path)
    assert storage.exists(dandiset_yaml_path)
    assert storage.exists(assets_jsonld_path)
    assert storage.exists(dandiset_jsonld_path)
    assert storage.exists(collection_jsonld_path)


@pytest.mark.django_db
def test_validate_asset_metadata(asset: Asset):
    tasks.validate_asset_metadata(asset.id)

    asset.refresh_from_db()

    assert asset.status == Asset.Status.VALID
    assert asset.validation_errors == []


@pytest.mark.django_db
def test_validate_asset_metadata_no_schema_version(asset: Asset):
    asset.metadata = {}
    asset.metadata.save()

    tasks.validate_asset_metadata(asset.id)

    asset.refresh_from_db()

    assert asset.status == Asset.Status.INVALID
    assert len(asset.validation_errors) == 1
    assert asset.validation_errors[0]['field'] == ''
    assert asset.validation_errors[0]['message'].startswith('Metadata version None is not allowed.')


@pytest.mark.django_db
def test_validate_asset_metadata_malformed_schema_version(asset: Asset):
    asset.metadata['schemaVersion'] = 'xxx'
    asset.metadata.save()

    tasks.validate_asset_metadata(asset.id)

    asset.refresh_from_db()

    assert asset.status == Asset.Status.INVALID
    assert len(asset.validation_errors) == 1
    assert asset.validation_errors[0]['field'] == ''
    assert asset.validation_errors[0]['message'].startswith('Metadata version xxx is not allowed.')


@pytest.mark.django_db
def test_validate_asset_metadata_no_encoding_format(asset: Asset):
    del asset.metadata['encodingFormat']
    asset.metadata.save()

    tasks.validate_asset_metadata(asset.id)

    asset.refresh_from_db()

    assert asset.status == Asset.Status.INVALID
    assert asset.validation_errors == [{'field': 'encodingFormat', 'message': 'field required'}]


@pytest.mark.django_db
def test_validate_asset_metadata_no_digest(asset: Asset):
    asset.blob.sha256 = None
    asset.blob.save()

    tasks.validate_asset_metadata(asset.id)

    asset.refresh_from_db()

    assert asset.status == Asset.Status.INVALID
    assert asset.validation_errors == [
        {'field': 'digest', 'message': 'Digest is missing dandi-etag or sha256 keys.'}
    ]


@pytest.mark.django_db
def test_validate_asset_metadata_malformed_keywords(asset: Asset):
    asset.metadata['keywords'] = 'foo'
    asset.metadata.save()

    tasks.validate_asset_metadata(asset.id)

    asset.refresh_from_db()

    assert asset.status == Asset.Status.INVALID
    assert asset.validation_errors == [
        {'field': 'keywords', 'message': 'value is not a valid list'}
    ]


@pytest.mark.django_db
def test_validate_version_metadata(version: Version, asset: Asset):
    version.assets.add(asset)

    tasks.validate_version_metadata(version.id)

    version.refresh_from_db()

    assert version.status == Version.Status.VALID
    assert version.validation_errors == []


@pytest.mark.django_db
def test_validate_version_metadata_no_schema_version(version: Version, asset: Asset):
    version.assets.add(asset)

    del version.metadata['schemaVersion']
    version.metadata.save()

    tasks.validate_version_metadata(version.id)

    version.refresh_from_db()

    assert version.status == Version.Status.INVALID
    assert len(version.validation_errors) == 1
    assert version.validation_errors[0]['field'] == ''
    assert version.validation_errors[0]['message'].startswith(
        'Metadata version None is not allowed.'
    )


@pytest.mark.django_db
def test_validate_version_metadata_malformed_schema_version(version: Version, asset: Asset):
    version.assets.add(asset)

    version.metadata['schemaVersion'] = 'xxx'
    version.metadata.save()

    tasks.validate_version_metadata(version.id)

    version.refresh_from_db()

    assert version.status == Version.Status.INVALID
    assert len(version.validation_errors) == 1
    assert version.validation_errors[0]['message'].startswith(
        'Metadata version xxx is not allowed.'
    )


@pytest.mark.django_db
def test_validate_version_metadata_no_description(version: Version, asset: Asset):
    version.assets.add(asset)

    del version.metadata['description']
    version.metadata.save()

    tasks.validate_version_metadata(version.id)

    version.refresh_from_db()

    assert version.status == Version.Status.INVALID
    assert version.validation_errors == [{'field': 'description', 'message': 'field required'}]


@pytest.mark.django_db
def test_validate_version_metadata_malformed_license(version: Version, asset: Asset):
    version.assets.add(asset)

    version.metadata['license'] = 'foo'
    version.metadata.save()

    tasks.validate_version_metadata(version.id)

    version.refresh_from_db()

    assert version.status == Version.Status.INVALID
    assert version.validation_errors == [
        {'field': 'license', 'message': 'value is not a valid list'}
    ]
