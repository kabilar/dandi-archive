from __future__ import annotations

from typing import TYPE_CHECKING

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from dandiapi.api.utils import CloudFrontCookieGenerator

import datetime
from botocore.signers import CloudFrontSigner
import rsa
import json

if TYPE_CHECKING:
    from django.http.response import HttpResponseBase
    from rest_framework.request import Request


def rsa_signer(message):
    import os
    print(os.getcwd())
    private_pem_location = 'private_key.pem' # Aaron - TODO
    with open(private_pem_location, 'r') as key_file:
        private_key = rsa.PrivateKey.load_pkcs1(key_file.read())
    return rsa.sign(message, private_key, 'SHA-1')


def get_cloudfront_cookies():
    key_pair_id = 'fa996026-f6b3-4979-b758-ccfdc7515ec8'  # test-bucket-key-group -- lincbrain AWS
    asset_url_folder = 'zarr'  # Aaron - TODO asset_url_folder should be parent folder for all zarr, etc. assets in LINC Archive -- should be OS Env Secret
    number_of_days = 1

    policy = {
        "Statement": [
            {
                "Resource": f"{asset_url_folder}/*",
                "Condition": {
                    "DateLessThan": {"AWS:EpochTime": int((datetime.datetime.now() + datetime.timedelta(days=number_of_days)).timestamp())}
                }
            }
        ]
    }
    print(3)
    cloudfront_signer = CloudFrontSigner(key_pair_id, rsa_signer)
    print(4)
    cookies = cloudfront_signer.generate_cookies(policy=json.dumps(policy), secure=True)
    print(5)
    return cookies

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
    expires_in_minutes = 20
    key_pair_id = 'fa996026-f6b3-4979-b758-ccfdc7515ec8'  # test-bucket-key-group -- lincbrain AWS
    object_url = 'https://d2du7pzm1jeax1.cloudfront.net/zarr'

    cloudfront_cookie_generator = CloudFrontCookieGenerator(private_key_file='private_key.pem')
    expires_at = int((datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_in_minutes)).timestamp())

    cookies = cloudfront_cookie_generator.create_signed_cookies(
        resource=object_url,
        keypair_id=key_pair_id,
        expires_at=expires_at
    )

    response_data = {"message": "Cookies successfully generated"}
    response = Response(response_data)
    for cookie_name, cookie_value in cookies.items():
        response.set_cookie(
            key=cookie_name,
            value=cookie_value,
            max_age=60*60*24,
            expires=60*60*24, # 1 day
            secure=True,
            httponly=True
        )

    return response
