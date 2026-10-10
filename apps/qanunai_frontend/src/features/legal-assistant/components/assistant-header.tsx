import { LanguageToggle } from "@/components/language-toggle";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/providers/language";
import { PlusIcon, ScaleIcon } from "lucide-react";
import { useHealth } from "../hooks/use-health";

interface AssistantHeaderProps {
  canReset: boolean;
  onNewChat: () => void;
}

function HealthIndicator() {
  const { t } = useLanguage();
  const health = useHealth();

  const online = health.isSuccess;
  const dotClassName = online
    ? "bg-emerald-500"
    : health.isError
      ? "bg-destructive"
      : "bg-muted-foreground/40";

  return (
    <span className="flex items-center gap-1.5" title={online ? t("healthOnline") : t("healthOffline")}>
      <span className={cn("size-2 rounded-full", dotClassName)} />
      <span className="hidden text-xs text-muted-foreground sm:inline">
        {online ? t("healthOnline") : t("healthOffline")}
      </span>
    </span>
  );
}

export function AssistantHeader({
  canReset,
  onNewChat,
}: AssistantHeaderProps) {
  const { t } = useLanguage();

  return (
    <header className="border-b bg-background/95 backdrop-blur">
      <div className="mx-auto flex w-full max-w-3xl items-center justify-between gap-2 px-4 py-3">
        <div className="flex min-w-0 items-center gap-2">
          <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <ScaleIcon className="size-4" />
          </span>
          <div className="min-w-0">
            <p className="truncate font-semibold leading-tight">{t("title")}</p>
            <HealthIndicator />
          </div>
        </div>
        <div className="flex items-center gap-1">
          <LanguageToggle />
          <Button
            aria-label={t("newChatTooltip")}
            disabled={!canReset}
            onClick={onNewChat}
            size="sm"
            title={t("newChatTooltip")}
            variant="ghost"
          >
            <PlusIcon className="size-4" />
            <span className="hidden sm:inline">{t("newChat")}</span>
          </Button>
        </div>
      </div>
    </header>
  );
}
