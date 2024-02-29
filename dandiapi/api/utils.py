from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import base64
import json
import datetime

class CloudFrontCookieGenerator:

    def __init__(self, private_key_file):
        import os
        path = f'{os.getcwd()}/dandiapi/api/private_key.pem'
        with open(path, 'rb') as key_file:
            self.private_key = load_pem_private_key(
                key_file.read(),
                password=None,
            )

    def _sign_string(self, message):
        return self.private_key.sign(
            message,
            padding.PKCS1v15(),
            hashes.SHA1()
        )

    @staticmethod
    def _url_base64_encode(msg):
        msg_base64 = base64.b64encode(msg).decode('utf-8')
        msg_base64 = msg_base64.replace('+', '-').replace('=', '_').replace('/', '~')
        return msg_base64

    def generate_signature(self, policy):
        signature = self._sign_string(policy.encode('utf-8'))
        encoded_signature = self._url_base64_encode(signature)
        return encoded_signature

    def create_signed_cookies(self, resource, keypair_id, expires_at):
        policy = json.dumps({
            "Statement": [{
                "Resource": resource,
                "Condition": {
                    "DateLessThan": {"AWS:EpochTime": expires_at}
                }
            }]
        })

        encoded_policy = self._url_base64_encode(policy.encode('utf-8'))
        signature = self.generate_signature(policy)

        cookies = {
            "CloudFront-Policy": encoded_policy,
            "CloudFront-Signature": signature,
            "CloudFront-Key-Pair-Id": keypair_id
        }

        return cookies


# def create_signed_cookies(object_url, keypair_id, private_key_file, expire_minutes=20):
#
#     return cookies
#
# # Usage Example
# expires_in_minutes = 20  # Time in minutes for the cookies to expire
# object_url = 'https://d2du7pzm1jeax1.cloudfront.net/path/to/content'
# private_key_file = 'path/to/your/private-key.pem'  # Path to your PEM-encoded private key file
# keypair_id = 'APKAIXXXXXXXX'  # Your CloudFront key pair ID
#
# cookies = create_signed_cookies(object_url, keypair_id, private_key_file, expires_in_minutes)
# print(cookies)


# # Credit to https://gist.github.com/mekza/b7cdc0858aa1dd22b016/3b3614020ca312d8f0302b10a26506442532da66
#
# from boto.cloudfront.distribution import Distribution
# from cryptography.hazmat.primitives.asymmetric import padding
# from cryptography.hazmat.primitives import serialization
# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives import hashes
# import base64
#
#
# class CloudFrontCookieGenerator(Distribution):
#
#     def sign_rsa(self, message):
#         private_key = serialization.load_pem_private_key(self.keyfile, password=None,
#                                                          backend=default_backend())
#         signer = private_key.signer(padding.PKCS1v15(), hashes.SHA1())
#         message = message.encode('utf-8')
#         signer.update(message)
#         return signer.finalize()
#
#     def _sign_string(self, message, private_key_file=None, private_key_string=None):
#         if private_key_file:
#             self.keyfile = open(private_key_file, 'rb').read()
#         elif private_key_string:
#             self.keyfile = private_key_string.encode('utf-8')
#         return self.sign_rsa(message)
#
#     @staticmethod
#     def _url_base64_encode(msg):
#         """
#         Base64 encodes a string using the URL-safe characters specified by
#         Amazon.
#         """
#         msg_base64 = base64.b64encode(msg).decode('utf-8')
#         msg_base64 = msg_base64.replace('+', '-')
#         msg_base64 = msg_base64.replace('=', '_')
#         msg_base64 = msg_base64.replace('/', '~')
#         return msg_base64
#
#     def generate_signature(self, policy, private_key_file=None):
#         """
#         :param policy: no-whitespace json str (NOT encoded yet)
#         :param private_key_file: your .pem file with which to sign the policy
#         :return: encoded signature for use in cookie
#         """
#         # Distribution._create_signing_params()
#         signature = self._sign_string(policy, private_key_file)
#
#         # now base64 encode the signature & make URL safe
#         encoded_signature = self._url_base64_encode(signature)
#
#         return encoded_signature
#
#     def create_signed_cookies(self, url, private_key_file=None, keypair_id=None,
#                               expires_at=20, secure=True):
#         """
#         generate the Cloudfront download distirbution signed cookies
#         :param resource: The object or path of resource.
#                          Examples: 'dir/object.mp4', 'dir/*', '*'
#         :param private_key_file: Path to the private key file (pem encoded)
#         :param key_pair_id: ID of the keypair used to sign the cookie
#         :param expire_minutes:  The number of minutes until expiration
#         :param secure: use https or http protocol for Cloudfront URL - update
#                        to match your distribution settings.
#         :return: Cookies to be set
#         """
#
#         # generate no-whitespace json policy,
#         # then base64 encode & make url safe
#         policy = self._custom_policy(
#             url,
#             expires_at
#         )
#
#         encoded_policy = self._url_base64_encode(policy.encode('utf-8'))
#
#         # assemble the 3 Cloudfront cookies
#         signature = self.generate_signature(
#             policy, private_key_file=private_key_file
#         )
#         cookies = {
#             "CloudFront-Policy": encoded_policy,
#             "CloudFront-Signature": signature,
#             "CloudFront-Key-Pair-Id": keypair_id
#         }
#         return cookies
#
#
# def sign_to_cloudfront(object_url, expires_at):
#     """ Sign URL to distribute file"""
#     cloudfront_cookie_generator = CloudFrontCookieGenerator()
#     url = cloudfront_cookie_generator.create_signed_url(
#        url=object_url,
#        keypair_id="XXXXXXXXXXX",
#        expire_time=expires_at,
#        private_key_file="ssl/key.pem"
#     )
#
#     return url
#
#
# def create_signed_cookies(object_url, expires_at):
#     """
#     Create a signed cookie
#     """
#     cloudfront_cookie_generator = CloudFrontCookieGenerator()
#
#     cookies = cloudfront_cookie_generator.create_signed_cookies(
#         url=object_url,
#         private_key_file="ssl/key.pem",
#         keypair_id='abc',
#         expires_at=expires_at
#     )
#     return cookies
