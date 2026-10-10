import { z } from "zod";
import { fetchJson } from "@/lib/api";

export const retrievedDocumentSchema = z.object({
  content: z.string(),
  score: z.number().nullable(),
  meta: z.record(z.string(), z.unknown()),
});

export type RetrievedDocument = z.infer<typeof retrievedDocumentSchema>;

export const queryResponseSchema = z.object({
  answer: z.string(),
  documents: z.array(retrievedDocumentSchema),
});

export type QueryResponse = z.infer<typeof queryResponseSchema>;

export const ragKeys = {
  all: ["rag"] as const,
};

/** POST /api/v1/rag/query — asks the RAG assistant a question. */
export function askQuestion(query: string): Promise<QueryResponse> {
  return fetchJson("/api/v1/rag/query", queryResponseSchema, {
    method: "POST",
    body: JSON.stringify({ query }),
  });
}
