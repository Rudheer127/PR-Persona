import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function POST(req: Request) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await req.json();
    const prUrl = body.pr_url;

    if (!prUrl) {
      return NextResponse.json({ error: "Missing pr_url" }, { status: 400 });
    }

    // Proxy the request to the Python analysis-service
    const backendUrl = process.env.NEXT_PUBLIC_ANALYSIS_SERVICE_URL || "http://localhost:8000";
    const apiKey = process.env.ANALYSIS_SERVICE_API_KEY || "default-dev-key";

    const response = await fetch(`${backendUrl}/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        pr_url: prUrl,
        user_id: user.id
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        { error: data.detail || "Analysis service error" },
        { status: response.status }
      );
    }

    return NextResponse.json(data);

  } catch (error) {
    console.error("BFF proxy error:", error);
    return NextResponse.json(
      { error: "Internal Server Error" },
      { status: 500 }
    );
  }
}
