# Permissions for S3 Assets in LINC Archive

Collaborators: Aaron Kanzer, Kabilar Gunalan

## Requirements

• As a CONNECTS developer, I shall be able to view multiple datasets/layers (e.g. dMRI, tractography, HiP-CT) in the same neuroglancer
• As a CONNECTS developer, I shall be able to view data locally or on neuroglancer
• As a CONNECTS developer, I shall be able to have direct access to S3 asset URI
• As a LINC Archive user, I shall be able to render neuroglancer layers view similar to DANDI

#### Relevant Links

https://github.com/orgs/lincbrain/projects/2?pane=issue&itemId=54650571

https://github.com/neuroscales/ngtools/blob/main/notebooks/show_tract.ipynb

https://github.com/google/neuroglancer/issues/507

## Implementation Options

#### Issue read-only credentials for S3 bucket. Quick set up.

Does not resolve rendering issue. Would resolve accessing the asset in Jupyter Notebook, but would require flaky Python code.

#### Integrate read-only credentials for S3 bucket into LINC Archive, LINC CLI

###### CloudFront distribution with Origin Access Identity control for relevant S3 buckets

- S3 Asset Bucket is served via a CloudFront distribution
- User hits a get_presigned_cookie/ API endpoint in LINC Archive. In the endpoint response is a valid cookie that allows the user's browser to be able to access the asset via their browser

Rendering via Neuroglancer

- (Might need to modify fork of neuroglancer to handle CloudFront asset path in same format that it handles S3 asset path)

Accessing via LINC Archive API

- Cookies would get passed in request to get asset
- Provide LINC CLI option for retrieving asset. Instead of just referencing the asset directly, we would need to provide a helper function that wraps the request with the cookie

#### AWS Cognito, npm AWS SDK package

TBD

#### Provide endpoint to provide pre-signed S3 Asset URLs

Blocker: Pre-signed URLs can only be generated at the object-level, not at the sub-directory level. Neuroglancer renders many
objects at once as a user zooms, scrolls, etc., thus unless we generated a pre-signed URL for each asset, this would be difficult.

#### Netlify OAuth requirement to render site

Solves rendering issue, but does not solve accessing private S3 assets

