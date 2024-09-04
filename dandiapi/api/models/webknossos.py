from __future__ import annotations
import os

from uuid import uuid4

from django.db import models

from .asset import Asset

WEBKNOSSOS_BINARY_DATA_FOLDER = "binaryData"
WEBKNOSSOS_BINARY_DATA_PORT = "8080"
WEBKNOSSOS_DATASOURCE_PROPERTIES_FILE_NAME = "datasource-properties.json"

class WebKnossosDataset(models.Model):  # noqa: DJ008
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    webknossos_dataset_name = models.CharField(max_length=100, null=True, blank=True)
    webknossos_organization_name = models.CharField(max_length=100, null=True, blank=True)

    def get_datasource_properties_url(self) -> str:
        webknossos_api_url = os.getenv('WEBKNOSSOS_API_URL', "webknossos-r5.lincbrain.org")

        if webknossos_api_url:
            return (f'http://{webknossos_api_url}:{WEBKNOSSOS_BINARY_DATA_PORT}/'
                    f'{WEBKNOSSOS_BINARY_DATA_FOLDER}/{self.webknossos_organization_name}/'
                    f'{self.webknossos_dataset_name}/{WEBKNOSSOS_DATASOURCE_PROPERTIES_FILE_NAME}')
        raise Exception("WEBKNOSSOS_API_URL is not set")

    def get_asset_s3_uri(self) -> str:
        return self.asset.s3_uri

    def get_webknossos_url(self) -> str:
        webknossos_api_url = os.getenv('WEBKNOSSOS_API_URL', "webknossos-r5.lincbrain.org")

        if webknossos_api_url:
            return (f'https://{webknossos_api_url}/datasets/{self.webknossos_organization_name}/{self.webknossos_dataset_name}')
        raise Exception("WEBKNOSSOS_API_URL is not set")


class WebKnossosDataLayer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    webknossos_dataset = models.ForeignKey(WebKnossosDataset, related_name='webknossos_datalayers', on_delete=models.PROTECT)
    asset = models.ForeignKey(Asset, related_name='webknossos_datasets', on_delete=models.PROTECT)

    def get_webknossos_url(self) -> str:
        webknossos_api_url = os.getenv('WEBKNOSSOS_API_URL', "webknossos-r5.lincbrain.org")

        if webknossos_api_url:
            return (f'https://webknossos-r5.lincbrain.org/datasets/LINC'
                    f'/{self.webknossos_dataset.webknossos_dataset_name}')
        # raise Exception("WEBKNOSSOS_API_URL is not set")

class WebKnossosAnnotation(models.Model):  # noqa: DJ008
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    webknossos_annotation_name = models.CharField(max_length=100, null=True, blank=True)
    webknossos_organization = models.CharField(max_length=100, null=True, blank=True)
    webknossos_annotation_owner_first_name = models.CharField(max_length=100, null=True, blank=True)
    webknossos_annotation_owner_last_name = models.CharField(max_length=100, null=True, blank=True)

    # ForeignKeys
    asset = models.ForeignKey(Asset, related_name='webknossos_annotations', on_delete=models.PROTECT)
    webknossos_dataset = models.ForeignKey(WebKnossosDataset, related_name='webknossos_annotations', on_delete=models.PROTECT)

    def get_asset_s3_uri(self) -> str:
        return self.asset.s3_uri

    def get_full_name(self) -> str:
        return (f'{self.webknossos_annotation_owner_first_name}'
                f' {self.webknossos_annotation_owner_last_name}')
