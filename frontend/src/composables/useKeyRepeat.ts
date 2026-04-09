import { onUnmounted } from "vue";

/** Hold to repeat: first key on down, then after a delay at ~120ms (volume, D-pad, etc.). */
export function useKeyRepeat(sendKey: (k: string) => Promise<void>) {
  let delayT: ReturnType<typeof setTimeout> | null = null;
  let intervalT: ReturnType<typeof setInterval> | null = null;

  function clearTimers() {
    if (delayT !== null) {
      clearTimeout(delayT);
      delayT = null;
    }
    if (intervalT !== null) {
      clearInterval(intervalT);
      intervalT = null;
    }
  }

  function stop() {
    clearTimers();
  }

  function start(key: string) {
    clearTimers();
    void sendKey(key);
    delayT = setTimeout(() => {
      intervalT = setInterval(() => void sendKey(key), 120);
    }, 420);
  }

  onUnmounted(stop);

  /** Use on volume, channels, D-pad, etc. — no @click on the same control. */
  function bindRepeat(key: string) {
    return {
      onPointerdown: (e: PointerEvent) => {
        e.preventDefault();
        const el = e.currentTarget as HTMLElement | null;
        if (el?.setPointerCapture) {
          try {
            el.setPointerCapture(e.pointerId);
          } catch {
            /* ignore */
          }
        }
        start(key);
      },
      onPointerup: stop,
      onPointercancel: stop,
      onLostPointerCapture: stop,
      onContextmenu: (e: Event) => e.preventDefault(),
    };
  }

  return { bindRepeat, stop };
}
