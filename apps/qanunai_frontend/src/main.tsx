import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { TooltipProvider } from "@/components/ui/tooltip";
import { LanguageProvider } from "@/providers/language";
import { QueryProvider } from "@/providers/query-client";
import App from "./App";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <LanguageProvider>
      <QueryProvider>
        <TooltipProvider>
          <App />
        </TooltipProvider>
      </QueryProvider>
    </LanguageProvider>
  </StrictMode>
);
