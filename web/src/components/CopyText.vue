<template>
  <v-textarea
    v-if="isTextarea == true"
    ref="textField"
    :model-value="text"
    class="cite-as-textarea"
    hide-details="auto"
    variant="outlined"
    readonly
    v-bind="$attrs"
  >
    <template #prepend>
      <v-tooltip location="bottom">
        <template #activator="{ props: tooltipProps }">
          <v-icon
            v-bind="tooltipProps"
            @click="copyToClipboard"
          >
            mdi-content-copy
          </v-icon>
        </template>
        {{ iconHoverText }}
      </v-tooltip>
    </template>
  </v-textarea>

  <v-text-field
    v-else
    v-bind="$attrs"
    id="api-key-text"
    ref="textField"
    class="my-1"
    :model-value="displayedText"
    hide-details="auto"
    variant="outlined"
    density="compact"
    readonly
    :append-inner-icon="secret ? (revealed ? 'mdi-eye-off' : 'mdi-eye') : undefined"
    @click:append-inner="toggleRevealed"
  >
    <template #prepend>
      <v-tooltip location="bottom">
        <template #activator="{ props: tooltipProps }">
          <v-icon
            v-bind="tooltipProps"
            @click="copyToClipboard"
          >
            mdi-content-copy
          </v-icon>
        </template>
        {{ iconHoverText }}
      </v-tooltip>
    </template>
  </v-text-field>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';

defineOptions({
  // This will prevent arbitrary props from being rendered as HTML attributes
  // v-bind="$attrs" ensures that props are ingested as vue props instead
  inheritAttrs: false,
});

const props = defineProps({
  text: {
    type: String,
    default: '',
  },
  iconHoverText: {
    type: String,
    default: 'Copy text to clipboard',
  },
  isTextarea: {
    type: Boolean,
    default: false,
  },
  // Mask the text until the user clicks the reveal icon. Copying always
  // copies the real text.
  secret: {
    type: Boolean,
    default: false,
  },
});

const revealed = ref(false);

function toggleRevealed(e: MouseEvent) {
  // Prevent closing a parent v-menu when the reveal icon is clicked
  e.stopPropagation();
  revealed.value = !revealed.value;
}

// Use a fixed-length mask rather than type="password", which would invite
// browser password managers to offer to save the value.
const displayedText = computed(() => (
  props.secret && !revealed.value && props.text ? '•'.repeat(16) : props.text
));

const textField = ref<HTMLElement | null>(null);

async function copyToClipboard() {
  try {
    await navigator.clipboard.writeText(props.text);
    console.log('Copied to clipboard');
  } catch (err) {
    console.error('Failed to copy:', err);
  }
}
</script>

<style>
.cite-as-textarea textarea {
  overflow: auto;
}
</style>
