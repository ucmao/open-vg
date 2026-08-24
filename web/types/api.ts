export interface ApiSuccess<T> {
  success: true
  message: string
  data: T
  errors?: never
}

export interface ApiFailure {
  success: false
  message: string
  data?: never
  errors?: Record<string, string>
  status?: number
  statusCode?: number
}

export type ApiResponse<T> = ApiSuccess<T> | ApiFailure

export interface ApiError {
  success?: false
  message: string
  errors?: Record<string, string>
  status?: number
  statusCode?: number
}

export const isApiError = (error: unknown): error is ApiError => {
  return typeof error === 'object' && error !== null && 'message' in error
}
