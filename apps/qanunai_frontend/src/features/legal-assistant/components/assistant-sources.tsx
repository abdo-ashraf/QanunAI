import {
  Source,
  Sources,
  SourcesContent,
  SourcesTrigger,
} from "@/components/ai-elements/sources";
import { useLanguage } from "@/providers/language";
import { FileTextIcon } from "lucide-react";
import type { RetrievedDocument } from "../api/rag";

interface AssistantSourcesProps {
  documents: RetrievedDocument[];
}

function titleFor(
  document: RetrievedDocument,
  index: number,
  fallback: (index: number) => string
) {
  const source = document.meta.source;
  if (typeof source === "string" && source.trim().length > 0) {
    return source;
  }
  return fallback(index);
}

export function AssistantSources({ documents }: AssistantSourcesProps) {
  const { t } = useLanguage();

  if (documents.length === 0) {
    return null;
  }

  return (
    <Sources>
      <SourcesTrigger
        count={documents.length}
        className="w-fit cursor-pointer text-primary hover:underline"
      >
        <span className="font-medium">
          {t("usedSources").replace("{count}", String(documents.length))}
        </span>
      </SourcesTrigger>
      <SourcesContent>
        {documents.map((document, index) => (
          <Source
            key={`${index}-${document.content.slice(0, 24)}`}
            className="flex w-full max-w-xl flex-col items-start gap-1.5 rounded-lg border bg-card p-3 text-start no-underline transition-colors hover:bg-muted/50"
          >
            <span className="flex w-full items-center justify-between gap-2">
              <span className="flex min-w-0 items-center gap-1.5 text-xs font-medium text-foreground">
                <FileTextIcon className="size-3.5 shrink-0" />
                <span className="truncate" dir="auto">
                  {titleFor(document, index, (i) =>
                    t("sourceLabel").replace("{index}", String(i + 1))
                  )}
                </span>
              </span>
              {document.score !== null && (
                <span className="shrink-0 rounded bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground">
                  {t("similarity")} {Math.round(document.score * 100)}%
                </span>
              )}
            </span>
            <span
              className="line-clamp-3 text-xs text-muted-foreground"
              dir="auto"
            >
              {document.content}
            </span>
          </Source>
        ))}
      </SourcesContent>
    </Sources>
  );
}
