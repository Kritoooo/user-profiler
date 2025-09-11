import type { Metadata } from "next";
import "./globals.css";
import Navigation from "@/components/Navigation";

export const metadata: Metadata = {
  title: "User Profiler",
  description: "User Digital Footprint Analyzer",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 antialiased">
        <Navigation />
        <main className="max-w-7xl mx-auto py-6 px-4">
          {children}
        </main>
        <footer className="bg-white border-t mt-12">
          <div className="max-w-7xl mx-auto py-4 px-4 text-center text-gray-600">
            <p>&copy; 2024 User Profiler System. Built with Next.js and Python.</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
