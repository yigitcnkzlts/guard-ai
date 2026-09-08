import type { MetadataRoute } from "next";

const baseUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "https://guard-ai.vercel.app";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: "*", allow: ["/product", "/trust-center"], disallow: ["/login", "/api/"] },
    sitemap: `${baseUrl}/sitemap.xml`,
  };
}
