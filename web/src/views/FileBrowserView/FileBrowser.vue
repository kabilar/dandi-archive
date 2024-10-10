<template>
  <div v-if="!unembargo_in_progress">
    <v-progress-linear
      v-if="!currentDandiset"
      indeterminate
    />
    <v-container v-else>
      <v-dialog
        v-if="!!itemToDelete"
        v-model="itemToDelete"
        persistent
        max-width="60vh"
      >
        <v-card>
          <v-card-title class="text-h5">
            Really delete this asset?
          </v-card-title>

          <v-card-text>
            Are you sure you want to delete asset <span
              class="font-italic"
            >{{ itemToDelete.path }}</span>?
            <strong>This action cannot be undone.</strong>
          </v-card-text>

          <v-card-actions>
            <v-spacer />
            <v-btn
              @click="itemToDelete = null"
            >
              Cancel
            </v-btn>
            <v-btn
              v-if="itemToDelete"
              color="error"
              @click="deleteAsset"
            >
              Yes
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-row>
        <v-col :cols="12">
          <v-card>
            <v-card-title>
              <v-btn
                icon
                exact
                :to="{
                  name: 'dandisetLanding',
                  params: { identifier, version },
                }"
              >
                <v-icon>mdi-home</v-icon>
              </v-btn>
              <v-divider
                vertical
                class="ml-2 mr-3"
              />
              <router-link
                :to="{ name: 'fileBrowser', query: { location: rootDirectory } }"
                exact
                style="text-decoration: none;"
                class="mx-2"
              >
                {{ identifier }}
              </router-link>

              <template v-for="(part, i) in splitLocation">
                <template v-if="part">
                  /
                  <router-link
                    :key="part"
                    :to="{ name: 'fileBrowser', query: { location: locationSlice(i) } }"
                    exact
                    style="text-decoration: none;"
                    class="mx-2"
                  >
                    {{ part }}
                  </router-link>
                </template>
              </template>
              <span class="ml-auto">
                <b>Size</b>
              </span>
            </v-card-title>
            <v-progress-linear
              v-if="updating"
              indeterminate
            />

            <v-divider v-else />

            <FileUploadInstructions v-if="currentDandiset.asset_count === 0" />
            <v-banner v-else-if="itemsNotFound">
              No items found at the specified path.
            </v-banner>
            <v-list v-else>
              <!-- Extra item to navigate up the tree -->
              <v-list-item
                v-if="location !== rootDirectory"
                @click="navigateToParent"
              >
                <v-icon
                  class="mr-2"
                  color="primary"
                >
                  mdi-folder
                </v-icon>
                ..
              </v-list-item>

              <v-list-item
                v-for="item in items"
                :key="item.path"
                color="primary"
                @click.self="openItem(item)"
              >
                <v-icon
                  class="mr-2"
                  color="primary"
                >
                  <template v-if="item.asset === null">
                    mdi-folder
                  </template>
                  <template v-else>
                    mdi-file
                  </template>
                </v-icon>
                {{ item.name }}
                <v-spacer />

                <v-list-item-action>
                  <v-btn
                    v-if="showDelete(item)"
                    icon
                    @click="setItemToDelete(item)"
                  >
                    <v-icon color="error">
                      mdi-delete
                    </v-icon>
                  </v-btn>
                </v-list-item-action>

                <v-list-item-action v-if="item.asset">
                  <v-tooltip top>
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn
                        icon
                        :href="inlineURI(item.asset.asset_id)"
                        v-bind="attrs"
                        v-on="on"
                      >
                        <v-icon color="primary">
                          mdi-open-in-app
                        </v-icon>
                      </v-btn>
                    </template>
                    <span>Open asset in browser (you can also click on the item itself)</span>
                  </v-tooltip>
                </v-list-item-action>
                <v-list-item-action v-if="item.asset">
                  <v-tooltip top>
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn
                        icon
                        :href="downloadURI(item.asset.asset_id)"
                        v-bind="attrs"
                        v-on="on"
                      >
                        <v-icon color="primary">
                          mdi-download
                        </v-icon>
                      </v-btn>
                    </template>
                    <span>Download asset</span>
                  </v-tooltip>
                </v-list-item-action>

                <v-list-item-action v-if="item.asset">
                  <v-tooltip top>
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn
                        icon
                        :href="assetMetadataURI(item.asset.asset_id)"
                        target="_blank"
                        rel="noreferrer"
                        v-bind="attrs"
                        v-on="on"
                      >
                        <v-icon color="primary">
                          mdi-information
                        </v-icon>
                      </v-btn>
                    </template>
                    <span>View asset metadata</span>
                  </v-tooltip>
                </v-list-item-action>

                <v-list-item-action v-if="item.asset">
                  <v-menu
                    v-model="menuOpen[item.asset.asset_id]"
                    bottom
                    left
                    close-on-content-click="false"
                  >
                   <template #activator="{ on, attrs }">
                      <v-btn
                        v-if="item.asset.s3_uri"
                        color="primary"
                        icon
                        title="Links"
                        v-bind="attrs"
                        v-on="on"
                      >
                        <v-icon>mdi-content-copy</v-icon>
                      </v-btn>
                      <v-btn
                        v-else
                        color="primary"
                        disabled
                        icon
                      >
                        <v-icon>mdi-content-copy</v-icon>
                      </v-btn>
                    </template>
                    <v-list
                      dense
                    >
                      <v-subheader
                        class="font-weight-medium"
                      >
                        LINKS
                      </v-subheader>
                      <v-list-item
                        target="_blank"
                        rel="noreferrer"
                      >
                        <v-list-item-title class="font-weight-light">
                          AWS S3 URI <span v-if="copied" style="color: green; padding-left: 8px; padding-right: 8px; margin-left: 16px;">Copied!</span>
                        </v-list-item-title>
                        <v-spacer></v-spacer>
                        <v-icon @click.stop="copyToClipboard(item.asset?.s3_uri)">mdi-content-copy</v-icon>
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </v-list-item-action>
                <v-list-item-action v-if="item.asset">
                  <v-menu
                    bottom
                    left
                  >
                    <template #activator="{ on, attrs }">
                      <v-btn
                        color="primary"
                        x-small
                        :disabled="!item.services || !item.services.length"
                        v-bind="attrs"
                        v-on="on"
                      >
                        Open With <v-icon small>mdi-menu-down</v-icon>
                      </v-btn>
                    </template>
                    <v-list
                      v-if="item && item.services"
                      dense
                    >
                      <v-subheader
                        v-if="item.services.length"
                        class="font-weight-medium"
                      >
                        EXTERNAL SERVICES
                      </v-subheader>
                      <v-list-item
                        v-for="el in item.services"
                        :key="el.name"
                        @click="el.isNeuroglancer ? redirectToNeuroglancerUrl(item) : null"
                        :href="!el.isNeuroglancer ? el.url : null"
                        target="_blank"
                        rel="noreferrer"
                      >
                        <v-list-item-title class="font-weight-light">
                          {{ el.name }}
                        </v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </v-list-item-action>

                <v-list-item-action
                  v-if="item.asset"
                  class="px-2"
                >
                  <v-menu
                    bottom
                    left
                  >
                    <template #activator="{ on, attrs }">
                      <v-btn
                        color="success"
                        x-small
                        :disabled="!item.asset.webknossos_info || !item.asset.webknossos_info?.length"
                        v-bind="attrs"
                        v-on="on"
                      >
                        WebKNOSSOS <v-icon small>mdi-menu-down</v-icon>
                      </v-btn>
                    </template>
                    <v-list
                      v-if="item && item.asset.webknossos_info"
                      dense
                    >
                      <v-subheader
                        v-if="item.asset.webknossos_info"
                        class="font-weight-medium"
                      >
                        WEBKNOSSOS DATASETS CONTAINING ASSET
                      </v-subheader>
                      <v-list-item
                        v-for="el in item.asset.webknossos_info"
                        :key="item.asset.s3_uri"
                        @click.stop.prevent="el ? handleWebKnossosClick(el.webknossos_url) : null"
                        :href="el.webknossos_url ? el.webknossos_url : null"
                        target="_blank"
                        rel="noreferrer"
                      >
                        <v-list-item-title class="font-weight-light">
                          {{ el.webknossos_name ? el.webknossos_name : "No datasets associated" }}
                        </v-list-item-title>
                      </v-list-item>
                    </v-list>
                    <v-list v-if="item && item.asset.webknossos_info" dense>
                    <v-subheader
                      v-if="item.asset.webknossos_info.some(dataset => dataset.webknossos_annotations && dataset.webknossos_annotations.length > 0)"
                      class="font-weight-medium"
                    >
                      WEBKNOSSOS ANNOTATIONS CONTAINING ASSET
                    </v-subheader>

                    <!-- Check if the list has no datasets or annotations -->
                    <v-subheader
                      v-else
                      class="font-weight-medium"
                    >
                      No annotations associated
                    </v-subheader>

                    <!-- Iterate over each dataset -->
                    <v-list-item-group
                      v-for="dataset in item.asset.webknossos_info"
                      :key="dataset.webknossos_name"
                      class="mb-3"
                    >
                      <v-list dense v-if="dataset.webknossos_annotations && dataset.webknossos_annotations.length > 0">
                        <v-list-item
                          v-for="annotation in dataset.webknossos_annotations"
                          :key="annotation.webknossos_annotation_url"
                          @click="annotation ? handleWebKnossosClick(annotation.webknossos_annotation_url) : null"
                          :href="annotation.webknossos_annotation_url ? annotation.webknossos_annotation_url : null"
                          target="_blank"
                          rel="noreferrer"
                        >
                          <v-list-item-title class="font-weight-light">
                            {{ annotation.webknossos_annotation_name.trim() !== '' ? (annotation.webknossos_annotation_name + (annotation.webknossos_annotation_author ? ' by ' + annotation.webknossos_annotation_author : '')) : 'annotation untitled by ' + annotation.webknossos_annotation_author }}
                          </v-list-item-title>
                        </v-list-item>
                      </v-list>
                    </v-list-item-group>

                  </v-list>
                  </v-menu>
                </v-list-item-action>

                <v-list-item-action
                  v-if="item.aggregate_size"
                  class="justify-end"
                  :style="{width: '4.5em'}"
                >
                  {{ fileSize(item) }}
                </v-list-item-action>
              </v-list-item>
            </v-list>
          </v-card>
        </v-col>
      </v-row>
      <FileBrowserPagination
        v-if="currentDandiset.asset_count"
        :page="page"
        :page-count="pages"
        @changePage="changePage($event)"
      />
    </v-container>
  </div>
</template>

<script setup lang="ts">
import type { Ref } from 'vue';
import {
  computed, onMounted, ref, watch,
} from 'vue';
import type { RawLocation } from 'vue-router';
import { useRouter, useRoute } from 'vue-router/composables';
import filesize from 'filesize';
import { trimEnd } from 'lodash';
import axios from 'axios';

import { dandiRest, user } from '@/rest';
import { useDandisetStore } from '@/stores/dandiset';
import type { AssetFile, AssetPath } from '@/types';
import FileBrowserPagination from '@/components/FileBrowser/FileBrowserPagination.vue';
import FileUploadInstructions from '@/components/FileBrowser/FileUploadInstructions.vue';

const rootDirectory = '';
const FILES_PER_PAGE = 15;

// AssetService is slightly different from Service
interface AssetService {
  name: string,
  url: string,
  isNeuroglancer?: boolean
}

interface ExtendedAssetPath extends AssetPath {
  services?: AssetService[];
  name: string;
  s3_uri?: string;
}

const sortByFolderThenName = (a: ExtendedAssetPath, b: ExtendedAssetPath) => {
  // Sort folders first
  if (a.asset === null && b.asset !== null) {
    return -1;
  }
  if (b.asset === null && a.asset !== null) {
    return 1;
  }

  // Items are either both files or both folders
  // Sort by name
  if (a.path < b.path) {
    return -1;
  }
  if (a.path > b.path) {
    return 1;
  }

  return 0;
};

const EXTERNAL_SERVICES = [
  // {
  //   name: 'Bioimagesuite/Viewer',
  //   regex: /\.nii(\.gz)?$/,
  //   maxsize: 1e9,
  //   endpoint: 'https://bioimagesuiteweb.github.io/unstableapp/viewer.html?image=$asset_url$',
  // },
  //
  // {
  //   name: 'MetaCell/NWBExplorer',
  //   regex: /\.nwb$/,
  //   maxsize: 1e9,
  //   endpoint: 'http://nwbexplorer.opensourcebrain.org/nwbfile=$asset_url$',
  // },
  //
  // {
  //   name: 'VTK/ITK Viewer',
  //   regex: /\.ome\.zarr$/,
  //   maxsize: Infinity,
  //   endpoint: 'https://kitware.github.io/itk-vtk-viewer/app/?gradientOpacity=0.3&image=$asset_url$',
  // },
  //
  // {
  //   name: 'OME Zarr validator',
  //   regex: /\.ome\.zarr$/,
  //   maxsize: Infinity,
  //   endpoint: 'https://ome.github.io/ome-ngff-validator/?source=$asset_url$',
  // },
  // {
  //   name: 'Neurosift',
  //   regex: /\.nwb$/,
  //   maxsize: Infinity,
  //   endpoint: 'https://flatironinstitute.github.io/neurosift?p=/nwb&url=$asset_dandi_url$&dandisetId=$dandiset_id$&dandisetVersion=$dandiset_version$', // eslint-disable-line max-len
  // },
  {
    name: 'Neuroglancer',
    regex: /\.(nwb|txt|nii(\.gz)?|ome\.zarr)$/,  // TODO: .txt for testing purposes
    maxsize: Infinity,
    endpoint: 'value-defaults-to-endpoint-logic'
  }
];
type Service = typeof EXTERNAL_SERVICES[0];

const props = defineProps({
  identifier: {
    type: String,
    required: true,
  },
  version: {
    type: String,
    required: true,
  },
});

const route = useRoute();
const router = useRouter();
const store = useDandisetStore();

const location = ref(rootDirectory);
const items: Ref<ExtendedAssetPath[] | null> = ref(null);

// Value is the asset id of the item to delete
const itemToDelete: Ref<AssetPath | null> = ref(null);

const page = ref(1);
const pages = ref(0);
const updating = ref(false);
const copied = ref(false);

const menuOpen = ref<Record<string, boolean>>({});
// Computed
const owners = computed(() => store.owners?.map((u) => u.username) || null);
const currentDandiset = computed(() => store.dandiset);
const embargoed = computed(() => currentDandiset.value?.dandiset.embargo_status === 'EMBARGOED');
const unembargo_in_progress = computed(() => currentDandiset.value?.dandiset.embargo_status === 'UNEMBARGOING')
const splitLocation = computed(() => location.value.split('/'));
const isAdmin = computed(() => user.value?.admin || false);
const isOwner = computed(() => !!(
  user.value && owners.value?.includes(user.value?.username)
));
const itemsNotFound = computed(() => items.value && !items.value.length);

console.log(items)

function serviceURL(endpoint: string, data: {
  dandisetId: string,
  dandisetVersion: string,
  assetUrl: string,
  assetDandiUrl: string,
  assetS3Url: string,
}) {
  return endpoint
    .replaceAll('$dandiset_id$', data.dandisetId)
    .replaceAll('$dandiset_version$', data.dandisetVersion)
    .replaceAll('$asset_url$', data.assetUrl)
    .replaceAll('$asset_dandi_url$', data.assetDandiUrl)
    .replaceAll('$asset_s3_url$', data.assetS3Url);
}

async function redirectToNeuroglancerUrl(item: any) {
  try {
    const url = 'https://api.lincbrain.org/api/permissions/s3/' + item.asset.url; // Directly appending
    const response = await fetch(url, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    const data = await response.json();
    window.open(data.full_url, "_blank");
  } catch (error) {
    console.error('Error fetching data:', error);
  }
}

function copyToClipboard(s3Uri?: string) {
  if (s3Uri) {
    navigator.clipboard.writeText(s3Uri).then(() => {
      copied.value = true;
      setTimeout(() => {
        copied.value = false;
      }, 2000);
    }).catch(err => {
      console.error('Failed to copy text: ', err)
    });
  } else {
    console.error('No S3 URI found')
  }
}



function getExternalServices(path: AssetPath, info: {dandisetId: string, dandisetVersion: string}) {
  if (path.asset === null) {
    return [];
  }

  const servicePredicate = (service: Service, _path: AssetPath) => (
    new RegExp(service.regex).test(path.path)
          && _path.asset !== null
          && _path.aggregate_size <= service.maxsize
  );

  // Formulate the two possible asset URLs -- the direct S3 link to the relevant
  // object, and the DANDI URL that redirects to the S3 one.
  const baseApiUrl = import.meta.env.VITE_APP_DANDI_API_ROOT;
  const assetDandiUrl = `${baseApiUrl}assets/${path.asset?.asset_id}/download/`;
  const assetS3Url = trimEnd((path.asset as AssetFile).url, '/');

  // Select the best "default" URL: the direct S3 link is better when it can be
  // used, but we're forced to supply the internal DANDI URL for embargoed
  // dandisets (since the ready-made S3 URL will prevent access in that case).
  const assetUrl = embargoed.value ? assetDandiUrl : assetS3Url;

  return EXTERNAL_SERVICES
    .filter((service) => servicePredicate(service, path))
    .map((service) => ({
      name: service.name,
      url: serviceURL(service.endpoint, {
        dandisetId: info.dandisetId,
        dandisetVersion: info.dandisetVersion,
        assetUrl,
        assetDandiUrl,
        assetS3Url,
      }),
      isNeuroglancer: service.name === 'Neuroglancer',
    }));
}

function locationSlice(index: number) {
  return `${splitLocation.value.slice(0, index + 1).join('/')}/`;
}

function openItem(item: AssetPath) {
  const { asset, path } = item;

  if (asset) {
    // If the item is an asset, open it in the browser.
    window.open(inlineURI(asset.asset_id), "_self");
  } else {
    // If it's a directory, move into it.
    location.value = path;
  }
}

function navigateToParent() {
  location.value = location.value.split('/').slice(0, -1).join('/');
}

function downloadURI(asset_id: string) {
  return dandiRest.assetDownloadURI(props.identifier, props.version, asset_id);
}

function inlineURI(asset_id: string) {
  return dandiRest.assetInlineURI(props.identifier, props.version, asset_id);
}

function assetMetadataURI(asset_id: string) {
  return dandiRest.assetMetadataURI(props.identifier, props.version, asset_id);
}

function fileSize(item: AssetPath) {
  return filesize(item.aggregate_size, { round: 1, base: 10, standard: 'iec' });
}

function showDelete(item: AssetPath) {
  return props.version === 'draft' && item.asset && (isAdmin.value || isOwner.value);
}

async function getItems() {
  updating.value = true;
  let resp;
  const currentPage = Number(route.query.page) || page.value;
  try {
    resp = await dandiRest.assetPaths(
      props.identifier, props.version, location.value, currentPage, FILES_PER_PAGE,
    );
  } catch (e) {
    if (axios.isAxiosError(e) && e.response?.status === 404) {
      items.value = [];
      updating.value = false;
      return;
    }
    throw e;
  }
  const { count, results } = resp;

  // Set num pages
  pages.value = Math.ceil(count / FILES_PER_PAGE);

  // Inject extra properties
  const extendedItems: ExtendedAssetPath[] = results
    .map((path) => ({
      ...path,
      // Inject relative path
      name: path.path.split('/').pop()!,
      // Inject services
      services: getExternalServices(path, {
        dandisetId: props.identifier,
        dandisetVersion: props.version,
      }) || undefined,
    }))
    .sort(sortByFolderThenName);

  // Assign values
  items.value = extendedItems;
  updating.value = false;
}

function setItemToDelete(item: AssetPath) {
  itemToDelete.value = item;
}

async function deleteAsset() {
  if (!itemToDelete.value) {
    return;
  }
  const { asset } = itemToDelete.value;
  if (asset === null) {
    throw new Error('Attempted to delete path with no asset!');
  }

  // Delete the asset on the server.
  await dandiRest.deleteAsset(props.identifier, props.version, asset.asset_id);

  // Recompute the items to display in the browser.
  getItems();
  itemToDelete.value = null;
}

function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);

  if (parts.length === 2) {
    const part = parts.pop();
    if (part) {
      return part.split(';').shift() || null;
    }
  }
  return null;
}

function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function waitForCookie(cookieName: string, timeout = 5000, interval = 100) {
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    if (document.cookie.includes(`${cookieName}=`)) {
      return true; // Cookie found
    }
    await sleep(interval); // Wait and check again
  }

  return false; // Timeout occurred, cookie not found
}

async function handleWebKnossosClick(url: string) {
  // Check if the 'id' cookie is present
  const idCookie = getCookie('id');

  if (idCookie) {
    window.open(url, '_blank');
  } else {
    // If no cookie, call webKnossosLogin
    try {
      await dandiRest.loginWebKnossos(); // Call the login function
      
      const cookieSet = await waitForCookie('id');

      if (cookieSet) {
        window.open(url, '_blank');
      } else {
        console.error('Login to WebKNOSSOS did not populate the cookie within the timeout.');
      } // After successful login, proceed to the URL
    } catch (error) {
      console.error('Login to WebKNOSSOS failed:', error);
    }
  }
}

// Update URL if location changes
watch(location, () => {
  const { location: existingLocation } = route.query;

  // Reset page to 1 when location changes
  page.value = 1;

  // Update route when location changes
  if (existingLocation === location.value) { return; }
  router.push({
    ...route,
    query: { location: location.value, page: String(page.value) },
  } as RawLocation);
});

// go to the directory specified in the URL if it changes
watch(() => route.query, (newRouteQuery) => {
  location.value = (
    Array.isArray(newRouteQuery.location)
      ? newRouteQuery.location[0]
      : newRouteQuery.location
  ) || rootDirectory;

  // Retrieve with new location
  getItems();
}, { immediate: true });

function changePage(newPage: number) {
  page.value = newPage;
  router.push({
    ...route,
    query: { location: location.value, page: String(page.value) },
  } as RawLocation);
}

// Fetch dandiset if necessary
onMounted(() => {
  if (!store.dandiset) {
    store.initializeDandisets({
      identifier: props.identifier,
      version: props.version,
    });
  }
});
</script>
