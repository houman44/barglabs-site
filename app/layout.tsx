import "./globals.css";

export const metadata = {
  metadataBase: new URL("https://barglabs.ai"),
  title: "Barg Labs",
  description:
    "Barg Labs is an AI-native studio building Alfred, Cejel, Egbert, and Therasyn — applied AI products for studios, code trust, markets, and regulated health systems.",
  icons: {
    icon: [
      { url: "/barg-icon.svg", type: "image/svg+xml" },
      { url: "/barg-icon.png", type: "image/png" },
    ],
  },
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
