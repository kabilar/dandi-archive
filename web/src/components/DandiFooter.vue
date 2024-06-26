<template>
  <v-footer class="text-body-2">
    <v-container>
      <cookie-law theme="blood-orange">
        <div slot="message">
          <span
            v-if="cookiesEnabled()"
          >We use cookies to ensure you get the best experience on
            the LINC Data Platform</span>
          <span
            v-else
          >We noticed you're blocking cookies - note that certain aspects of
            the site may not work.</span>
        </div>
      </cookie-law>
      <v-row>
        <v-col offset="2">
          &copy; 2023 - 2024 LINC<br>
          version
          <a
            class="version-link"
            :href="githubLink"
            target="_blank"
            rel="noopener"
          >{{ version }}</a>
        </v-col>
        <v-col>
          Funding / In-Kind Support:<br>
          - <a
            target="_blank"
            rel="noopener"
            href="https://braininitiative.nih.gov/"
          >BRAIN Initiative CONNECTS Program</a>
          <v-icon x-small>
            mdi-open-in-new
          </v-icon>
          <br>
          - <a
            target="_blank"
            rel="noopener"
            :href="sentryLandingPageUrl"
          >Sentry</a>
          <v-icon x-small>
            mdi-open-in-new
          </v-icon>
          <br>
        </v-col>
      </v-row>
    </v-container>
  </v-footer>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import CookieLaw from 'vue-cookie-law';

import { dandiAboutUrl, lincBrainUrl, sentryLandingPageUrl } from '@/utils/constants';
import { cookiesEnabled } from '@/rest';

const version = import.meta.env.VITE_APP_VERSION;
const githubLink = import.meta.env.VITE_APP_GIT_REVISION ? `https://github.com/lincbrain/linc-archive/commit/${import.meta.env.VITE_APP_GIT_REVISION}` : 'https://github.com/lincbrain/linc-archive';

export default defineComponent({
  name: 'DandiFooter',
  components: { CookieLaw },
  setup() {
    return {
      lincBrainUrl,
      dandiAboutUrl,
      sentryLandingPageUrl,
      version,
      githubLink,
      cookiesEnabled,
    };
  },
});
</script>

<style scoped>
@media (min-width: 1904px) {
  .container {
    max-width: 1185px;
  }
}

.version-link {
  color: inherit;
}

.version-link:hover {
  text-decoration: underline;
}
</style>
