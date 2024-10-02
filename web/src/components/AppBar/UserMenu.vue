<template>
  <v-menu offset-y :close-on-content-click="false">
    <template #activator="{ on }">
      <v-btn icon v-on="on">
        <v-avatar color="light-blue lighten-4">
          <span class="primary--text">
            {{ userInitials }}
          </span>
        </v-avatar>
      </v-btn>
    </template>
    <v-list id="user-menu" dense>
      <v-list-item>
        <v-list-item-content>
          <span v-if="user">
            You are logged in as
            <a :href="`https://github.com/${user.username}`" target="_blank" rel="noopener" v-text="user.username" />.
          </span>
        </v-list-item-content>
      </v-list-item>
      <ApiKeyItem v-if="user?.approved" />
      <v-list-item @click="getNeuroglancerCookies" v-if="user?.approved">
        <v-list-item-content>
          Get Neuroglancer Cookies
        </v-list-item-content>
        <v-list-item-action>
          <v-icon>mdi-cookie</v-icon>
          <span v-if="cookiesRequestSuccess == 1" style="color: green; margin-left: 10px; text-wrap: wrap; max-width: 150px;">
            Success! Expires in 30 days
          </span>
          <span v-if="cookiesRequestSuccess == -1" style="color: red; margin-left: 10px; text-wrap: wrap; max-width: 150px;">
            Unable to get cookies
          </span>
        </v-list-item-action>
      </v-list-item>
      <v-list-item @click="logout">
        <v-list-item-content>
          Logout
        </v-list-item-content>
        <v-list-item-action>
          <v-icon>mdi-logout</v-icon>
        </v-list-item-action>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import {user, dandiRest, webknossosRest} from '@/rest';
import ApiKeyItem from '@/components/AppBar/ApiKeyItem.vue';

const userInitials = computed(() => {
  if (user.value) {
    const { name } = user.value;
    if (name) {
      const name_parts = name.split(' ');
      if (name_parts.length >= 2) {
        const first_name = name_parts[0];
        const last_name = name_parts[name_parts.length - 1];
        return (
          first_name.charAt(0).toLocaleUpperCase() + last_name.charAt(0).toLocaleUpperCase()
        );
      }
    }
  }
  return '??';
});

const cookiesRequestSuccess = ref(0);

async function getNeuroglancerCookies() {
  try {
    const response = await fetch('https://api.lincbrain.org/api/permissions/s3/', {
      method: 'GET', // or 'POST' if that's what the API requires
      credentials: 'include' // to ensure cookies are sent and received
    });
    const data = await response.json();
    cookiesRequestSuccess.value = 1;
    // Optionally, reset the success state after a delay
    setTimeout(() => { cookiesRequestSuccess.value = 0; }, 3000);
    // Handle the response data here
  } catch (error) {
    cookiesRequestSuccess.value = -1;
    setTimeout(() => { cookiesRequestSuccess.value = 0; }, 3000);
    console.error('Error fetching data');
  }
}



async function logout() {
  await webknossosRest.logout()
  await dandiRest.logout();
}
</script>
