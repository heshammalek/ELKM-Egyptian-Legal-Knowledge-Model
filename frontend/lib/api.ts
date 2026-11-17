import type { SearchResponse } from "../types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

export async function searchLegal(question: string): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE_URL}/search/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return (await response.json()) as SearchResponse;
}
