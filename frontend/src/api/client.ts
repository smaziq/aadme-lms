const API_BASE = import.meta.env.VITE_API_BASE ?? "";

export async function apiRequest<T>(
  path: string,
  options: { method?: string; body?: unknown; token?: string | null } = {},
): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (options.token) headers.Authorization = `Token ${options.token}`;
  const res = await fetch(`${API_BASE}${path}`, {
    method: options.method ?? "GET",
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export async function apiDownload(
  path: string,
  token: string,
  filename: string,
): Promise<void> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { Authorization: `Token ${token}` },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

export async function apiUpload<T>(
  path: string,
  file: File,
  token: string | null,
): Promise<T> {
  const form = new FormData();
  form.append("file", file);
  const headers: Record<string, string> = {};
  if (token) headers.Authorization = `Token ${token}`;
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    body: form,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
}