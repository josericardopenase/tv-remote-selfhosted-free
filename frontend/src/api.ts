export type Device = { name: string; ip: string };

export type ConnectState = "connected" | "pairing";

function errDetail(data: Record<string, unknown>, r: Response): string {
  const d = data.detail;
  if (Array.isArray(d))
    return d.map((x: { msg?: string }) => x.msg || JSON.stringify(x)).join("; ");
  if (typeof d === "string") return d;
  return (data.message as string) || r.statusText;
}

async function postJson<T>(path: string, body: object = {}): Promise<T> {
  const r = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = (await r.json().catch(() => ({}))) as Record<string, unknown>;
  if (!r.ok) throw new Error(errDetail(data, r));
  return data as T;
}

export async function apiStatus(): Promise<{ connected: boolean; pairing: boolean }> {
  const r = await fetch("/api/status");
  if (!r.ok) throw new Error(r.statusText);
  return r.json() as Promise<{ connected: boolean; pairing: boolean }>;
}

export async function apiScan(): Promise<{ devices: Device[] }> {
  return postJson("/api/scan");
}

export async function apiConnect(ip: string): Promise<{ state: ConnectState }> {
  return postJson("/api/connect", { ip });
}

export async function apiPair(code: string): Promise<{ ok: boolean }> {
  return postJson("/api/pair", { code });
}

export async function apiKey(key: string): Promise<{ ok: boolean }> {
  return postJson("/api/key", { key });
}
