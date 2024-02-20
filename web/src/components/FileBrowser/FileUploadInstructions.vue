<template>
  <v-sheet
    v-if="dandisetIdentifier"
    class="d-flex"
    height="70vh"
  >
    <v-row
      class="d-flex flex-column justify-center text-center"
    >
      <div class="text-h6 font-weight-light">
        This Dataset does not currently have any files associated with it,
        but this is where they will appear once they're added.
      </div>
      <div class="my-7">
        <span class="text-subtitle-1">Use the LINC Brain CLI on the command line:</span>
        <div
          class="d-flex justify-center"
          style="font-family: monospace;"
        >
          <v-sheet
            color="black"
            width="60%"
            class="white--text pl-2 py-1 text-left"
          >
            <div>{{ downloadCommand }}</div>
            <div>> cd {{ dandisetIdentifier }}</div>
            <div>> lincbrain organize &lt;source_folder&gt; -f dry</div>
            <div>> lincbrain organize &lt;source_folder&gt;</div>
            <div>> lincbrain upload</div>
          </v-sheet>
        </div>
      </div>
      <div>
        <span class="text-subtitle-1">Don't have LINC Brain CLI?</span>
        <div>
          <span class="text-body-2 grey--text text--darken-1">
            <span class="text-body-2 grey--text text--darken-1">
              Follow the installation instructions in the
              <a href="https://www.dandiarchive.org/handbook/10_using_dandi/#dandi-python-client">
                DANDI handbook
              </a> .
            </span>
          </span>
        </div>
      </div>
    </v-row>
  </v-sheet>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useDandisetStore } from '@/stores/dandiset';

const store = useDandisetStore();
const dandisetIdentifier = computed(() => store.dandiset?.dandiset.identifier);

const downloadCommand = computed(() => {
  const baseUrl = import.meta.env.VITE_APP_DANDI_API_ROOT === 'https://staging-api.lincbrain.org/api/'
    ? 'https://staging--lincbrain-org.netlify.app/dandiset/'
    : 'https://lincbrain.org/dandiset/';

  return dandisetIdentifier.value
    ? `> lincbrain download ${baseUrl}${dandisetIdentifier.value}/draft`
    : ''; // Empty string just as a fallback in case store.dandiset? is undefined
});
</script>

