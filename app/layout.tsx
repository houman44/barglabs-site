import "./globals.css";

export const metadata = {
  title: "Barg Labs",
  description:
    "Barg Labs builds Alfred, Egbert, Therasyn, Sara, and Edwy — five applied AI products for studios, markets, regulated health systems, the web, and AI literacy.",
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
