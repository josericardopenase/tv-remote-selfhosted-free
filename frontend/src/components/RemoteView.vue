<script setup lang="ts">
import { ref } from "vue";
import { apiKey } from "@/api";
import { useKeyRepeat } from "@/composables/useKeyRepeat";

const status = ref("");

async function sendKey(key: string) {
  try {
    await apiKey(key);
    status.value = "";
  } catch (e) {
    status.value = e instanceof Error ? e.message : String(e);
  }
}

const { bindRepeat } = useKeyRepeat(sendKey);
</script>

<template>
  <div>
    <header class="mb-6 text-center">
      <h2 class="text-xl font-bold tracking-tight text-zinc-100">Mando</h2>
      <p class="mt-1 text-xs text-zinc-500">
        Mantén pulsado volumen, canales, cruceta y avance/retroceso para repetir.
      </p>
    </header>

    <!-- Primary row: power / home / back -->
    <div class="mb-5 flex justify-center gap-5">
      <button
        type="button"
        class="flex h-14 w-14 items-center justify-center rounded-full border border-red-900/40 bg-gradient-to-b from-red-900/90 to-danger text-xl text-zinc-100 shadow-[0_4px_16px_rgba(107,28,34,0.35)] active:scale-95"
        title="Power"
        @click="sendKey('POWER')"
      >
        ⏻
      </button>
      <button
        type="button"
        class="flex h-14 w-14 items-center justify-center rounded-full border border-white/10 bg-surface-elevated text-xl text-zinc-100 active:scale-95"
        title="Inicio"
        @click="sendKey('HOME')"
      >
        ⌂
      </button>
      <button
        type="button"
        class="flex h-14 w-14 items-center justify-center rounded-full border border-white/10 bg-surface-elevated text-xl text-zinc-100 active:scale-95"
        title="Atrás"
        @click="sendKey('BACK')"
      >
        ↩
      </button>
    </div>

    <!-- Volume (hold to repeat) -->
    <div class="mb-5 rounded-2xl border border-white/5 bg-surface p-3 shadow-card">
      <button
        type="button"
        class="mb-2 w-full touch-manipulation select-none rounded-xl border border-white/10 bg-zinc-800 py-3.5 font-semibold text-zinc-100 active:bg-zinc-700"
        v-bind="bindRepeat('VOLUME_UP')"
      >
        Vol +
      </button>
      <button
        type="button"
        class="w-full touch-manipulation select-none rounded-xl border border-white/10 bg-zinc-800 py-3.5 font-semibold text-zinc-100 active:bg-zinc-700"
        v-bind="bindRepeat('VOLUME_DOWN')"
      >
        Vol −
      </button>
    </div>

    <!-- Mute / Menu -->
    <div class="mb-5 flex justify-center gap-2.5">
      <button
        type="button"
        class="rounded-full border border-white/10 bg-zinc-800 px-5 py-2.5 text-sm font-semibold text-zinc-100 active:bg-zinc-700"
        @click="sendKey('MUTE')"
      >
        Mudo
      </button>
      <button
        type="button"
        class="rounded-full border border-white/10 bg-zinc-800 px-5 py-2.5 text-sm font-semibold text-zinc-100 active:bg-zinc-700"
        @click="sendKey('MENU')"
      >
        Menú
      </button>
    </div>

    <!-- Guide / Info / Input -->
    <p class="mb-2 text-center text-[0.65rem] font-semibold uppercase tracking-widest text-zinc-500">
      TV &amp; guía
    </p>
    <div class="mb-5 grid grid-cols-3 gap-2">
      <button
        v-for="item in [
          { k: 'GUIDE', l: 'Guía' },
          { k: 'INFO', l: 'Info' },
          { k: 'TV_INPUT', l: 'Entrada' },
        ]"
        :key="item.k"
        type="button"
        class="rounded-xl border border-white/10 bg-zinc-800/90 py-3 text-xs font-semibold text-zinc-100 active:bg-zinc-700"
        @click="sendKey(item.k)"
      >
        {{ item.l }}
      </button>
    </div>

    <!-- Channels (hold to repeat) -->
    <div class="mb-5 grid grid-cols-2 gap-2">
      <button
        type="button"
        class="touch-manipulation select-none rounded-xl border border-white/10 bg-zinc-800 py-3 text-sm font-semibold text-zinc-100 active:bg-zinc-700"
        v-bind="bindRepeat('CHANNEL_UP')"
      >
        Canal +
      </button>
      <button
        type="button"
        class="touch-manipulation select-none rounded-xl border border-white/10 bg-zinc-800 py-3 text-sm font-semibold text-zinc-100 active:bg-zinc-700"
        v-bind="bindRepeat('CHANNEL_DOWN')"
      >
        Canal −
      </button>
    </div>

    <!-- Captions / Settings / Assist -->
    <div class="mb-5 grid grid-cols-3 gap-2">
      <button
        type="button"
        class="rounded-xl border border-white/10 bg-zinc-800/80 py-2.5 text-[0.7rem] font-semibold leading-tight text-zinc-100 active:bg-zinc-700"
        @click="sendKey('CAPTIONS')"
      >
        Subtítulos
      </button>
      <button
        type="button"
        class="rounded-xl border border-white/10 bg-zinc-800/80 py-2.5 text-[0.7rem] font-semibold leading-tight text-zinc-100 active:bg-zinc-700"
        @click="sendKey('SETTINGS')"
      >
        Ajustes
      </button>
      <button
        type="button"
        class="rounded-xl border border-white/10 bg-zinc-800/80 py-2.5 text-[0.7rem] font-semibold leading-tight text-zinc-100 active:bg-zinc-700"
        @click="sendKey('ASSIST')"
      >
        Asistente
      </button>
    </div>

    <!-- Color buttons (many STBs / TVs) -->
    <p class="mb-2 text-center text-[0.65rem] font-semibold uppercase tracking-widest text-zinc-500">
      Colores
    </p>
    <div class="mb-6 flex justify-center gap-3">
      <button
        v-for="c in [
          { k: 'PROG_RED', cls: 'bg-red-700' },
          { k: 'PROG_GREEN', cls: 'bg-green-700' },
          { k: 'PROG_YELLOW', cls: 'bg-yellow-500 text-zinc-900' },
          { k: 'PROG_BLUE', cls: 'bg-blue-700' },
        ]"
        :key="c.k"
        type="button"
        class="h-10 w-10 rounded-full border border-white/10 font-mono text-[0.65rem] font-bold active:scale-95"
        :class="c.cls"
        :title="c.k"
        @click="sendKey(c.k)"
      >
        ●
      </button>
    </div>

    <!-- D-pad -->
    <div class="mb-6 rounded-2xl border border-white/5 bg-surface p-4 shadow-inner">
      <p class="mb-3 text-center text-[0.65rem] font-semibold uppercase tracking-widest text-zinc-500">
        Navegación
      </p>
      <div class="mx-auto grid max-w-[280px] grid-cols-3 gap-2">
        <div />
        <button
          type="button"
          class="min-h-12 touch-manipulation select-none rounded-xl border border-white/10 bg-zinc-800 font-semibold text-zinc-100 active:bg-zinc-700"
          v-bind="bindRepeat('DPAD_UP')"
        >
          ▲
        </button>
        <div />
        <button
          type="button"
          class="min-h-12 touch-manipulation select-none rounded-xl border border-white/10 bg-zinc-800 font-semibold text-zinc-100 active:bg-zinc-700"
          v-bind="bindRepeat('DPAD_LEFT')"
        >
          ◀
        </button>
        <button
          type="button"
          class="min-h-12 touch-manipulation select-none rounded-xl border border-accent/40 bg-gradient-to-b from-zinc-700/80 to-zinc-900 font-bold text-accent active:bg-zinc-700"
          @click="sendKey('DPAD_CENTER')"
        >
          OK
        </button>
        <button
          type="button"
          class="min-h-12 touch-manipulation select-none rounded-xl border border-white/10 bg-zinc-800 font-semibold text-zinc-100 active:bg-zinc-700"
          v-bind="bindRepeat('DPAD_RIGHT')"
        >
          ▶
        </button>
        <div />
        <button
          type="button"
          class="min-h-12 touch-manipulation select-none rounded-xl border border-white/10 bg-zinc-800 font-semibold text-zinc-100 active:bg-zinc-700"
          v-bind="bindRepeat('DPAD_DOWN')"
        >
          ▼
        </button>
        <div />
      </div>
    </div>

    <!-- Playback -->
    <p class="mb-3 text-center text-[0.65rem] font-semibold uppercase tracking-widest text-zinc-500">
      Reproducción
    </p>
    <div class="flex flex-wrap justify-center gap-3">
      <button
        type="button"
        class="flex h-12 w-12 touch-manipulation select-none items-center justify-center rounded-full border border-white/10 bg-surface-elevated text-lg active:scale-95"
        v-bind="bindRepeat('MEDIA_REWIND')"
      >
        ⏮
      </button>
      <button
        type="button"
        class="flex h-12 w-12 items-center justify-center rounded-full border border-white/10 bg-surface-elevated text-lg active:scale-95"
        @click="sendKey('MEDIA_PLAY_PAUSE')"
      >
        ⏯
      </button>
      <button
        type="button"
        class="flex h-12 w-12 touch-manipulation select-none items-center justify-center rounded-full border border-white/10 bg-surface-elevated text-lg active:scale-95"
        v-bind="bindRepeat('MEDIA_FAST_FORWARD')"
      >
        ⏭
      </button>
      <button
        type="button"
        class="flex h-12 w-12 items-center justify-center rounded-full border border-white/10 bg-surface-elevated text-lg active:scale-95"
        @click="sendKey('MEDIA_PREVIOUS')"
        title="Anterior"
      >
        ⏪
      </button>
      <button
        type="button"
        class="flex h-12 w-12 items-center justify-center rounded-full border border-white/10 bg-surface-elevated text-lg active:scale-95"
        @click="sendKey('MEDIA_NEXT')"
        title="Siguiente"
      >
        ⏩
      </button>
      <button
        type="button"
        class="flex h-12 w-12 items-center justify-center rounded-full border border-white/10 bg-surface-elevated text-lg active:scale-95"
        @click="sendKey('MEDIA_STOP')"
        title="Stop"
      >
        ⏹
      </button>
    </div>

    <p v-if="status" class="mt-6 text-center text-sm text-accent">{{ status }}</p>
  </div>
</template>
