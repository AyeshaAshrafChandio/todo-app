// Generic API types

export interface ApiError {
  error: string;
  detail: string;
}

export interface ApiResponse<T> {
  data: T;
  error?: ApiError;
}
