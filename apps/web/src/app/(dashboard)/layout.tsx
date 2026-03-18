import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import Link from "next/link";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login");
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-50">
      <header className="sticky top-0 z-40 border-b border-zinc-200 bg-white/80 backdrop-blur-md dark:border-zinc-800 dark:bg-zinc-950/80">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-6">
            <Link href="/" className="text-lg font-bold tracking-tight">
              ReviewSense AI
            </Link>
            <nav className="hidden md:flex gap-4 text-sm font-medium text-zinc-600 dark:text-zinc-400">
              <Link href="/" className="hover:text-zinc-900 dark:hover:text-zinc-50">Dashboard</Link>
              <Link href="/team" className="hover:text-zinc-900 dark:hover:text-zinc-50">Team Health</Link>
              <Link href="/settings" className="hover:text-zinc-900 dark:hover:text-zinc-50">Settings</Link>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-zinc-500">{user.email}</span>
            <form action="/auth/signout" method="post">
              <button className="text-sm font-medium text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-300">
                Sign out
              </button>
            </form>
          </div>
        </div>
      </header>
      <main className="container mx-auto p-4 py-8">
        {children}
      </main>
    </div>
  );
}
