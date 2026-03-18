import { createClient } from "@/lib/supabase/server";
import Link from "next/link";

export default async function DashboardOverview() {
  const supabase = await createClient();
  
  // In a real app, fetch recent PR analyses for the user's orgs
  // For the scaffold, we just show a static CTA and a form to submit a new PR
  
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Overview</h1>
        <p className="mt-2 text-zinc-600 dark:text-zinc-400">
          Analyze a pull request for social health and reviewer qualification.
        </p>
      </div>

      <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <h2 className="text-lg font-semibold">Analyze New PR</h2>
        <form className="mt-4 flex gap-4 max-w-xl" action="/api/analyze" method="post">
          <input
            type="url"
            name="pr_url"
            required
            placeholder="https://github.com/owner/repo/pull/1"
            className="flex-1 rounded-md border border-zinc-300 bg-transparent px-3 py-2 text-sm placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-zinc-900 dark:border-zinc-700 dark:focus:ring-zinc-100"
          />
          <button
            type="submit"
            className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-semibold text-white hover:bg-zinc-800 dark:bg-white dark:text-zinc-900 dark:hover:bg-zinc-200"
          >
            Analyze
          </button>
        </form>
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-4">Recent Analyses</h2>
        <div className="rounded-lg border border-zinc-200 dark:border-zinc-800 overflow-hidden text-sm">
          <table className="w-full text-left">
            <thead className="bg-zinc-50 dark:bg-zinc-900/50">
              <tr>
                <th className="px-4 py-3 font-medium text-zinc-500">PR</th>
                <th className="px-4 py-3 font-medium text-zinc-500">Repository</th>
                <th className="px-4 py-3 font-medium text-zinc-500">Verdict</th>
                <th className="px-4 py-3 font-medium text-zinc-500">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
              <tr>
                <td className="px-4 py-3 text-zinc-500 dark:text-zinc-400">No analyses found.</td>
                <td className="px-4 py-3"></td>
                <td className="px-4 py-3"></td>
                <td className="px-4 py-3"></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
