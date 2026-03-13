import "./globals.css";

export const metadata = {
  title: "Barg Labs",
  description: "Founder — Barg Labs",
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
