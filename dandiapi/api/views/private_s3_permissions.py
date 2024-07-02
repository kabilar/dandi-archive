from __future__ import annotations

import base64
import datetime
import io
import json
import os
from typing import TYPE_CHECKING
import urllib

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from dandiapi.api.storage import get_boto_client, get_storage


def construct_neuroglancer_url(source, layer_name):
    neuroglancer_url = os.getenv('CLOUDFRONT_NEUROGLANCER_URL')
    base_url = f'{neuroglancer_url}/cloudfront/frontend/index.html#!'
    json_object = {
        "layers": [
            {
                "type": "new",
                "source": source,
                "tab": "source",
                "name": layer_name
            }
        ],
        "selectedLayer": {
            "visible": True,
            "layer": layer_name
        },
        "layout": "4panel"
    }

    json_str = json.dumps(json_object)
    encoded_json = urllib.parse.quote(json_str)
    return f"{base_url}{encoded_json}"


def _replace_unsupported_chars(some_str):
    """Replace unsupported chars: '+=/' with '-_~'."""
    return some_str.replace("+", "-") \
        .replace("=", "_") \
        .replace("/", "~")


def _in_a_month():
    """Returns a UTC POSIX timestamp for one month in the future."""
    one_month_later = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=30)
    return int(one_month_later.timestamp())

def rsa_signer(message, key):
    """
    Sign a message using RSA private key with PKCS#1 v1.5 padding and SHA-1 hash.

    :param message: The message to sign
    :param key: RSA private key in PEM format
    :return: The signature
    """
    private_key = load_pem_private_key(
        key,
        password=None
    )

    # Updated signing process
    return private_key.sign(
        message,
        padding.PKCS1v15(),
        hashes.SHA1()
    )



def generate_policy_cookie(url):
    """Returns a tuple: (policy json, policy base64)."""
    policy_dict = {
        "Statement": [
            {
                "Resource": f'{url}/*',
                "Condition": {
                    "DateLessThan": {
                        "AWS:EpochTime": _in_a_month()
                    }
                }
            }
        ]
    }

    # Using separators=(',', ':') removes seperator whitespace
    policy_json = json.dumps(policy_dict, separators=(",", ":"))

    policy_64 = str(base64.b64encode(policy_json.encode("utf-8")), "utf-8")
    policy_64 = _replace_unsupported_chars(policy_64)
    return policy_json, policy_64


def generate_signature(policy, key):
    """Creates a signature for the policy from the key, returning a string."""
    sig_bytes = rsa_signer(policy.encode("utf-8"), key)
    return _replace_unsupported_chars(str(base64.b64encode(sig_bytes), "utf-8"))


def generate_cookies(policy, signature):
    """Returns a dictionary for cookie values in the form 'COOKIE NAME': 'COOKIE VALUE'."""
    return {
        "CloudFront-Policy": policy,
        "CloudFront-Signature": signature,
        "CloudFront-Key-Pair-Id": os.getenv('CLOUDFRONT_PEM_KEY_ID')
    }


def generate_signed_cookies(key):
    neuroglancer_url = os.getenv('CLOUDFRONT_NEUROGLANCER_URL')
    policy_json, policy_64 = generate_policy_cookie(neuroglancer_url)
    signature = generate_signature(policy_json, key)
    return generate_cookies(policy_64, signature)


if TYPE_CHECKING:
    from django.http.response import HttpResponseBase
    from rest_framework.request import Request

@swagger_auto_schema(
    method='GET',
    responses={200: None},
    operation_summary='Provides presigned cookie for retrieving S3 assets exposed '
                      'via AWS CloudFront Distributions',
    operation_description='',
)
@api_view(['GET'])
@parser_classes([JSONParser])
@permission_classes([IsAuthenticated])
def presigned_cookie_s3_cloudfront_view(request: Request, asset_path=None) -> HttpResponseBase:
    # Get Private PEM Key from S3
    client = get_boto_client(get_storage())
    private_pem_key = os.getenv('CLOUDFRONT_PRIVATE_PEM_S3_LOCATION')
    response = client.get_object(Bucket=settings.DANDI_DANDISETS_BUCKET_NAME, Key=private_pem_key)
    pem_content = response['Body'].read()

    with io.BytesIO(pem_content) as pem_file:
        cookies = generate_signed_cookies(pem_file.read())

    if not asset_path:
        response_data = {"message": "Cookies successfully generated"}
    else:
        replacement_url = os.getenv('CLOUDFRONT_NEUROGLANCER_URL')
        parts = asset_path.split('/')
        file_type_prefix = parts[3]
        cloudfront_s3_location = replacement_url + '/' + '/'.join(parts[3:])

        if file_type_prefix != 'zarr':
            file_type_prefix = 'nifti'

        complete_url = construct_neuroglancer_url(
            f'{file_type_prefix}://{cloudfront_s3_location}',
            parts[4]
        )

        response_data = {
            "full_url": complete_url
        }

    response = Response(response_data)
    response['Access-Control-Allow-Credentials'] = 'true'
    response['Access-Control-Allow-Origin'] = request.headers.get('Origin', 'https://lincbrain.org')
    response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'  # Adjust as needed
    response['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type'  # Adjust as needed

    for cookie_name, cookie_value in cookies.items():
        response.set_cookie(
            key=cookie_name,
            value=cookie_value,
            secure=True,
            httponly=True,
            domain=f".{os.getenv('CLOUDFRONT_BASE_URL')}"
        )

    return response
