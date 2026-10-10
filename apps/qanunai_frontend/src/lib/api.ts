import type { z } from "zod";

/**
 * Base URL for the QanunAI backend. Empty by default so requests go through the
 * Vite dev proxy (`/api`, `/health`). Set VITE_API_BASE_URL for other origins.
 */
export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(
  /\/+$/,
  ""
);

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(status: number, detail: unknown) {
    super(`API request failed with status ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

function extractDetail(payload: unknown): unknown {
  if (payload && typeof payload === "object" && "detail" in payload) {
    return (payload as { detail: unknown }).detail;
  }
  return undefined;
}

export async function fetchJson<Schema extends z.ZodType>(
  path: string,
  schema: Schema,
  init?: RequestInit
): Promise<z.infer<Schema>> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...init,
    });
  } catch (error) {
    throw new ApiError(0, error);
  }

  if (!response.ok) {
    let payload: unknown;
    try {
      payload = await response.json();
    } catch {
      payload = undefined;
    }
    throw new ApiError(response.status, extractDetail(payload));
  }

  const payload = await response.json();
  return schema.parse(payload);
}
