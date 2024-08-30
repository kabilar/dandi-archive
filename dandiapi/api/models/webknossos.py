from __future__ import annotations
import os

from uuid import uuid4

from django.db import models

from .asset import Asset

WEBKNOSSOS_BINARY_DATA_FOLDER = "binaryData"
WEBKNOSSOS_BINARY_DATA_PORT = "8080"
WEBKNOSSOS_DATASOURCE_PROPERTIES_FILE_NAME = "datasource-properties.json"

class WebKnossosDataset(models.Model):  # noqa: DJ008
    webknossos_dataset_id = models.UUIDField(unique=True, default=uuid4, db_index=True)
    webknossos_dataset_name = models.CharField(max_length=100)
    webknossos_organization_name = models.CharField(max_length=100)

    # ForeignKeys
    asset = models.ForeignKey(Asset, related_name='webknossos_datasets', on_delete=models.CASCADE)

    def get_datasource_properties_url(self) -> str:
        webknossos_api_url = os.getenv('WEBKNOSSOS_API_URL', None)

        if webknossos_api_url:
            return (f'http://{webknossos_api_url}:{WEBKNOSSOS_BINARY_DATA_PORT}/'
                    f'{WEBKNOSSOS_BINARY_DATA_FOLDER}/{self.webknossos_organization_name}/'
                    f'{self.webknossos_dataset_name}/{WEBKNOSSOS_DATASOURCE_PROPERTIES_FILE_NAME}')
        raise Exception("WEBKNOSSOS_API_URL is not set")

    def get_asset_s3_uri(self) -> str:
        return self.asset.s3_uri



class WebKnossosAnnotation(models.Model):  # noqa: DJ008
    webknossos_annotation_id = models.UUIDField(unique=True, default=uuid4, db_index=True)
    webknossos_annotation_name = models.CharField(max_length=100)
    webknossos_organization = models.CharField(max_length=100)

    # ForeignKeys
    asset = models.ForeignKey(Asset, related_name='webknossos_annotations', on_delete=models.CASCADE)
    webknossos_dataset = models.ForeignKey(WebKnossosDataset, related_name='webknossos_annotations', on_delete=models.PROTECT)

    def get_asset_s3_uri(self) -> str:
        return self.asset.s3_uri
