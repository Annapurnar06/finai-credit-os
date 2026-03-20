import { API_BASE } from "./constants";
import type {
  ApplicationDetail,
  ApplicationListItem,
  HealthResponse,
  LLMHealthResponse,
} from "./types";

async function fetcher<T>(url: string): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export function fetchHealth(): Promise<HealthResponse> {
  return fetcher("/api/health");
}

export function fetchLLMHealth(): Promise<LLMHealthResponse> {
  return fetcher("/api/health/llm");
}

export function fetchApplications(): Promise<ApplicationListItem[]> {
  return fetcher("/api/v1/applications");
}

export function fetchApplication(id: string): Promise<ApplicationDetail> {
  return fetcher(`/api/v1/applications/${id}`);
}

export async function resolveHITL(
  applicationId: string,
  data: { approved: boolean; approver: string; rationale: string },
): Promise<{ status: string; decision: string }> {
  const res = await fetch(`${API_BASE}/api/v1/hitl/${applicationId}/resolve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`HITL resolve failed: ${res.status}`);
  return res.json();
}

export const swrFetcher = <T>(url: string): Promise<T> => fetcher<T>(url);
