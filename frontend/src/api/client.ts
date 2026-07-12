import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

export default api;

// ── Types ──────────────────────────────────────────────────────────────────

export type EnrichmentStatus = "pending" | "in_progress" | "done" | "failed";
export type LeadType = "email" | "phone";

export interface Lead {
  id: number;
  input_value: string;
  input_type: LeadType;
  enrichment_status: EnrichmentStatus;
  enrichment_score: number;
  name: string | null;
  job_title: string | null;
  linkedin_url: string | null;
  twitter_url: string | null;
  github_url: string | null;
  bio: string | null;
  recent_posts: string[];
  interests: string[];
  company_name: string | null;
  company_industry: string | null;
  company_size: string | null;
  company_website: string | null;
  company_description: string | null;
  recent_news: string[];
  enrichment_sources: string[];
  raw_analysis: Record<string, { status: string; data: unknown; note?: string }>;
  error_message: string | null;
  generated_email: string | null;
  generated_call_script: string | null;
  generated_linkedin_msg: string | null;
}

export interface GenerationRequest {
  product_name: string;
  product_description: string;
  key_value_props: string[];
  target_pain_point: string;
  output_types: string[];
}

export interface GenerationResponse {
  lead_id: number;
  email: string | null;
  call_script: string | null;
  linkedin_msg: string | null;
}

// ── API calls ──────────────────────────────────────────────────────────────

export const leadsApi = {
  addSingle: async (value: string): Promise<Lead> => {
    const res = await api.post<Lead>("/leads/single", { value });
    return res.data;
  },

  upload: async (file: File): Promise<Lead[]> => {
    const form = new FormData();
    form.append("file", file);
    const res = await api.post<Lead[]>("/leads/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
  },

  list: async (): Promise<Lead[]> => {
    const res = await api.get<Lead[]>("/leads");
    return res.data;
  },

  get: async (id: number): Promise<Lead> => {
    const res = await api.get<Lead>(`/leads/${id}`);
    return res.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/leads/${id}`);
  },

  deleteAll: async (): Promise<void> => {
    await api.delete("/leads");
  },
};

export const enrichmentApi = {
  enrich: async (leadId: number): Promise<void> => {
    await api.post(`/enrichment/${leadId}`);
  },

  enrichAll: async (): Promise<void> => {
    await api.post("/enrichment/batch/all");
  },
};

export const generationApi = {
  generate: async (
    leadId: number,
    req: GenerationRequest
  ): Promise<GenerationResponse> => {
    const res = await api.post<GenerationResponse>(
      `/generation/${leadId}`,
      req
    );
    return res.data;
  },
};
