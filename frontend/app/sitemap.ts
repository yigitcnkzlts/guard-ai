import type { MetadataRoute } from "next";

const baseUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "https://guard-ai.vercel.app";

export default function sitemap(): MetadataRoute.Sitemap {
  return ["/product", "/trust-center", "/pricing"].map((path, index) => ({
    url: `${baseUrl}${path}`,
    changeFrequency: index === 0 ? "weekly" : "monthly",
    priority: index === 0 ? 1 : 0.7,
  }));
}
