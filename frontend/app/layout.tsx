import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Discovery Pulse AI — Myntra Wishlist Intelligence Engine",
  description: "Groq-powered research engine uncovering Indian fashion e-commerce shopping behaviors, wishlist intent, and purchase friction across 20,000+ reviews.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
