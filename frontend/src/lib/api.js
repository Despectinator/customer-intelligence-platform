import { supabase } from "./supabaseClient";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function request(
  path,
  { method = "GET", body, headers = {} } = {},
  hasRetried = false
) {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  const isFormData = body instanceof FormData;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 70000);

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers: {
        ...(body && !isFormData ? { "Content-Type": "application/json" } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...headers,
      },
      body: body ? (isFormData ? body : JSON.stringify(body)) : undefined,
      signal: controller.signal,
    });

    if (response.status === 401 && !hasRetried) {
      const { data: refreshedSession, error: refreshError } =
        await supabase.auth.refreshSession();

      if (!refreshError && refreshedSession.session?.access_token) {
        return request(path, { method, body, headers }, true);
      }
    }

    if (!response.ok) {
      let detail;

      try {
        const errorBody = await response.json();
        detail = errorBody.detail || errorBody.message;
      } catch {
        detail = response.statusText;
      }

      const error = new Error(
        detail || `Request failed with status ${response.status}`
      );
      error.status = response.status;
      throw error;
    }

    if (response.status === 204) return null;
    return await response.json();
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error(
        "The backend took too long to respond. If it has been idle, it may still be waking up — try again in a moment.",
        { cause: error }
      );
    }

    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

export const api = {
  get: (path) => request(path),
  post: (path, body) => request(path, { method: "POST", body }),
  put: (path, body) => request(path, { method: "PUT", body }),
  del: (path) => request(path, { method: "DELETE" }),
};
