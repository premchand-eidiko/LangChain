const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const token = localStorage.getItem("agent_token");
  const headers = new Headers(options.headers || {});
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (options.body && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!response.ok) {
    let message = "Something went wrong.";
    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {
      // Keep the friendly fallback when the server did not return JSON.
    }
    throw new Error(message);
  }
  if (response.status === 204) return null;
  return response.json();
}

export async function authenticate(mode, email, password) {
  const path = mode === "register" ? "/auth/register" : "/auth/login";
  const data = await request(path, {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  if (mode === "login") localStorage.setItem("agent_token", data.access_token);
  return data;
}

export function logout() {
  localStorage.removeItem("agent_token");
}

export const listChats = () => request("/chats");
export const getChat = (id) => request(`/chats/${id}`);
export const createChat = (title = "New conversation") =>
  request("/chats", { method: "POST", body: JSON.stringify({ title }) });
export const renameChat = (id, title) =>
  request(`/chats/${id}`, { method: "PATCH", body: JSON.stringify({ title }) });
export const deleteChat = (id) => request(`/chats/${id}`, { method: "DELETE" });
export const listDocuments = () => request("/documents");
export const getCurrentUser = () => request("/auth/me");

export async function uploadDocument(file, chatId) {
  const body = new FormData();
  body.append("upload", file);
  if (chatId) body.append("chat_id", chatId);
  return request("/documents/upload", { method: "POST", body });
}

export async function streamMessage(chatId, content, onToken, onError, signal) {
  const token = localStorage.getItem("agent_token");
  const response = await fetch(`${API_URL}/chats/${chatId}/message`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    signal,
    body: JSON.stringify({ content }),
  });
  if (!response.ok) {
    let message = "The assistant could not respond.";
    try {
      message = (await response.json()).detail || message;
    } catch {
      // Keep the friendly fallback.
    }
    throw new Error(message);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { value, done } = await reader.read();
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";
    for (const line of lines) {
      if (!line.trim()) continue;
      const event = JSON.parse(line);
      if (event.type === "token") onToken(event.content);
      if (event.type === "error") onError(event.message);
    }
    if (done) break;
  }
}
