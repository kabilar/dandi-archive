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

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from dandiapi.api.storage import get_boto_client, get_storage
from django.conf import settings

def _replace_unsupported_chars(some_str):
    """Replace unsupported chars: '+=/' with '-_~'"""
    return some_str.replace("+", "-") \
        .replace("=", "_") \
        .replace("/", "~")


def _in_an_hour():
    """Returns a UTC POSIX timestamp for one hour in the future"""
    return int(time.time()) + (60*60)


def rsa_signer(message, key):
    """
    Sign a message using RSA private key with PKCS#1 v1.5 padding and SHA-1 hash.

    :param message: The message to sign
    :param key: RSA private key in PEM format
    :return: The signature
    """
    private_key = load_pem_private_key(
        key,
        password=None,  # Replace with password if the private key is encrypted
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
                "Resource": url,
                "Condition": {
                    "DateLessThan": {
                        "AWS:EpochTime": _in_an_hour()
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


def generate_cookies(policy, signature, cloudfront_id):
    """Returns a dictionary for cookie values in the form 'COOKIE NAME': 'COOKIE VALUE'"""
    return {
        "CloudFront-Policy": policy,
        "CloudFront-Signature": signature,
        "CloudFront-Key-Pair-Id": cloudfront_id
    }


def generate_signed_cookies(url, cloudfront_id, key):
    policy_json, policy_64 = generate_policy_cookie(url)
    signature = generate_signature(policy_json, key)
    return generate_cookies(policy_64, signature, cloudfront_id)


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
def presigned_cookie_s3_cloudfront_view(request: Request) -> HttpResponseBase:

    # Get Private PEM Key from S3
    client = get_boto_client(get_storage())
    private_pem_key = f'cloudfront/private_key_{settings.DJANGO_SENTRY_ENVIRONMENT}_new.pem'
    response = client.get_object(Bucket=settings.DANDI_DANDISETS_BUCKET_NAME, Key=private_pem_key)
    pem_content = response['Body'].read()

    public_cloudfront_key_id = 'KZQ92MU8PCLJ8'  # pkcs1 -- lincbrain AWS -- staging-key
    neuroglancer_url = 'https://neuroglancer.lincbrain.org/*'

    with io.BytesIO(pem_content) as pem_file:
        cookies = generate_signed_cookies(neuroglancer_url, public_cloudfront_key_id, pem_file.read())

    response_data = {"message": cookies}
    response = Response(response_data)
    for cookie_name, cookie_value in cookies.items():
            response.set_cookie(
                key=cookie_name,
                value=cookie_value,
                secure=True,
                httponly=True,
                domain=".lincbrain.org"
            )

    return response
