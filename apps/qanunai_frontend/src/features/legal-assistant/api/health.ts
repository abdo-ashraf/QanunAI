import { z } from "zod";
import { fetchJson } from "@/lib/api";

export const healthSchema = z.object({
  status: z.string(),
  sample: z.string().optional(),
});

export type Health = z.infer<typeof healthSchema>;

export const healthKeys = {
  all: ["health"] as const,
};

/** GET /health — used for the connection indicator in the header. */
export function fetchHealth(): Promise<Health> {
  return fetchJson("/health", healthSchema);
}
