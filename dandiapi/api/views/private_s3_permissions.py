from __future__ import annotations

from typing import TYPE_CHECKING

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import datetime
from botocore.signers import CloudFrontSigner
import rsa
import json

if TYPE_CHECKING:
    from django.http.response import HttpResponseBase
    from rest_framework.request import Request

def rsa_signer(message):
    private_pem_location = 'temp' # Aaron - TODO
    with open(private_pem_location, 'r') as key_file:
        private_key = rsa.PrivateKey.load_pkcs1(key_file.read())
    return rsa.sign(message, private_key, 'SHA-1')


def get_cloudfront_cookies():
    key_pair_id = 'populate'  # Aaron - TODO
    asset_url_folder = 'populate'  # Aaron - TODO asset_url_folder should be parent folder for all zarr, etc. assets in LINC Archive -- should be OS Env Secret
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

    cloudfront_signer = CloudFrontSigner(key_pair_id, rsa_signer)
    cookies = cloudfront_signer.generate_cookies(policy=json.dumps(policy), secure=True)
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
    cookies = get_cloudfront_cookies()
    response_data = {"message": "Cookie successfully generated"}
    response = Response(response_data)
    for cookie_name, cookie_value in cookies.items():
        response.set_cookie(
            key=cookie_name,
            value=cookie_value['value'],
            max_age=cookie_value.get('max-age'),
            expires=cookie_value.get('expires'),
            secure=cookie_value.get('secure', True),
            httponly=cookie_value.get('httponly', True)
        )

    return response
