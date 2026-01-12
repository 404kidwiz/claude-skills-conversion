import * as fs from 'fs';
import * as path from 'path';

interface APIConfig {
  baseURL: string;
  timeout: number;
  retries: number;
  headers: Record<string, string>;
}

class APIClientGenerator {
  private config: APIConfig;

  constructor(config: APIConfig) {
    this.config = config;
  }

  generate(outputDir: string, clientType: 'axios' | 'fetch'): void {
    const clientDir = path.join(outputDir, 'api');
    fs.mkdirSync(clientDir, { recursive: true });

    if (clientType === 'axios') {
      this.generateAxiosClient(clientDir);
    } else {
      this.generateFetchClient(clientDir);
    }

    this.generateTypes(clientDir);
    this.generateEndpoints(clientDir);
    this.generateIndex(clientDir);

    console.log(`✓ API client (${clientType}) generated`);
  }

  private generateAxiosClient(dir: string): void {
    const content = `import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

class APIClient {
  private client: AxiosInstance;

  constructor(config: APIConfig) {
    this.client = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout,
      headers: config.headers,
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = \`Bearer \${token}\`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.patch<T>(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }
}

const apiClient = new APIClient({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:3000/api',
  timeout: 10000,
  retries: 3,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;
`;

    fs.writeFileSync(path.join(dir, 'client.ts'), content);
  }

  private generateFetchClient(dir: string): void {
    const content = `class APIClient {
  private baseURL: string;
  private timeout: number;

  constructor(config: APIConfig) {
    this.baseURL = config.baseURL;
    this.timeout = config.timeout;
  }

  private async request<T>(
    url: string,
    options: RequestInit = {}
  ): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    const token = localStorage.getItem('token');
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers.Authorization = \`Bearer \${token}\`;
    }

    try {
      const response = await fetch(\`\${this.baseURL}\${url}\`, {
        ...options,
        headers,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(\`HTTP error! status: \${response.status}\`);
      }

      return response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  async get<T>(url: string): Promise<T> {
    return this.request<T>(url, { method: 'GET' });
  }

  async post<T>(url: string, data?: any): Promise<T> {
    return this.request<T>(url, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put<T>(url: string, data?: any): Promise<T> {
    return this.request<T>(url, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async patch<T>(url: string, data?: any): Promise<T> {
    return this.request<T>(url, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async delete<T>(url: string): Promise<T> {
    return this.request<T>(url, { method: 'DELETE' });
  }
}

const apiClient = new APIClient({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:3000/api',
  timeout: 10000,
  retries: 3,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;
`;

    fs.writeFileSync(path.join(dir, 'client.ts'), content);
  }

  private generateTypes(dir: string): void {
    const content = `// API Response Types
export interface APIResponse<T> {
  data: T;
  message?: string;
  meta?: {
    page?: number;
    pageSize?: number;
    total?: number;
  };
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// User Types
export interface User {
  id: number;
  email: string;
  name: string;
  avatar?: string;
  createdAt: string;
  updatedAt: string;
}

export interface UserCreate {
  email: string;
  name: string;
  password: string;
}

export interface UserUpdate {
  email?: string;
  name?: string;
}

// API Error Types
export interface APIError {
  message: string;
  code?: string;
  details?: any;
}
`;

    fs.writeFileSync(path.join(dir, 'types.ts'), content);
  }

  private generateEndpoints(dir: string): void {
    const content = `import apiClient from './client';
import type { User, UserCreate, UserUpdate, PaginatedResponse, APIResponse } from './types';

export const userAPI = {
  getUsers: (page = 1, pageSize = 20): Promise<PaginatedResponse<User>> =>
    apiClient.get<PaginatedResponse<User>>(\`/users?page=\${page}&pageSize=\${pageSize}\`),

  getUser: (id: number): Promise<APIResponse<User>> =>
    apiClient.get<APIResponse<User>>(\`/users/\${id}\`),

  createUser: (data: UserCreate): Promise<APIResponse<User>> =>
    apiClient.post<APIResponse<User>>('/users', data),

  updateUser: (id: number, data: UserUpdate): Promise<APIResponse<User>> =>
    apiClient.put<APIResponse<User>>(\`/users/\${id}\`, data),

  deleteUser: (id: number): Promise<void> =>
    apiClient.delete<void>(\`/users/\${id}\`),
};
`;

    fs.writeFileSync(path.join(dir, 'endpoints.ts'), content);
  }

  private generateIndex(dir: string): void {
    const content = `export { default as apiClient } from './client';
export * from './types';
export * from './endpoints';
`;

    fs.writeFileSync(path.join(dir, 'index.ts'), content);
  }
}

// CLI
const args = process.argv.slice(2);
const clientType = args[0] || 'axios';

const config: APIConfig = {
  baseURL: 'http://localhost:3000/api',
  timeout: 10000,
  retries: 3,
  headers: {
    'Content-Type': 'application/json',
  },
};

const generator = new APIClientGenerator(config);
generator.generate('./src', clientType as any);
