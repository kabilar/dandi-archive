# Backups

## Previous implementations for DANDI

1. Download entire S3 bucket to Dartmouth server (i.e. `drogon`)
1. Backup with DataLad to create DataLad Dandisets on `drogon`

## Current implementation for DANDI

1. Backup with DataLad to create DataLad Dandisets on Dropbox
backup2datalad - annex special remote - git-annex mv (from s3 to dropbox)
    1. Current issue is Zarr - slow due to too many files
    1. Support embargo dandisets - 

## Potential implementations for LINC

- Postgres database

- S3 bucket
    1. For the production S3 bucket enable S3 Versioning and Object Lock.
    1. Copy S3 bucket to deep glacier.

dandi2datalad
git annex mv backups to dropbox

Glacier backups not implemented for DANDI

frequency of backups?
complexity of private datasets

S3 bucket versioning
back up to mit with datalad and git annex
