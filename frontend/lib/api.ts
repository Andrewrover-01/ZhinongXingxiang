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
