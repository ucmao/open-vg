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
}

export type ApiResponse<T> = ApiSuccess<T> | ApiFailure
