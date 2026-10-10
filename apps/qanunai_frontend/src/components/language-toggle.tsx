import { Button } from "@/components/ui/button";
import { useLanguage } from "@/providers/language";
import { GlobeIcon } from "lucide-react";

export function LanguageToggle() {
  const { locale, t, toggleLocale } = useLanguage();

  return (
    <Button
      aria-label={t("languageLabel")}
      onClick={toggleLocale}
      size="sm"
      variant="ghost"
    >
      <GlobeIcon className="size-4" />
      <span>{t("languageLabel")}</span>
      <span className="sr-only">{locale}</span>
    </Button>
  );
}
