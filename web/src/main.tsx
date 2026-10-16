import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "@fontsource-variable/public-sans";
import "@fontsource-variable/source-serif-4";
import "./styles/tokens.css";
import "./styles/app.css";
import App from "./App";
import { RunProvider } from "./run";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { refetchOnWindowFocus: true, retry: 1, staleTime: 5_000 },
  },
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RunProvider>
        <App />
      </RunProvider>
    </QueryClientProvider>
  </StrictMode>,
);
