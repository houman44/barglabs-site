import "./globals.css";

export const metadata = {
  title: "Barg Labs",
  description:
    "Barg Labs builds Alfred, Egbert, and Therasyn — three applied AI products for studios, markets, and regulated health systems.",
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
