import { env } from "./env";

export interface ApiErrorResponse {
  error_code: string;
  message: string;
  details?: unknown;
  request_id?: string;
}

export class ApiError extends Error {
  public status: number;
  public data: ApiErrorResponse;

  constructor(status: number, data: ApiErrorResponse) {
    super(data.message || "An unexpected API error occurred");
    this.status = status;
    this.data = data;
    this.name = "ApiError";
  }
}

interface FetchOptions extends RequestInit {
  timeout?: number;
}

export async function fetchApi<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
  const { timeout = 10000, ...customConfig } = options;
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);

  const url = `${env.NEXT_PUBLIC_API_URL}${endpoint}`;
  
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...customConfig.headers,
  };

  const config: RequestInit = {
    ...customConfig,
    headers,
    signal: customConfig.signal || controller.signal,
  };

  try {
    const response = await fetch(url, config);
    clearTimeout(id);
    
    if (!response.ok) {
      let errorData: ApiErrorResponse;
      try {
        errorData = await response.json();
      } catch {
        errorData = {
          error_code: "UNKNOWN_ERROR",
          message: response.statusText || "Unknown Error",
        };
      }
      throw new ApiError(response.status, errorData);
    }
    
    if (response.status === 204) {
      return {} as T;
    }
    
    return await response.json();
  } catch (error: unknown) {
    clearTimeout(id);
    if (error instanceof Error && error.name === "AbortError") {
      throw new ApiError(408, {
        error_code: "TIMEOUT",
        message: "Request timed out",
      });
    }
    throw error;
  }
}
