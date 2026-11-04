import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import AuthButtons from "@/components/AuthButtons";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ELKM Studio",
  description: "Egyptian Legal Knowledge Model",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-black text-white min-h-screen flex flex-col`}>
        {/* النافبار */}
        <header className="w-full px-6 py-4 flex justify-between items-center z-50 fixed top-0 left-0 bg-black/50 backdrop-blur-md border-b border-gray-800">
          <div className="text-xl font-bold tracking-tighter text-white">
            ELKM Studio
          </div>
          <AuthButtons />
        </header>
        
        {/* المحتوى */}
        <main className="flex-1 pt-20"> {/* pt-20 عشان ندي مساحة للنافبار الثابت */}
          {children}
        </main>
      </body>
    </html>
  );
}
