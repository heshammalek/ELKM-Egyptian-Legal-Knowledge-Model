import Link from "next/link";

export default function ChatLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="h-screen flex flex-col bg-black">
      <header className="px-6 py-3 border-b border-gray-800 flex justify-between items-center bg-[#0a0a0a] z-50">
        <div className="font-bold text-lg text-white">LexChain Egypt</div>
        <div className="flex gap-4">
          <Link href="/" className="text-sm text-gray-400 hover:text-white transition">Home</Link>
          <button className="text-sm text-gray-400 hover:text-white transition">Logout</button>
        </div>
      </header>
      <main className="flex-1 overflow-hidden">
        {children}
      </main>
    </div>
  );
}
