<script setup lang="ts">
import { ref, watch } from "vue";
import { apiPair } from "@/api";

const open = defineModel<boolean>("open", { required: true });
const emit = defineEmits<{ paired: [] }>();

const code = ref("");
const err = ref("");

watch(open, (v) => {
  if (v) {
    code.value = "";
    err.value = "";
  }
});

async function submit() {
  const c = code.value.trim();
  if (c.length !== 6) {
    err.value = "El código debe tener 6 caracteres hex.";
    return;
  }
  err.value = "";
  try {
    await apiPair(c);
    open.value = false;
    emit("paired");
  } catch (e) {
    err.value = e instanceof Error ? e.message : String(e);
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-show="open"
      class="fixed inset-0 z-[200] flex items-center justify-center bg-black/70 p-6 backdrop-blur-sm"
      @click.self="open = false"
    >
      <div
        class="w-full max-w-sm rounded-2xl border border-white/10 bg-surface p-6 shadow-card"
        @click.stop
      >
        <p class="mb-4 text-sm leading-relaxed text-zinc-100">
          Introduce el código de <strong class="text-accent">6 caracteres hex</strong> que muestra la TV.
        </p>
        <input
          v-model="code"
          type="text"
          maxlength="6"
          autocomplete="off"
          placeholder="a1b2c3"
          class="w-full rounded-xl border border-white/10 bg-[#0e0e12] px-4 py-3.5 font-mono text-lg tracking-widest text-zinc-100 placeholder:text-zinc-600 focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/20"
          @keyup.enter="submit"
        />
        <p v-if="err" class="mt-2 text-sm text-red-400">{{ err }}</p>
        <button
          type="button"
          class="mt-4 w-full min-h-12 rounded-xl bg-gradient-to-b from-accent-hover to-accent font-semibold text-[#1a1608] shadow-[0_2px_8px_rgba(201,162,39,0.25)]"
          @click="submit"
        >
          Emparejar
        </button>
      </div>
    </div>
  </Teleport>
</template>
