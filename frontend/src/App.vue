<script setup lang="ts">
import { onMounted, ref } from "vue";
import ConnectView from "./components/ConnectView.vue";
import PairModal from "./components/PairModal.vue";
import RemoteView from "./components/RemoteView.vue";
import { apiStatus } from "./api";

const view = ref<"connect" | "remote">("connect");
const pairOpen = ref(false);

onMounted(async () => {
  try {
    const s = await apiStatus();
    if (s.connected) view.value = "remote";
  } catch {
    /* keep connect */
  }
});

function goRemote() {
  view.value = "remote";
  pairOpen.value = false;
}

function openPairingModal() {
  pairOpen.value = true;
}
</script>

<template>
  <div class="mx-auto max-w-md px-4 pb-8 pt-6">
    <ConnectView
      v-if="view === 'connect'"
      @connected="goRemote"
      @pairing="openPairingModal"
    />
    <RemoteView v-else />
    <PairModal v-model:open="pairOpen" @paired="goRemote" />
  </div>
</template>
