export const locales = ["ar", "en"] as const;
export type Locale = (typeof locales)[number];

export interface Messages {
  title: string;
  subtitle: string;
  placeholder: string;
  newChat: string;
  newChatTooltip: string;
  usedSources: string;
  sourceLabel: string;
  similarity: string;
  thinking: string;
  errorRequest: string;
  errorNetwork: string;
  retry: string;
  copy: string;
  copied: string;
  healthOnline: string;
  healthOffline: string;
  languageLabel: string;
  suggestions: string[];
}

export type TextKey = Exclude<keyof Messages, "suggestions">;

export const messages: Record<Locale, Messages> = {
  ar: {
    title: "قانوني",
    subtitle:
      "مساعد قانوني يجيب عن أسئلتك بالاستناد إلى القانون المدني المصري لعام 1948 مع ذكر المصادر.",
    placeholder: "اكتب سؤالك القانوني هنا…",
    newChat: "محادثة جديدة",
    newChatTooltip: "بدء محادثة جديدة",
    usedSources: "المصادر ({count})",
    sourceLabel: "مصدر {index}",
    similarity: "التشابه",
    thinking: "يبحث في القانون المدني…",
    errorRequest:
      "تعذّر الحصول على إجابة. المساعد غير متاح حالياً، يرجى المحاولة لاحقاً.",
    errorNetwork:
      "تعذّر الاتصال بالخادم. تأكد من أن الخادم يعمل ثم أعد المحاولة.",
    retry: "إعادة المحاولة",
    copy: "نسخ",
    copied: "تم النسخ",
    healthOnline: "متصل",
    healthOffline: "غير متصل",
    languageLabel: "English",
    suggestions: [
      "ما هي أركان العقد في القانون المدني المصري؟",
      "ما هي حالات انقضاء الالتزام؟",
      "ما الفرق بين الإعذار والفسخ؟",
      "ما هي أحكام المسؤولية التقصيرية؟",
    ],
  },
  en: {
    title: "QanunAI",
    subtitle:
      "A legal Q&A assistant that answers based on the Egyptian Civil Code of 1948, with cited sources.",
    placeholder: "Ask a legal question…",
    newChat: "New chat",
    newChatTooltip: "Start a new conversation",
    usedSources: "Sources ({count})",
    sourceLabel: "Source {index}",
    similarity: "Similarity",
    thinking: "Searching the Civil Code…",
    errorRequest:
      "The assistant could not answer right now. It may be temporarily unavailable, please try again later.",
    errorNetwork:
      "Could not reach the server. Make sure the backend is running, then retry.",
    retry: "Retry",
    copy: "Copy",
    copied: "Copied",
    healthOnline: "Online",
    healthOffline: "Offline",
    languageLabel: "العربية",
    suggestions: [
      "What are the essential elements of a contract in Egyptian civil law?",
      "What are the ways an obligation is extinguished?",
      "What is the difference between notice and rescission?",
      "What are the rules of tort liability?",
    ],
  },
};
