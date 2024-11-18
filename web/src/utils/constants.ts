const dandiUrl = 'https://dandiarchive.org';
const dandiAboutUrl = 'https://www.dandiarchive.org/';
const lincBrainUrl = "https://connects.mgh.harvard.edu/";
const lincDocumentationUrl = 'https://docs.lincbrain.org/';
const lincHelpUrl = 'https://docs.lincbrain.org/#support';
const lincHubUrl = 'https://hub.lincbrain.org/';

const lincWebKNOSSOSUrl = 'https://webknossos.lincbrain.org';

const sentryLandingPageUrl = "https://sentry.io";

const draftVersion = 'draft';

const VALIDATION_ICONS = {
  // version metadata
  // https://github.com/dandi/schema/blob/master/releases/0.4.4/dandiset.json#L231
  name: 'mdi-note',
  description: 'mdi-text',
  contributor: 'mdi-account-multiple',
  license: 'mdi-gavel',
  assetsSummary: 'mdi-file-multiple',

  // asset metadata
  // https://github.com/dandi/schema/blob/master/releases/0.4.4/asset.json#L312
  contentSize: 'mdi-table-of-contents',
  encodingFormat: 'mdi-code-json',
  digest: 'mdi-barcode',
  path: 'mdi-folder-multiple',
  identifier: 'mdi-identifier',

  // icon to use when one isn't found
  DEFAULT: 'mdi-alert',
};

const sortingOptions = [
  {
    name: 'Modified',
    djangoField: 'modified',
  },
  {
    name: 'Identifier',
    djangoField: 'id',
  },
  {
    name: 'Name',
    djangoField: 'name',
  },
  {
    name: 'Size',
    djangoField: 'size',
  },
];

const DANDISETS_PER_PAGE = 8;

export {
  dandiUrl,
  dandiAboutUrl,
  lincDocumentationUrl,
  lincHubUrl,
  draftVersion,
  lincHelpUrl,
  lincBrainUrl,
  lincWebKNOSSOSUrl,
  VALIDATION_ICONS,
  sortingOptions,
  DANDISETS_PER_PAGE,
  sentryLandingPageUrl,
};
