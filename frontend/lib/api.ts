import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { "Content-Type": "application/json" },
});

// Attach JWT token to every request
apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Auto-redirect on 401
apiClient.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ─── Auth ───────────────────────────────────────────────────────────────────

export interface LoginPayload {
  username: string;
  password: string;
}

export interface RegisterPayload {
  username: string;
  phone: string;
  password: string;
  real_name?: string;
  province?: string;
  city?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  id: string;
  username: string;
  phone: string;
  real_name?: string;
  province?: string;
  city?: string;
  role: string;
  avatar_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export const authApi = {
  login: (data: LoginPayload) =>
    apiClient.post<TokenResponse>("/auth/login", data).then((r) => r.data),
  register: (data: RegisterPayload) =>
    apiClient.post<UserResponse>("/auth/register", data).then((r) => r.data),
  me: () => apiClient.get<UserResponse>("/auth/me").then((r) => r.data),
};

// ─── Farmland ───────────────────────────────────────────────────────────────

export interface FarmlandResponse {
  id: string;
  owner_id: string;
  name: string;
  area: string;
  location?: string;
  latitude?: string;
  longitude?: string;
  soil_type?: string;
  crop_type?: string;
  crop_stage?: string;
  sowing_date?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface FarmlandPayload {
  name: string;
  area: string;
  location?: string;
  latitude?: string;
  longitude?: string;
  soil_type?: string;
  crop_type?: string;
  crop_stage?: string;
  sowing_date?: string;
  notes?: string;
}

export const farmlandApi = {
  list: () =>
    apiClient.get<FarmlandResponse[]>("/farmlands/").then((r) => r.data),
  get: (id: string) =>
    apiClient.get<FarmlandResponse>(`/farmlands/${id}`).then((r) => r.data),
  create: (data: FarmlandPayload) =>
    apiClient.post<FarmlandResponse>("/farmlands/", data).then((r) => r.data),
  update: (id: string, data: Partial<FarmlandPayload>) =>
    apiClient.put<FarmlandResponse>(`/farmlands/${id}`, data).then((r) => r.data),
  delete: (id: string) => apiClient.delete(`/farmlands/${id}`),
};

// ─── Upload ──────────────────────────────────────────────────────────────────

export interface UploadResponse {
  url: string;
  filename: string;
  content_type: string;
  size: number;
}

export const uploadApi = {
  upload: (file: File): Promise<UploadResponse> => {
    const form = new FormData();
    form.append("file", file);
    return apiClient
      .post<UploadResponse>("/upload/image", form, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data);
  },
};

// ─── AI Doctor ───────────────────────────────────────────────────────────────

export interface RAGSourceOut {
  id: string;
  title: string;
  category: string;
  snippet: string;
  distance: number;
}

export interface DiagnoseRequest {
  image_url: string;
  description?: string;
  crop_type?: string;
  farmland_id?: string;
}

export interface DiagnoseResponse {
  record_id: string;
  diagnosis: string;
  severity?: string;
  confidence?: number;
  treatment_plan: string;
  medicine_suggest?: string;
  sources: RAGSourceOut[];
  llm_model: string;
}

export interface DiagnoseRecord extends DiagnoseResponse {
  image_url: string;
  description?: string;
  crop_type?: string;
  created_at: string;
}

export const aiDoctorApi = {
  diagnose: (data: DiagnoseRequest) =>
    apiClient.post<DiagnoseResponse>("/ai-doctor/diagnose", data).then((r) => r.data),
  records: (skip = 0, limit = 20) =>
    apiClient
      .get<DiagnoseRecord[]>("/ai-doctor/records", { params: { skip, limit } })
      .then((r) => r.data),
  record: (id: string) =>
    apiClient.get<DiagnoseRecord>(`/ai-doctor/records/${id}`).then((r) => r.data),
};

/** Open an SSE stream for AI Doctor streaming diagnosis. Returns a Reader. */
export function streamDiagnose(
  data: DiagnoseRequest,
  token: string
): ReadableStreamDefaultReader<Uint8Array> {
  const ctrl = new AbortController();
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const resp = fetch(`${base}/api/v1/ai-doctor/diagnose/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
    signal: ctrl.signal,
  });
  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      try {
        const res = await resp;
        if (!res.body) {
          controller.error(new Error("Empty response body"));
          return;
        }
        const reader = res.body.getReader();
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          controller.enqueue(value);
        }
        controller.close();
      } catch (e) {
        controller.error(e);
      }
    },
    cancel() {
      ctrl.abort();
    },
  });
  return stream.getReader();
}

// ─── Policy ──────────────────────────────────────────────────────────────────

export interface PolicySessionSummary {
  session_id: string;
  message_count: number;
  last_message: string;
  last_at: string;
}

export interface PolicyMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  rag_sources?: RAGSourceOut[];
  created_at: string;
}

export const policyApi = {
  sessions: () =>
    apiClient.get<PolicySessionSummary[]>("/policy/sessions").then((r) => r.data),
  sessionMessages: (sessionId: string) =>
    apiClient.get<PolicyMessage[]>(`/policy/sessions/${sessionId}`).then((r) => r.data),
  deleteSession: (sessionId: string) =>
    apiClient.delete(`/policy/sessions/${sessionId}`),
};

/** Open an SSE stream for Policy chat. Returns a ReadableStreamDefaultReader. */
export function streamPolicyChat(
  sessionId: string,
  message: string,
  token: string
): ReadableStreamDefaultReader<Uint8Array> {
  const ctrl = new AbortController();
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      try {
        const res = await fetch(`${base}/api/v1/policy/chat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ session_id: sessionId, message }),
          signal: ctrl.signal,
        });
        if (!res.body) {
          controller.error(new Error("Empty response body"));
          return;
        }
        const reader = res.body.getReader();
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          controller.enqueue(value);
        }
        controller.close();
      } catch (e) {
        controller.error(e);
      }
    },
    cancel() {
      ctrl.abort();
    },
  });
  return stream.getReader();
}
