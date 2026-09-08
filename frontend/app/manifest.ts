import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "GUARD AI Security Console",
    short_name: "GUARD AI",
    description: "Runtime security and governance for enterprise AI agents.",
    start_url: "/",
    display: "standalone",
    background_color: "#0e1319",
    theme_color: "#72c8bb",
  };
}
