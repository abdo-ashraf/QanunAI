import {
  Conversation,
  ConversationContent,
  ConversationScrollButton,
} from "@/components/ai-elements/conversation";
import { Message, MessageContent } from "@/components/ai-elements/message";
import { Shimmer } from "@/components/ai-elements/shimmer";
import {
  Suggestion,
  Suggestions,
} from "@/components/ai-elements/suggestion";
import { useLanguage } from "@/providers/language";
import { ScaleIcon } from "lucide-react";
import type { ChatMessage } from "../types";
import { AssistantMessageView, UserMessageView } from "./chat-message";

interface ChatViewProps {
  messages: ChatMessage[];
  isPending: boolean;
  onSend: (text: string) => void;
  onRetry: () => void;
}

function EmptyState({ onSend }: { onSend: (text: string) => void }) {
  const { t, suggestions } = useLanguage();

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-5 p-6 text-center">
      <div className="flex size-14 items-center justify-center rounded-full bg-muted text-muted-foreground">
        <ScaleIcon className="size-7" />
      </div>
      <div className="space-y-1.5">
        <h2 className="text-lg font-semibold">{t("title")}</h2>
        <p className="mx-auto max-w-md text-sm text-muted-foreground">
          {t("subtitle")}
        </p>
      </div>
      <div className="w-full max-w-2xl">
        <Suggestions>
          {suggestions.map((suggestion) => (
            <Suggestion
              key={suggestion}
              onClick={onSend}
              suggestion={suggestion}
            />
          ))}
        </Suggestions>
      </div>
    </div>
  );
}

export function ChatView({
  messages,
  isPending,
  onSend,
  onRetry,
}: ChatViewProps) {
  const { t } = useLanguage();
  const isEmpty = messages.length === 0 && !isPending;

  return (
    <Conversation className="min-h-0 flex-1">
      <ConversationContent className="mx-auto w-full max-w-3xl">
        {isEmpty ? (
          <EmptyState onSend={onSend} />
        ) : (
          <>
            {messages.map((message) =>
              message.role === "user" ? (
                <UserMessageView key={message.id} message={message} />
              ) : (
                <AssistantMessageView
                  key={message.id}
                  message={message}
                  onRetry={onRetry}
                />
              )
            )}
            {isPending && (
              <Message from="assistant">
                <MessageContent>
                  <Shimmer className="text-sm">{t("thinking")}</Shimmer>
                </MessageContent>
              </Message>
            )}
          </>
        )}
      </ConversationContent>
      <ConversationScrollButton />
    </Conversation>
  );
}
