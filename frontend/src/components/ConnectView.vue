<script setup lang="ts">
import { onMounted, ref } from "vue";
import type { Device } from "@/api";
import { apiConnect, apiScan } from "@/api";

const emit = defineEmits<{
  connected: [];
  pairing: [];
}>();

const devices = ref<Device[]>([]);
const selected = ref<Device | null>(null);
const manualIp = ref("");
const scanHint = ref("Buscando en la red…");
const status = ref("");
const scanning = ref(false);
const connecting = ref(false);

function clearSelection() {
  selected.value = null;
}

function canConnect(): boolean {
  const m = manualIp.value.trim();
  return !!(selected.value || m.length >= 7);
}

async function runScan() {
  scanning.value = true;
  connecting.value = false;
  scanHint.value = "Buscando en la red…";
  status.value = "";
  devices.value = [];
  clearSelection();
  try {
    const data = await apiScan();
    devices.value = data.devices || [];
    if (devices.value.length) {
      scanHint.value = `${devices.value.length} dispositivo(s) — toca uno y pulsa Conectar`;
    } else {
      scanHint.value = "Ningún dispositivo — prueba Buscar de nuevo o IP manual";
    }
  } catch (e) {
    scanHint.value = "Error al buscar";
    status.value = e instanceof Error ? e.message : String(e);
    devices.value = [];
  } finally {
    scanning.value = false;
  }
}

function selectDevice(d: Device) {
  selected.value = d;
  manualIp.value = "";
}

async function connect() {
  const m = manualIp.value.trim();
  const ip = m.length >= 7 ? m : selected.value?.ip;
  if (!ip) {
    status.value = "Selecciona un dispositivo o escribe una IP.";
    return;
  }
  connecting.value = true;
  status.value = "Conectando…";
  try {
    const { state } = await apiConnect(ip);
    if (state === "pairing") {
      status.value = "Emparejamiento: mira la TV";
      emit("pairing");
    } else {
      emit("connected");
    }
  } catch (e) {
    status.value = e instanceof Error ? `Error: ${e.message}` : String(e);
  } finally {
    connecting.value = false;
  }
}

onMounted(() => {
  runScan();
});

function onManualInput() {
  if (manualIp.value.trim()) clearSelection();
}
</script>

<template>
  <div>
    <header class="mb-6 text-center">
      <h1 class="text-2xl font-bold tracking-tight text-zinc-100">Android TV</h1>
      <p class="mt-2 text-sm leading-relaxed text-zinc-400">
        Elige tu televisor. Mismo Wi‑Fi que el equipo que ejecuta el servidor.
      </p>
    </header>

    <div
      class="rounded-2xl border border-white/5 bg-surface p-4 shadow-card"
    >
      <p class="mb-2 text-[0.7rem] font-semibold uppercase tracking-widest text-zinc-500">
        Dispositivos encontrados
      </p>
      <p class="mb-3 min-h-[1.35em] text-sm text-zinc-400">
        <template v-if="devices.length">
          <span class="font-semibold text-accent">{{ devices.length }}</span>
          <span> dispositivo(s) — toca uno y pulsa Conectar</span>
        </template>
        <span v-else>{{ scanHint }}</span>
      </p>

      <div class="max-h-64 min-h-[100px] overflow-y-auto">
        <p
          v-if="!devices.length && !scanning"
          class="px-3 py-6 text-center text-sm text-zinc-500"
        >
          No se ha encontrado ningún Android TV. Comprueba la red o usa IP manual abajo.
        </p>
        <p v-if="scanning" class="px-3 py-6 text-center text-sm text-zinc-500">
          Escaneando…
        </p>
        <button
          v-for="d in devices"
          :key="d.ip"
          type="button"
          class="mb-2 w-full rounded-xl border border-white/10 bg-gradient-to-b from-zinc-800/80 to-zinc-900/90 px-4 py-4 text-left transition hover:border-white/15"
          :class="
            selected?.ip === d.ip
              ? 'border-accent shadow-[0_0_0_1px_#c9a227,0_4px_20px_rgba(201,162,39,0.12)]'
              : ''
          "
          @click="selectDevice(d)"
        >
          <div class="font-semibold text-zinc-100">
            {{ d.name.replace(/\.$/, "") || "Android TV" }}
          </div>
          <div class="font-mono text-xs text-zinc-500">{{ d.ip }}</div>
        </button>
      </div>

      <div class="mt-4 flex gap-2.5">
        <button
          type="button"
          class="min-h-12 flex-1 rounded-xl border border-white/10 bg-zinc-800 font-semibold text-zinc-100 transition active:bg-zinc-700 disabled:opacity-40"
          :disabled="scanning"
          @click="runScan"
        >
          Buscar de nuevo
        </button>
        <button
          type="button"
          class="min-h-12 flex-1 rounded-xl bg-gradient-to-b from-accent-hover to-accent font-semibold text-[#1a1608] shadow-[0_2px_8px_rgba(201,162,39,0.25)] transition active:brightness-105 disabled:opacity-40"
          :disabled="!canConnect() || connecting || scanning"
          @click="connect"
        >
          Conectar
        </button>
      </div>

      <details class="mt-4 border-t border-white/5 pt-4">
        <summary class="cursor-pointer text-sm text-zinc-500 [list-style:none] before:mr-1 before:text-accent before:content-['▸'] open:before:content-['▾']">
          ¿No aparece tu TV? Conectar por IP
        </summary>
        <input
          v-model="manualIp"
          type="text"
          placeholder="Ej. 192.168.1.47"
          inputmode="numeric"
          autocomplete="off"
          class="mt-3 w-full rounded-xl border border-white/10 bg-[#0e0e12] px-4 py-3.5 text-zinc-100 placeholder:text-zinc-600 focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/20"
          @input="onManualInput"
        />
      </details>

      <p v-if="status" class="mt-3 text-center text-sm text-accent">{{ status }}</p>
    </div>
  </div>
</template>
