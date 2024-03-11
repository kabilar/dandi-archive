# Support authorization and access controls for open, embargoed, and restricted assets and Dandisets

This document outlines identity and group management controls building on the current implementation.  Many items in the document have been pull directly from [embargo-mvp](https://github.com/dandi/dandi-archive/blob/master/doc/design/embargo-mvp.md) and [embargo-full](https://github.com/dandi/dandi-archive/blob/master/doc/design/embargo-full.md).

## Current implementation

view only dandisets
view only on embargoed dandisets

## Use case 1

Dandisets are restricted to select owners for indefinite time period.

## Use case 2

Embargoed and restricted Dandisets are shared with reviewers.  

Embargoed and restricted Dandisets allow for anonymous read-only access.  Users would be able to browse the Dandiset on the web app and download with the command line interface.

## MVP User requirements

1. Implement a policy

Describe permissions to user requirements
Restricted applies to asset
role-based access control (RBAC) 
add actions from: https://github.com/dandi/dandi-archive/blob/audit-design-doc/doc/design/audit-trail-mvp.md
CRUD requirements

| User Role | Resource | Actions |
| - | - | - |
| Owner | Open Dandiset | Create Dandiset, Add Owner, Remove Owner,  Update version metadata, add asset, update asset, remove asset, unembargo Dandiset, publish Dandiset, Delete Dandiset, searchable |
| Non-owner | Open Dandiset | GET |
| Owner | Embargoed Dandiset | ? |
| Non-owner | Embargoed Dandiset | Cannot view Dandiset, Not searchable |
| Invited reviewer | Embargoed Dandiset | GET |
| Anonymous reviewer | Embargoed Dandiset | GET |
| Owner | Restricted Dandiset | ? |
| Reviewer | Restricted Dandiset | GET |
| Anonymous Reviewer | Restricted Dandiset | GET |
| Owner | Published Asset | ? |
| Reviewer | Published Asset | ? |
| Anonymous Reviewer | Published Asset | ? |

Definitions
1. Restricted asset - 
1. Restricted Dandiset - Any Dandiset that contains a restricted asset?

Resource-based access control (ReBAC) policy

| Resource | Permissions |
| - | - |
| Open Dandiset | - |
| Embargoed Dandiset | - |
| Restricted Dandiset | - |

## MVP+1 User requirements

## MVP Technical specifications

## MVP+1 Technical specifications

## Open questions

1. Restrict access of asset and/or Dandiset?
1. Which S3 bucket to store restricted assets?  Allow users to supply their bucket?
    1. Currently AWS OpenData can store restricted assets.
1. If restriction is at the asset-level, how is a Dandiset access control defined?
    1. Possible solution map UUID to Dandiset?

## Potential solutions

## Embargoed and Restricted Read-only access
- Reviewers are allowed to access asset data on private and restricted embargoed dandisets.

## Embargoed and Restricted Anonymous read-only access
1. There are two modes to support: browsing the embargoed dandiset anonymously, and downloading the asset data anonymously with the CLI.

Browsing the embargoed dandiset anonymously can be achieved with a secret URL parameter unique to the dandiset.
When the web UI detects the secret URL parameter, it passes it as an authorization token header/URL parameter to all API requests.
The API will treat any request with the correct secret as coming from a reviewer, unless the user is already an owner.

A link to the dandiset with this secret URL parameter is included somewhere on the embargoed dandiset page as a way to share access anonymously.

### TODO how to download anonymously with the CLI?

## Embargoed and Restricted Read-only access
- If a user is a reviewer on an embargoed dandiset, they do not have any permissions on other embargoed dandisets unless explicitly added to those dandisets as well.
- The web UI will show reviewer selection directly under owner selection.
- Reviewers are not acknowledged for unembargoed dandisets and will not show up in the web UI.
- This will be implemented as a new django-guardian role.
- All read endpoints for assets are permitted for users who are reviewers of the embargoed dandiset.
- All read endpoints for dandisets and versions will treat reviewers the same as owners.
- All write and upload endpoints are unchanged.

## Use case 1

1. Reviewer
2. Sensitive data

1. Defines policies
    Data use agreements?
    NIH identity system - RAS
    NeMo - NDA approval for authorization

Anonymous viewers
    View Dandiset on web app
    Download individual files on web app
    Download Dandiset or individual files with CLI or Python Client 
A link to the dandiset with this secret URL parameter is included somewhere on the embargoed dandiset page as a way to share access anonymously.
Verify, validate, quality control on embargoed datasets
Groups/organizations

1. Aspects of archive that the design touches
-------------------------------------------------------------------
# Embargo

## Non-private embargoed dandisets
- Embargoed dandisets are invisible to non-owners.
- Restricted embargoed dandisets are searchable, viewable, and their metadata is public to everyone, but their asset data and metadata is not.
- Users will select their desired embargo mode using radio buttons when creating a dandiset.
- Dandiset `embargo_status` values: `EMBARGOED`, `UNEMBARGOING`, `OPEN`,`RESTRICTED`.
- All of the dandiset and version endpoints will only hide `EMBARGOED` dandisets from appearing.
- The asset endpoints will not permitted for anonymous users on embargoed assets that are `EMBARGOED` or `RESTRICTED`.

### TODO: can users switch the embargo mode between embargoed and restricted?
It would be easy to do, since it's just a change `embargo_status`, no data needs to be copied.
We would need a place in the UI to set that

## Embargo period enforcement
NIH embargoes (and embargoes in general) will have an end date to ensure that the data is not secret forever.
We will enforce that an end date be specified for every new embargoed dandiset, and forcibly release embargoed dandisets that expire.

The MVP collects the NIH award number and stores it in the metadata.
We can use the NIH API to determine the required release date for the award (?).
### TODO should we gather the end date during creation time, as we do award number?

We should add scheduled jobs (in the manner of garbage collection) that:
* Notify admins and owners of any embargoed dandisets without end dates
* Notify admins and owners of any embargoed dandisets that are approaching their end dates (daily emails for the last week?)
* Notify admins and owners of any embargoed dandisets that have past their end dates

Admins will be at liberty to manually delete or unembargo embargoed dandisets without end dates.
Admins will be at liberty to manually unembargo embargoed dandisets that have expired.

## Zarr download
The MVP embargo zarr download design involves a request to our API server for every file being downloaded from the zarr archive.
Since zarr archives can contain hundreds of thousands of files, there would be a corresponding number of requests, which might degrade performance of the API server.
If this becomes an issue, we could:
* Spin off the zarr download functionality into a separate microservice that can be scaled separately, and would isolate any accidental DDOS effects.
  This could be as simple as adding a new django app and a new Heroku dyno, or as complex as a Lambda@Edge+CloudFront service.
* Dynamically provision IAM users with permission to access prefixes in the embargo bucket and distribute access keys to users.
  This would require the API server to manage IAM directly, which is a lot of complexity to manage.
* Make the embargo bucket publicly readable, but not listable.
  If anyone knows the full S3 object key they have the ability to download the data, but they will not have the ability to search for or scan the bucket for new content.
  We would then distribute the zarr_id to anyone who needs to access an embargoed zarr archive, giving them permanent read access to it.
  The downside is that access is not revocable, since we cannot take back the zarr ID from the user or efficiently change the location of the zarr archive.

- email the owners of an embargoed dandiset (and admins) when it has been successfully unembargoed
- on the stats page, display the full amount of data stored in the archive, and indicate how much of it is under embargo
  - e.g., `300 TB total data size (100 TB currently under embargo)`
  - link the word "embargo" to docs/explanation thereof
------------------------------------------------------------------
# Embargo Minimum Viable Product

# User experience

## Web
When creating a new dandiset, users will have checkbox to choose whether or not the dandiset should be embargoed.
If so, the user must also specify an NIH award number (https://era.nih.gov/files/Deciphering_NIH_Application.pdf).
The award number will be added as a new `Funder` on an automatically generated Contributor Organization in the metadata.

Instead of the normal `Publish` button and version browser, the DLP will instead show an `Unembargo` button.
Clicking it will open a confirmation modal informing the user that they are unembargoing, all their data will be publicized, there is no undoing, and that it can take some time for large dandisets.
Confirming will lock the dandiset for the duration of the unembargo.
Once the unembargo finishes, the dandiset will be like any other unpublished draft dandiset.

Once created, an embargoed dandiset is only visible or searchable to owners.
Instead of the `draft` chip, an `embargoed` chip should be used on the dandiset listing pages.
These dandisets+chips will only appear in the listings to owners of the embargoed dandisets.

## CLI
The CLI experience will be basically unchanged.
Uploads to an embargoed dandiset will function exactly the same from an API perspective, the data simply goes to a different location.

# Data storage
Embargoed assets will be stored in a separate S3 bucket.
This bucket is private and not browsable by the general public.

Each dandiset stored in the embargoed bucket will be prefixed with a dandiset identifier.
This will make it easier to manage embargo permissions for a specific embargoed dandiset.
The API server will use the embargo bucket to store blobs in exactly the same way it uses the public bucket, but with the embargoed dandiset prefixed.
Manifests will be stored at a different path to simplify redundant path information.

Assuming dandiset `123456` was embargoed:
* Blobs will be stored at `123456/blobs/123/456/123456...
* Manifests will be stored at `123456/manifests/...`
* Zarr files will be stored at `123456/zarr/{uuid}/...`

When unembargoing an embargoed dandiset, all asset data for that dandiset is copied to the public bucket.

When uploading a new asset to an embargoed dandiset, the server will first check if that blob has already been uploaded publicly.
If so, the public blob will be used instead of uploading the data again to the embargo bucket.

# Data download
Downloading embargoed assets is the same as downloading normal assets.
The `/assets/{asset_id}/download` will verify that the user has permission on the embargoed dandiset if the asset is embargoed, and return a presigned URL if so.

Downloading embargoed zarr archives will be done through a special API surface.
Clients will use zarr's builtin [fsspec](https://zarr.readthedocs.io/en/stable/tutorial.html#io-with-fsspec) store [HTTPFileSystem](https://filesystem-spec.readthedocs.io/en/latest/api.html#fsspec.implementations.http.HTTPFileSystem) like this:
```
zarr_archive = zarr.open('https://api.dandiarchive.org/api/zarr/{zarr_id}/files/')
```
`https://api.dandiarchive.org/api/zarr/{zarr_id}/files/{path_to_file_or_directory}` will return either a directory listing parsable by HTTPFileSystem, or a redirect to a presigned S3 URL that can be used to download the file.
Permissions will also be checked just as when doing an asset download.

A test implementation can be found [here](https://github.com/dandi/dandi-api/commit/46f637c4d29d69d34a1a78d820193402d3fc3778).


# Django changes

## Models
The `Dandiset` model will have an `embargo_status` field that is one of `EMBARGOED`, `UNEMBARGOING`, or `OPEN`.
* `OPEN` means that the Dandiset is publicly accessible and publishable.
  This is the state all Dandisets currently have.
* `EMBARGOED` means that the Dandiset is embargoed.
  It is searchable and viewable to owners.
  It is not searchable or viewable to non-owners.
  It is not publishable.
  Manifest YAML/JSON files will be written to the embargo bucket rather than the public bucket.
* `UNEMBARGOING` means that the Dandiset is currently transitioning from embargoed to public.
  All modification operations will return a 400 error while the unembargo is in progress.
  This includes metadata changes and uploads.

A new `EmbargoedAssetBlob` model will be added.
This behaves the same as a normal `AssetBlob`, but points to the embargo bucket rather than the public bucket.
It also contains a reference to the `Dandiset` it belongs to.

`Asset`s will point to exactly one `AssetBlob` or `EmbargoedAssetBlob` or `EmbargoedZarrArchive` or `ZarrArchive`.
An `Asset` will be considered "embargoed" if it has an `EmbargoedAssetBlob` or `EmbargoedZarrArchive`.
An embargoed `Asset` can only belong to the dandiset named in the `EmbargoedAssetBlob`.
The automatically populated `Asset` metadata will also set the `access` field to the appropriate value depending on whether or not the asset is embargoed.

A new `EmbargoedUpload` model will be added.
This is just like the normal `Upload` model, but the uploaded data will be sent to the embargoed bucket instead of the public bucket, and the `Upload` will create an `EmbargoedAssetBlob` when finalized.
It will also contain a reference to the `Dandiset` it belongs.

A new `EmbargoedZarrArchive` model will be added in the same vein as `EmbargoedAssetBlob`.
A new `EmbargoedZarrUploadFile` model will also be added to track zarr uploads to an embargoed dandiset.

There will be a new admin dashboard page showing embargoed dandisets and their award numbers to make it easier to monitor embargoed dandisets.
For now, we specifically want to police users creating embargoed dandisets with invalid awards, although we may eventually care about award end dates as well.

## API
* Create dandiset endpoint

  Add an `embargo` URL parameter to the endpoint which is normally absent.
  If `embargo` is present (` POST .../dandisets/?embargo`), the `access` metadata field will be set to `EmbargoedAccess`.
  The `embargo_status` of the dandiset will also be set to `EMBARGOED`.
  The expectation is that the web UI will have requested an award number from the user and recorded it as a `Funder` on a new Contributor Organization in the metadata.

* Get/List dandiset endpoint

  The DandisetViewSet queryset will filter out dandisets with `embargo_status == EMBARGOED` that are also not owned by the current user.
  This will prevent them from showing up in the listing or fetching endpoints.

  The `DandisetSerializer` will also be updated to include the `embargo_status` field so that the web client can render the embargoed dandiset appropriately.

* publish version endpoint

  Return error 400 if `dandiset.embargo_status != OPEN`.

* create asset, update metadata, and any other dandiset/version modification endpoints:

  Return error 400 if `dandiset.embargo_status == UNEMBARGOING`.

* New endpoint: `POST /api/dandisets/{dandiset_id}/unembargo`

  Unembargo an embargoed dandiset.

  Only permitted for owners and admins. If the `embargo_status` is `OPEN` or `UNEMBARGOING`, return 400.

  Set the `embargo_status` to `UNEMBARGOING`, then dispatch the unembargo task.

* Unembargo task

  For every `Asset` with an `EmbargoedAssetBlob` in the dandiset, convert the `EmbargoedAssetBlob` into an `AssetBlob` by moving the data from the embargo bucket to the public bucket.
  These could be >5GB, so the [multipart copy API](https://docs.aws.amazon.com/AmazonS3/latest/userguide/CopyingObjectsMPUapi.html) must be used.
  The ETag and checksum must remain undisturbed; the only change should be where the data is stored.
  Verify that the resulting unembargoed assets match one-for-one (in the database) with the embargoed assets that were copied.
  Once finished, the `access` metadata field on the dandiset will be updated to `OpenAccess` and `embargo_status` is set to `OPEN`.

  Before copying data, check if an existing `AssetBlob` with the same checksum has been uploaded already (this would have happened after uploading the embargoed data).
  If so, use it instead of copying the `EmbargoedAssetBlob` data.

* Get/List asset endpoint

  The NestedAssetViewSet queryset will filter out assets with `embargoed_asset_blob.dandiset.embargo_status != OPEN` that are also not owned by the current user.
  This will prevent them from showing up in the listing or fetching endpoints.

* upload_initialize_view

  An optional field `embargoed_dandiset` will be available on the serializer.
  If specified, it will be passed to the `Upload` object.
  This will mean the final upload will result in an `EmbargoedAssetBlob`.

  Even if `embargoed_dandiset` is specified, if an `AssetBlob` with a matching checksum already exists, return it instead of uploading embargoed data.
  This means that an embargoed dandiset can contain both embargoed and unembargoed assets.

  `EmbargoedAssetBlob`s should also be checked for deduplication, but only within an embargoed dandiset.
  This is to keep the permission model clean for owners of different embargoed dandisets that might contain the same asset.
  An embargoed dandiset should use the same `EmbargoedAssetBlob` if the same file appears in multiple places, but two embargoed dandisets should upload the same data twice if they both contain the same file.

  Return error 400 if `dandiset.embargo_status == UNEMBARGOING`.

* Zarr archive creation endpoint

  Add `embargo` and `dandiset` URL parameters to the endpoint which are normally absent.
  If `embargo` is present, an `EmbargoedZarrArchive` will be created instead of a `ZarrArchive`.
  If `embargo` is present, `dandiset` must also be present so that the `EmbargoedZarrArchive` knows which embargoed dandiset it belongs to.
  If `embargo` is absent and `dandiset` is present, it is ignored.

* Zarr download endpoints

  These endpoints will also be available for normal zarr archives.
  It is expected that normal zarr archives will use the s3 store, which will be more performant.
  When used on embargoed zarr archives, the user must have read access on the dandiset.

  * `https://api.dandiarchive.org/api/zarr/{zarr_id}/files/{path_to_directory}/` (note the trailing slash)

    Returns a JSON list of URLs describing the contents of the directory.
    This will read the `.checksum` file in S3 to determine the contents of the directory.
    If absent, return a 404.

    This endpoint must be parsable by [HTTPFileSystem](https://filesystem-spec.readthedocs.io/en/latest/api.html#fsspec.implementations.http.HTTPFileSystem) with `simple_links=True`.

  * `https://api.dandiarchive.org/api/zarr/{zarr_id}/files/{path_to_file}` (note the absence of trailing slash)

    Returns a 302 to a presigned S3 URL for the given file in the zarr archive.
    This will *not* check if the file is present in S3.
    Instead, S3 will simply return a 404 if the path is incorrect.

    [HTTPFileSystem](https://filesystem-spec.readthedocs.io/en/latest/api.html#fsspec.implementations.http.HTTPFileSystem) follows redirects by default, so no extra configuration is required.

* stats_view

  The total size value should include the size of `EmbargoedAssetBlob`s as well as `AssetBlob`s.
