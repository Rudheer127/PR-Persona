import { notFound } from "next/navigation";

export default function PRAnalysisPage({
  params,
}: {
  params: { owner: string; repo: string; number: string };
}) {
  // Scaffold: this page would fetch the analysis result from Supabase or trigger a new one
  
  return (
    <div className="space-y-8 max-w-5xl">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 text-sm text-zinc-500 mb-2">
            <span>{params.owner} / {params.repo}</span>
            <span>•</span>
            <span>PR #{params.number}</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight">Analysis Results</h1>
        </div>
        
        {/* Placeholder Verdict Badge */}
        <div className="px-4 py-2 rounded-full border border-green-200 bg-green-50 text-green-700 font-semibold dark:bg-green-900/30 dark:border-green-800/50 dark:text-green-400">
          CLEAR TO REVIEW
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Social Health Score summary */}
        <div className="col-span-1 rounded-xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
          <h2 className="text-sm font-medium text-zinc-500 mb-4">Social Health Score</h2>
          <div className="text-5xl font-bold tracking-tighter">92<span className="text-2xl text-zinc-400">/100</span></div>
          {/* Detailed breakdown bars would go here */}
        </div>
        
        {/* Persona Reactions */}
        <div className="col-span-1 md:col-span-2 space-y-4">
          <h2 className="text-lg font-semibold">Persona Reactions</h2>
          <div className="grid grid-cols-2 gap-4">
            {/* Mock Card 1 */}
            <div className="rounded-xl border border-zinc-200 p-4 dark:border-zinc-800">
              <div className="font-semibold flex items-center gap-2">👨‍💻 Junior Dev</div>
              <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">"This PR is clearly described and easy to follow. I feel confident testing it."</p>
            </div>
            {/* Mock Card 2 */}
            <div className="rounded-xl border border-zinc-200 p-4 dark:border-zinc-800">
              <div className="font-semibold flex items-center gap-2">🧙‍♂️ Senior Architect</div>
              <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">"Architecture aligns with our Phase 2 migration path. No red flags."</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
