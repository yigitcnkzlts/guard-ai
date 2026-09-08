try {
  performance.mark("guard-app-init");
  window.addEventListener("error", (event) => {
    console.error("[GUARD UI]", { message: event.message, source: event.filename });
  });
  window.addEventListener("unhandledrejection", (event) => {
    console.error("[GUARD UI] Unhandled promise rejection", event.reason);
  });
} catch {
  // Observability must never prevent the console from loading.
}

export function onRouterTransitionStart(url: string) {
  performance.mark(`guard-navigation:${url}`);
}
