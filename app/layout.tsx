import "./globals.css";

const themeScript = `
  (() => {
    try {
      const savedTheme = window.localStorage.getItem("barg-theme");
      const systemTheme = window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
      document.documentElement.dataset.theme =
        savedTheme === "dark" || savedTheme === "light" ? savedTheme : systemTheme;
    } catch {
      document.documentElement.dataset.theme = "dark";
    }
  })();
`;

export const metadata = {
  metadataBase: new URL("https://barglabs.ai"),
  title: "Barg Labs — Built for consequential AI",
  description:
    "Barg Labs builds evidence, governance, and execution infrastructure for consequential AI operating in code, companies, markets, and clinical systems.",
  icons: {
    icon: [
      { url: "/barg-icon.svg", type: "image/svg+xml" },
      { url: "/barg-icon-mark.png", type: "image/png" },
    ],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
