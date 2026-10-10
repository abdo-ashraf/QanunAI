import {
  Message,
  MessageAction,
  MessageActions,
  MessageContent,
  MessageResponse,
} from "@/components/ai-elements/message";
import { useLanguage } from "@/providers/language";
import { CheckIcon, CopyIcon, RefreshCcwIcon } from "lucide-react";
import { useCallback, useState } from "react";
import type { AssistantMessage, UserMessage } from "../types";
import { AssistantSources } from "./assistant-sources";

function CopyAction({ text }: { text: string }) {
  const { t } = useLanguage();
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      // Clipboard access can be denied; ignore silently.
    }
  }, [text]);

  return (
    <MessageAction
      label={t("copy")}
      onClick={handleCopy}
      tooltip={copied ? t("copied") : t("copy")}
    >
      {copied ? (
        <CheckIcon className="size-3.5" />
      ) : (
        <CopyIcon className="size-3.5" />
      )}
    </MessageAction>
  );
}

export function UserMessageView({ message }: { message: UserMessage }) {
  return (
    <Message from="user">
      <MessageContent>
        <p className="whitespace-pre-wrap" dir="auto">
          {message.text}
        </p>
      </MessageContent>
    </Message>
  );
}

interface AssistantMessageViewProps {
  message: AssistantMessage;
  onRetry: () => void;
}

export function AssistantMessageView({
  message,
  onRetry,
}: AssistantMessageViewProps) {
  const { t } = useLanguage();

  if (message.error) {
    const text =
      message.error === "network" ? t("errorNetwork") : t("errorRequest");
    return (
      <Message from="assistant">
        <MessageContent>
          <p className="text-destructive" dir="auto">
            {text}
          </p>
        </MessageContent>
        <MessageActions>
          <MessageAction
            label={t("retry")}
            onClick={onRetry}
            tooltip={t("retry")}
          >
            <RefreshCcwIcon className="size-3.5" />
          </MessageAction>
        </MessageActions>
      </Message>
    );
  }

  return (
    <div>
      <AssistantSources documents={message.documents} />
      <Message from="assistant">
        <MessageContent>
          <div dir="auto">
            <MessageResponse>{message.text}</MessageResponse>
          </div>
        </MessageContent>
        <MessageActions>
          <CopyAction text={message.text} />
        </MessageActions>
      </Message>
    </div>
  );
}
