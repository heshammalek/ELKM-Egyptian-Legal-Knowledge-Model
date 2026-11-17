import AuthButtons from "@/components/AuthButtons";

export default function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="w-full px-6 py-4 flex justify-between items-center z-50 absolute top-0 left-0">
        <div className="text-xl font-bold tracking-tighter text-white">ELKM Studio</div>
        <AuthButtons />
      </header>
      <main className="flex-1">{children}</main>
    </div>
  );
}
