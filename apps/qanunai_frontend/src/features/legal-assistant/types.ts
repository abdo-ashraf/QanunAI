import type { RetrievedDocument } from "./api/rag";

export interface UserMessage {
  id: string;
  role: "user";
  text: string;
}

export type AssistantErrorCode = "request" | "network";

export interface AssistantMessage {
  id: string;
  role: "assistant";
  text: string;
  documents: RetrievedDocument[];
  /** When set, the message represents a failed request that can be retried. */
  error?: AssistantErrorCode;
}

export type ChatMessage = UserMessage | AssistantMessage;

export function createMessageId(): string {
  return crypto.randomUUID();
}
