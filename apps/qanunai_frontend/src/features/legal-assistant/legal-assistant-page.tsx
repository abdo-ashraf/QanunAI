import { useLanguage } from "@/providers/language";
import { AssistantHeader } from "./components/assistant-header";
import { ChatComposer } from "./components/chat-composer";
import { ChatView } from "./components/chat-view";
import { useLegalAssistant } from "./hooks/use-legal-assistant";

export function LegalAssistantPage() {
  const { dir, t } = useLanguage();
  const { messages, isPending, send, retry, clear } = useLegalAssistant();

  return (
    <div className="flex h-dvh flex-col bg-background" dir={dir}>
      <AssistantHeader
        canReset={messages.length > 0 || isPending}
        onNewChat={clear}
      />
      <main className="flex min-h-0 flex-1 flex-col">
        <ChatView
          isPending={isPending}
          messages={messages}
          onRetry={retry}
          onSend={send}
        />
      </main>
      <footer className="border-t bg-background">
        <div className="mx-auto w-full max-w-3xl px-4 py-3">
          <ChatComposer isPending={isPending} onSend={send} />
          <p className="mt-2 text-center text-[11px] text-muted-foreground">
            {t("subtitle")}
          </p>
        </div>
      </footer>
    </div>
  );
}
