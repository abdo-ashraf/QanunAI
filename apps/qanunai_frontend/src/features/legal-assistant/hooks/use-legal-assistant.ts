import { useMutation } from "@tanstack/react-query";
import { useCallback, useState } from "react";
import { ApiError } from "@/lib/api";
import { askQuestion, type QueryResponse } from "../api/rag";
import {
  createMessageId,
  type AssistantErrorCode,
  type AssistantMessage,
  type ChatMessage,
} from "../types";

function toErrorCode(error: unknown): AssistantErrorCode {
  if (error instanceof ApiError && error.status === 0) {
    return "network";
  }
  return "request";
}

function assistantFromResponse(data: QueryResponse): AssistantMessage {
  return {
    id: createMessageId(),
    role: "assistant",
    text: data.answer,
    documents: data.documents,
  };
}

/**
 * Local chat transcript for a stateless backend. The backend does not accept
 * conversation history, so each turn is an independent question/answer pair.
 */
export function useLegalAssistant() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [lastQuery, setLastQuery] = useState<string | null>(null);

  const mutation = useMutation({ mutationFn: askQuestion, retry: false });

  const request = useCallback(
    (query: string) => {
      mutation.mutate(query, {
        onSuccess: (data) =>
          setMessages((prev) => [...prev, assistantFromResponse(data)]),
        onError: (error) =>
          setMessages((prev) => [
            ...prev,
            {
              id: createMessageId(),
              role: "assistant",
              text: "",
              documents: [],
              error: toErrorCode(error),
            },
          ]),
      });
    },
    [mutation]
  );

  const send = useCallback(
    (raw: string) => {
      const query = raw.trim();
      if (!query) {
        return;
      }
      setLastQuery(query);
      setMessages((prev) => [
        ...prev,
        { id: createMessageId(), role: "user", text: query },
      ]);
      request(query);
    },
    [request]
  );

  const retry = useCallback(() => {
    if (!lastQuery) {
      return;
    }
    setMessages((prev) => {
      const last = prev.at(-1);
      if (last && last.role === "assistant" && last.error) {
        return prev.slice(0, -1);
      }
      return prev;
    });
    request(lastQuery);
  }, [lastQuery, request]);

  const clear = useCallback(() => {
    setMessages([]);
    setLastQuery(null);
    mutation.reset();
  }, [mutation]);

  return {
    messages,
    isPending: mutation.isPending,
    send,
    retry,
    clear,
  };
}
