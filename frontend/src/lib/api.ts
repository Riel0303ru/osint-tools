// Centered API client connecting frontend pages to the FastAPI backend
import { useUIStore } from '../store/appStore';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string;
  error_code: string | null;
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  let controllerCreated = false;
  // If it is a scan endpoint, automatically trigger the warning toast and manage the AbortController
  if (endpoint.startsWith('/api/scan') || endpoint.startsWith('/api/ai/analyze')) {
    useUIStore.getState().showWarningToast(
      'Harap jangan meninggalkan halaman ini selama proses pemindaian agar koneksi tidak terputus.'
    );

    if (!options.signal) {
      // Abort any existing active request first
      const activeCtrl = useUIStore.getState().activeAbortController;
      if (activeCtrl) {
        activeCtrl.abort();
      }

      const newCtrl = new AbortController();
      useUIStore.getState().setActiveAbortController(newCtrl);
      options.signal = newCtrl.signal;
      controllerCreated = true;
    }
  }

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
    if (error.name === 'AbortError') {
      console.warn(`API request at ${endpoint} was aborted.`);
    } else {
      console.error(`API request failed at ${endpoint}:`, error);
    }
    throw error;
  } finally {
    if (controllerCreated) {
      const activeCtrl = useUIStore.getState().activeAbortController;
      if (activeCtrl && activeCtrl.signal === options.signal) {
        useUIStore.getState().setActiveAbortController(null);
      }
      useUIStore.getState().hideWarningToast();
    }
  }
}

export const api = {
  // Scans
  scanUsername: (username: string, budget = 100, priorityPlatforms: string[] = [], signal?: AbortSignal) =>
    request<any[]>('/api/scan/username', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, budget, priority_platforms: priorityPlatforms }),
      signal,
    }),

  scanEmail: (email: string, signal?: AbortSignal) =>
    request<any[]>('/api/scan/email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
      signal,
    }),

  scanDomain: (domain: string, signal?: AbortSignal) =>
    request<any[]>('/api/scan/domain', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ domain }),
      signal,
    }),

  scanPhone: (phone: string, signal?: AbortSignal) =>
    request<any[]>('/api/scan/phone', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone }),
      signal,
    }),

  scanIP: (ip: string, signal?: AbortSignal) =>
    request<any[]>('/api/scan/ip', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ip }),
      signal,
    }),

  scanCompany: (domain: string, signal?: AbortSignal) =>
    request<{ results: any[]; report: any }>('/api/scan/company', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ domain }),
      signal,
    }),

  scanDarkweb: (target: string, signal?: AbortSignal) =>
    request<any[]>('/api/scan/darkweb', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target }),
      signal,
    }),

  scanImage: (file: File, signal?: AbortSignal) => {
    const formData = new FormData();
    formData.append('file', file);
    return request<any[]>('/api/scan/image', {
      method: 'POST',
      body: formData,
      signal,
    });
  },

  scanDocument: (file: File, signal?: AbortSignal) => {
    const formData = new FormData();
    formData.append('file', file);
    return request<any[]>('/api/scan/document', {
      method: 'POST',
      body: formData,
      signal,
    });
  },

  scanVideo: (file: File, signal?: AbortSignal) => {
    const formData = new FormData();
    formData.append('file', file);
    return request<any[]>('/api/scan/video', {
      method: 'POST',
      body: formData,
      signal,
    });
  },

  // AI Analysis
  analyzeAI: (prompt: string, targetId?: string, moduleName?: string, signal?: AbortSignal) =>
    request<any>('/api/ai/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, target_id: targetId, module_name: moduleName }),
      signal,
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
