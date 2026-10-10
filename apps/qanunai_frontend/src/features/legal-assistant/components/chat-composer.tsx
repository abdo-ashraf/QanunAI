import {
  PromptInput,
  PromptInputBody,
  PromptInputFooter,
  PromptInputSubmit,
  PromptInputTextarea,
} from "@/components/ai-elements/prompt-input";
import { useLanguage } from "@/providers/language";

interface ChatComposerProps {
  isPending: boolean;
  onSend: (text: string) => void;
}

export function ChatComposer({ isPending, onSend }: ChatComposerProps) {
  const { t } = useLanguage();

  return (
    <PromptInput
      onSubmit={(message) => {
        const text = message.text.trim();
        if (text) {
          onSend(text);
        }
      }}
    >
      <PromptInputBody>
        <PromptInputTextarea
          disabled={isPending}
          placeholder={t("placeholder")}
        />
      </PromptInputBody>
      <PromptInputFooter className="justify-end">
        <PromptInputSubmit
          disabled={isPending}
          status={isPending ? "submitted" : undefined}
        />
      </PromptInputFooter>
    </PromptInput>
  );
}
