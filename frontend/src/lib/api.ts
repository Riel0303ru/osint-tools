// Centered API client connecting frontend pages to the FastAPI backend

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string;
  error_code: string | null;
}

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const result: ApiResponse<T> = await response.json();
    if (!result.success) {
      throw new Error(result.message || result.error_code || 'API Error');
    }
    return result.data;
  } catch (error: any) {
    console.error(`API request failed at ${endpoint}:`, error);
    throw error;
  }
}

export const api = {
  // Scans
  scanUsername: (username: string, budget = 100, priorityPlatforms: string[] = []) =>
    request<any[]>('/api/scan/username', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, budget, priority_platforms: priorityPlatforms }),
    }),

  scanEmail: (email: string) =>
    request<any[]>('/api/scan/email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    }),

  scanDomain: (domain: string) =>
    request<any[]>('/api/scan/domain', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ domain }),
    }),

  scanPhone: (phone: string) =>
    request<any[]>('/api/scan/phone', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone }),
    }),

  scanIP: (ip: string) =>
    request<any[]>('/api/scan/ip', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ip }),
    }),

  scanCompany: (domain: string) =>
    request<{ results: any[]; report: any }>('/api/scan/company', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ domain }),
    }),

  scanDarkweb: (target: string) =>
    request<any[]>('/api/scan/darkweb', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target }),
    }),

  scanImage: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return request<any[]>('/api/scan/image', {
      method: 'POST',
      body: formData,
    });
  },

  scanDocument: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return request<any[]>('/api/scan/document', {
      method: 'POST',
      body: formData,
    });
  },

  scanVideo: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return request<any[]>('/api/scan/video', {
      method: 'POST',
      body: formData,
    });
  },

  // AI Analysis
  analyzeAI: (prompt: string, targetId?: string, moduleName?: string) =>
    request<any>('/api/ai/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, target_id: targetId, module_name: moduleName }),
    }),

  // Correlation Graph
  getCorrelationGraph: (target?: string) => {
    const queryParam = target ? `?target=${encodeURIComponent(target)}` : '';
    return request<any>(`/api/correlation${queryParam}`);
  },

  // History
  getHistory: (page = 1, limit = 20) =>
    request<{ items: string[]; total: number; page: number; limit: number; pages: number }>(
      `/api/history?page=${page}&limit=${limit}`
    ),

  getTargetHistory: (target: string) =>
    request<string[]>(`/api/history/${encodeURIComponent(target)}`),

  getSnapshot: (target: string, timestamp: string) =>
    request<any[]>(`/api/history/${encodeURIComponent(target)}/${encodeURIComponent(timestamp)}`),

  // Reports
  generateReport: (target: string) =>
    request<{ target: string; report_dir: string; pdf_generated: boolean; download_url: string }>(
      '/api/reports/generate',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target }),
      }
    ),

  getDownloadReportUrl: (target: string) =>
    `${API_BASE_URL}/api/reports/download?target=${encodeURIComponent(target)}`,

  // Dashboard Stats
  getDashboardStats: () => request<any>('/api/dashboard/stats'),
};
