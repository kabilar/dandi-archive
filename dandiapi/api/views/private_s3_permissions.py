from __future__ import annotations

from typing import TYPE_CHECKING

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import time
import json
import base64
import io
import os
import neuroglancer
from neuroglancer.viewer_base import ViewerBase
from urllib.parse import quote

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from dandiapi.api.storage import get_boto_client, get_storage
from django.conf import settings

def ordered_dict_to_neuroglancer_url(ordered_dict, base_url):
    dict_data = json.loads(json.dumps(ordered_dict))

    json_str = json.dumps(dict_data)

    encoded_json = quote(json_str)

    full_url = f"{base_url}#!{encoded_json}"

    return full_url

def _replace_unsupported_chars(some_str):
    """Replace unsupported chars: '+=/' with '-_~'"""
    return some_str.replace("+", "-") \
        .replace("=", "_") \
        .replace("/", "~")


def _in_a_day():
    """Returns a UTC POSIX timestamp for one day in the future"""
    return int(time.time()) + (24 * 60 * 60)


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
    signature = private_key.sign(
        message,
        padding.PKCS1v15(),
        hashes.SHA1()
    )

    return signature


def generate_policy_cookie(url):
    """Returns a tuple: (policy json, policy base64)"""

    policy_dict = {
        "Statement": [
            {
                "Resource": f'{url}/*',
                "Condition": {
                    "DateLessThan": {
                        "AWS:EpochTime": _in_a_day()
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
    """Creates a signature for the policy from the key, returning a string"""
    sig_bytes = rsa_signer(policy.encode("utf-8"), key)
    sig_64 = _replace_unsupported_chars(str(base64.b64encode(sig_bytes), "utf-8"))
    return sig_64


def generate_cookies(policy, signature):
    """Returns a dictionary for cookie values in the form 'COOKIE NAME': 'COOKIE VALUE'"""
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
        response_data = {"message": "cookies successfully generated"}
    else:
        # https://linc-brain-mit-staging-us-east-2.s3.amazonaws.com/zarr/4bc0cab1-31a8-4305-9158-0e7fd7e12bcb/
        replacement_url = os.getenv('CLOUDFRONT_NEUROGLANCER_URL')
        parts = asset_path.split('/')
        file_prefix = parts[3]
        cloudfront_s3_location = replacement_url + '/' + '/'.join(parts[3:])

        if file_prefix != 'zarr':
            file_prefix = 'nifti'

        viewer = ViewerBase(token='1') # use ViewerBase instead of Viewer to not launch server
        with viewer.txn() as state:
            state.layers.append(
                name=parts[4],
                layer=neuroglancer.ImageLayer(
                    source=[f'{file_prefix}://' + cloudfront_s3_location],
                )
            )
            x = ordered_dict_to_neuroglancer_url(
                state._json_data,
                f'{replacement_url}/cloudfront/frontend/index.html'
            )
            print(x)

        response_data = {
            "url": cloudfront_s3_location,

        }

    response = Response(response_data)
    for cookie_name, cookie_value in cookies.items():
        response.set_cookie(
            key=cookie_name,
            value=cookie_value,
            secure=True,
            httponly=True,
            domain=f".{os.getenv('CLOUDFRONT_BASE_URL')}"
        )

    return response
