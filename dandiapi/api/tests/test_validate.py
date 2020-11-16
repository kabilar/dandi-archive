import hashlib

from django.core.files.base import ContentFile
import pytest

from dandiapi.api.models import Validation

from .fuzzy import TIMESTAMP_RE


@pytest.mark.django_db
def test_validate(api_client, user):
    api_client.force_authenticate(user=user)

    object_key = 'test.txt'
    contents = b'test content'

    h = hashlib.sha256()
    h.update(contents)
    sha256 = h.hexdigest()

    Validation.blob.field.storage.save(object_key, ContentFile(contents))

    assert (
        api_client.post(
            '/api/uploads/validate/',
            {
                'object_key': object_key,
                'sha256': sha256,
            },
            format='json',
        ).status_code
        == 204
    )

    validation = Validation.objects.get(sha256=sha256)
    assert validation.blob.name == object_key
    assert validation.state == Validation.State.IN_PROGRESS

    # TODO how to test that the celery job kicked off?


@pytest.mark.django_db
@pytest.mark.parametrize('state', [Validation.State.SUCCEEDED, Validation.State.FAILED])
def test_validate_no_object_key(api_client, user, state):
    api_client.force_authenticate(user=user)

    object_key = 'test.txt'
    contents = b'test content'

    h = hashlib.sha256()
    h.update(contents)
    sha256 = h.hexdigest()

    Validation.blob.field.storage.save(object_key, ContentFile(contents))

    # Save an existing Validation that will be updated
    Validation(blob=object_key, sha256=sha256, state=state).save()

    assert (
        api_client.post(
            '/api/uploads/validate/',
            {
                'sha256': sha256,
            },
            format='json',
        ).status_code
        == 204
    )

    validation = Validation.objects.get(sha256=sha256)
    assert validation.blob.name == object_key
    assert validation.state == Validation.State.IN_PROGRESS


@pytest.mark.django_db
def test_validate_no_object_key_wrong_sha256(api_client, user):
    api_client.force_authenticate(user=user)

    resp = api_client.post(
        '/api/uploads/validate/',
        {
            'sha256': 'wrong-sha256',
        },
        format='json',
    )
    assert resp.status_code == 400
    assert resp.data == ['A validation for an object with that checksum does not exist.']


@pytest.mark.django_db
def test_validate_in_progress_validation(api_client, user):
    api_client.force_authenticate(user=user)

    object_key = 'test.txt'
    contents = b'test content'

    h = hashlib.sha256()
    h.update(contents)
    sha256 = h.hexdigest()

    Validation.blob.field.storage.save(object_key, ContentFile(contents))

    # Save an existing Validation that will be updated
    Validation(blob=object_key, sha256=sha256, state=Validation.State.IN_PROGRESS).save()

    resp = api_client.post(
        '/api/uploads/validate/',
        {
            'object_key': object_key,
            'sha256': sha256,
        },
        format='json',
    )
    assert resp.status_code == 400
    assert resp.data == ['Validation already in progress.']


@pytest.mark.django_db
def test_validate_object_does_not_exist(api_client, user):
    api_client.force_authenticate(user=user)

    object_key = 'does-not-exist.txt'
    contents = b'test content'

    h = hashlib.sha256()
    h.update(contents)
    sha256 = h.hexdigest()

    resp = api_client.post(
        '/api/uploads/validate/',
        {
            'object_key': object_key,
            'sha256': sha256,
        },
        format='json',
    )
    assert resp.status_code == 400
    assert resp.data == ['Object does not exist.']


@pytest.mark.django_db
@pytest.mark.parametrize(
    'state', [Validation.State.IN_PROGRESS, Validation.State.SUCCEEDED, Validation.State.FAILED]
)
def test_get_validation(api_client, user, state):
    api_client.force_authenticate(user=user)

    object_key = 'does-not-exist.txt'
    contents = b'test content'

    h = hashlib.sha256()
    h.update(contents)
    sha256 = h.hexdigest()

    # Save an existing Validation that will be updated
    Validation(blob=object_key, sha256=sha256, state=state).save()

    assert api_client.get(
        f'/api/uploads/validations/{sha256}/',
        {
            'object_key': object_key,
            'sha256': sha256,
        },
        format='json',
    ).data == {
        'state': str(state),
        'sha256': sha256,
        'created': TIMESTAMP_RE,
        'modified': TIMESTAMP_RE,
    }


# TODO: Test the celery task