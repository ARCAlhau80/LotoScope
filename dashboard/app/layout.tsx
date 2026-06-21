import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "LotoScope — Dashboard de Análise Inteligente da Lotofácil",
  description:
    "Dashboard inteligente para análise de resultados da Lotofácil com estatísticas, previsões por Poisson, ciclos de frequência e análise de grupos A/B/C.",
  applicationName: "LotoScope",
  keywords: ["Lotofácil", "loteria", "análise", "estatística", "dashboard", "previsão"],
  authors: [{ name: "LotoScope" }],
  openGraph: {
    title: "LotoScope — Análise Inteligente da Lotofácil",
    description:
      "Dashboard com estatísticas, previsões posicionais, ciclos de frequência e análise de grupos para a Lotofácil.",
    type: "website",
    locale: "pt_BR",
  },
  icons: {
    icon: "/favicon.svg",
  },
};

export const viewport: Viewport = {
  themeColor: "#070b1a",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className={inter.variable}>
      <body className="font-sans">{children}</body>
    </html>
  );
}
