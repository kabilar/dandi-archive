from __future__ import annotations

import json
from json.decoder import JSONDecodeError
import os
from typing import TYPE_CHECKING

import requests

from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.http.response import Http404, HttpResponseBase, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from drf_yasg.utils import swagger_auto_schema
from oauth2_provider.views.base import AuthorizationView
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets

from dandiapi.api.mail import (
    send_approved_user_message,
    send_new_user_message_email,
    send_registered_notice_email,
)
from dandiapi.api.permissions import IsApproved
from dandiapi.api.views.serializers import UserDetailSerializer
from dandiapi.api.views.users import social_account_to_dict, user_to_dict
from dandiapi.api.models.user import UserMetadata

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse
    from rest_framework.request import Request


@swagger_auto_schema(
    methods=['GET', 'POST'],
    responses={200: 'The user token'},
)
@api_view(['GET', 'POST'])
@permission_classes([IsApproved])
def auth_token_view(request: Request) -> HttpResponseBase:
    if request.method == 'GET':
        token = get_object_or_404(Token, user=request.user)
    elif request.method == 'POST':
        Token.objects.filter(user=request.user).delete()
        token = Token.objects.create(user=request.user)
    return Response(token.key)


def extract_cookie_from_set_cookie(set_cookie_header):
    """
    Extracts the name=value pair from a Set-Cookie header string.

    :param set_cookie_header: The Set-Cookie header string.
    :return: A dictionary with the cookie name and value.
    """
    # Split the Set-Cookie header string to get the name=value part
    name_value = set_cookie_header.split(';')[0]  # Take only the first part, which is name=value

    # Split into name and value
    name, value = name_value.split('=', 1)

    # Return as a dictionary
    return {name: value}


class ExternalAPIViewset(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        methods=['GET'],
        responses={200: 'Login worked for given external API service'},
    )
    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsApproved],
        url_path=r'login/(?P<service>[^/.]+)'
    )
    def login(self, request: Request, service: str) -> HttpResponseBase:
        if request.user.socialaccount_set.count() == 1:
            social_account = request.user.socialaccount_set.get()
            user_dict = social_account_to_dict(social_account)
        else:
            user_dict = user_to_dict(request.user)

        user_detail_serializer = UserDetailSerializer(user_dict)

        if service == 'webknossos':
            user = User.objects.get(email=user_detail_serializer.data["email"])
            webknossos_credential = user.metadata.webknossos_credential
            webknossos_api_url = os.getenv('WEBKNOSSOS_API_URL', "webknossos-r5.lincbrain.org")
            external_endpoint = f'https://{webknossos_api_url}/api/auth/login'

            payload = {
                "email": user.email,
                "password": webknossos_credential
            }

            headers = {'Content-Type': 'application/json',}
            response = requests.post(external_endpoint, json=payload, headers=headers, timeout=10)
            django_response = JsonResponse({
                'status': 'Login request sent to external API'
            })
            if 'Set-Cookie' in response.headers:
                django_response['Set-Cookie'] = response.headers['Set-Cookie']
            return django_response

        else:
            return Response(status=400, data={"detail": "Unsupported service"})

    @swagger_auto_schema(
        methods=['GET'],
        responses={200: 'Login worked for given external API service'},
    )
    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsApproved],
        url_path=r'refresh_external_data/(?P<service>[^/.]+)'
    )
    def refresh_external_data(self, request: Request, service: str) -> None:
        if request.user.socialaccount_set.count() == 1:
            social_account = request.user.socialaccount_set.get()
            user_dict = social_account_to_dict(social_account)
        else:
            user_dict = user_to_dict(request.user)

        user_detail_serializer = UserDetailSerializer(user_dict)

        if service == 'webknossos':
            user = User.objects.get(email=user_detail_serializer.data["email"])
            webknossos_credential = user.metadata.webknossos_credential
            webknossos_api_url = os.getenv('WEBKNOSSOS_API_URL', "webknossos-r5.lincbrain.org")
            external_endpoint = f'https://{webknossos_api_url}/api/auth/login'

            payload = {
                "email": "akanzer@mit.edu",
                "password": "LINC2024!"
            }

            headers = {'Content-Type': 'application/json'}
            response = requests.post(external_endpoint, json=payload, headers=headers, timeout=10)

            print(response.headers)
            set_cookie_value = response.headers.get('Set-Cookie')
            cookies = extract_cookie_from_set_cookie(set_cookie_value)

            webknossos_datasets_url = f'{webknossos_api_url}/api/datasets'

            webknossos_datasets = requests.get(webknossos_datasets_url, cookies=cookies)

            for webknossos_dataset in webknossos_datasets.json():
                a = requests.get(f'http://webknossos-r5.lincbrain.org:8080/binaryData/LINC/{webknossos_dataset["name"]}/datasource-properties.json').json()
                for layers in a['dataLayers']:
                    for mag in layers['mags']:
                        print(mag['path'].rsplit('/', 1)[0])


            # print(datasets.json())
            #
            # for webknossos_dataset in datasets.json():
            #     dataset_name = webknossos_dataset['name']

        else:
            return Response(status=400, data={"detail": "Unsupported service"})





QUESTIONS = [
    {'question': 'First Name', 'max_length': 100},
    {'question': 'Last Name', 'max_length': 100},
    {'question': 'What do you plan to use LINC Data Platform for?', 'max_length': 1000},
    {'question': 'Please list any affiliations you have.', 'max_length': 1000},
]

# questions for new users
NEW_USER_QUESTIONS = QUESTIONS

# questions for existing users who have no first/last name
COLLECT_USER_NAME_QUESTIONS = QUESTIONS[:2]


@require_http_methods(['GET'])
def authorize_view(request: HttpRequest) -> HttpResponse:
    """Override authorization endpoint to handle user questionnaire."""
    user: User = request.user
    if (
        user.is_authenticated
        and not user.is_superuser
        and user.metadata.status == UserMetadata.Status.INCOMPLETE
    ):
        # send user to questionnaire if they haven't filled it out yet
        return HttpResponseRedirect(
            f'{reverse("user-questionnaire")}'
            f'?{request.META["QUERY_STRING"]}&QUESTIONS={json.dumps(NEW_USER_QUESTIONS)}'
        )
    elif not user.is_anonymous and (not user.first_name or not user.last_name):  # noqa: RET505
        # if this user doesn't have a first/last name available, redirect them to a
        # form to provide those before they can log in.
        return HttpResponseRedirect(
            f'{reverse("user-questionnaire")}'
            f'?{request.META["QUERY_STRING"]}&QUESTIONS={json.dumps(COLLECT_USER_NAME_QUESTIONS)}'
        )

    # otherwise, continue with normal authorization workflow
    return AuthorizationView.as_view()(request)


@swagger_auto_schema()
@api_view(['GET', 'POST'])
@require_http_methods(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def user_questionnaire_form_view(request: HttpRequest) -> HttpResponse:
    user: User = request.user
    if request.method == 'POST':
        user_metadata: UserMetadata = user.metadata
        questionnaire_already_filled_out = user_metadata.questionnaire_form is not None
        # we can't use Django forms here because we're using a JSONField, so we have
        # to extract the request data manually
        req_body = request.POST.dict()
        user_metadata.questionnaire_form = {
            question['question']: req_body.get(question['question'])[: question['max_length']]
            if req_body.get(question['question']) is not None
            else None
            for question in QUESTIONS
        }
        user_metadata.save(update_fields=['questionnaire_form'])

        # Save first and last name if applicable
        if req_body.get('First Name'):
            user.first_name = req_body['First Name']
            user.save(update_fields=['first_name'])
        if req_body.get('Last Name'):
            user.last_name = req_body['Last Name']
            user.save(update_fields=['last_name'])

        #         Only send emails when the user fills out the questionnaire for the first time.
        #         If they go back later and update it for whatever reason, they should not receive
        #         another email confirming their registration. Additionally, users who have already
        #         been approved that go back and
        #         update the form later should also not receive an email.
        if (
            not questionnaire_already_filled_out
            and user_metadata.status == UserMetadata.Status.INCOMPLETE
        ):
            # Specific to DANDI Archive
            # is_edu_email: bool = user.email.endswith('.edu')

            # Require manual approval
            user.metadata.status = UserMetadata.Status.PENDING
            # Specific to DANDI Archive
            # user_metadata.status = (
            #     UserMetadata.Status.APPROVED if is_edu_email else UserMetadata.Status.PENDING
            # )
            user_metadata.save(update_fields=['status'])

            # send email indicating the user has signed up
            for socialaccount in user.socialaccount_set.all():
                # Send approved email if they have been auto-approved
                if user_metadata.status == UserMetadata.Status.APPROVED:
                    send_approved_user_message(user, socialaccount)
                # otherwise, send "awaiting approval" email
                else:
                    send_registered_notice_email(user, socialaccount)
                    send_new_user_message_email(user, socialaccount)

        # pass on OAuth query string params to auth endpoint
        return HttpResponseRedirect(
            f'{reverse("authorize").rstrip("/")}/?{request.META["QUERY_STRING"]}'
        )

    try:
        # questions to display in the form
        questions = json.loads(request.GET.get('QUESTIONS'))
    except (JSONDecodeError, TypeError) as e:
        raise Http404 from e

    return render(
        request,
        'api/account/questionnaire_form.html',
        {
            'questions': questions,
            'query_params': request.GET.dict(),
            'dandi_web_app_url': settings.DANDI_WEB_APP_URL,
        },
    )
