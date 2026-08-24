export type JsonPrimitive = string | number | boolean | null
export type JsonValue = JsonPrimitive | JsonObject | JsonValue[]
export interface JsonObject {
  [key: string]: JsonValue
}

export interface PaginatedData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages?: number
}

export type Gender = 'male' | 'female' | 'other' | 'prefer_not_to_say'
export type UserSource = 'REGISTER' | 'GOOGLE' | 'ADMIN_CREATED' | 'IMPORT'

export interface UserSummary {
  id: number
  handle: string
  nickname: string
  avatar_url: string | null
  email?: string
  bio?: string | null
  is_following?: boolean
}

export interface User extends UserSummary {
  email: string
  bio: string | null
  instagram_handle: string | null
  twitter_handle: string | null
  discord_handle: string | null
  location: string | null
  gender: Gender | null
  source: UserSource | null
  handle_updated_at: string | null
  total_credits: number
  is_admin: boolean
  is_active: boolean
  email_verified: boolean
  created_at: string
  followers_count?: number
  following_count?: number
  public_works_count?: number
  total_works_count?: number
  total_views?: number
  total_favorites?: number
  total_likes?: number
  total_remixes?: number
}

export interface LoginResult {
  access_token: string
  token_type: 'bearer' | string
  user: User
}

export type CreditRecordType = 'recharge' | 'gift' | 'consume' | 'refund' | 'admin_adjust' | string

export interface CreditRecord {
  id: number
  user_id: number
  amount: number
  type: CreditRecordType
  description: string | null
  expire_at: string | null
  created_at: string
}

export interface RechargePackage {
  id: number
  name: string
  amount: number
  credits: number
  is_active: boolean
  is_featured: boolean
  tag_text: string | null
  description?: string | null
  order: number
  created_at: string
  updated_at: string
}

export interface PaymentOrder {
  id: number
  user_id: number
  amount_usd: number
  credits: number
  paypal_order_id: string | null
  stripe_session_id?: string | null
  stripe_payment_intent_id?: string | null
  status: string
  created_at: string
  completed_at: string | null
}

export interface Work {
  id: number
  user_id?: number
  type: string
  prompt?: string | null
  model_key?: string
  model_name?: string
  file_url: string | null
  thumbnail_url: string | null
  trailing_image_url?: string | null
  status: string
  error_message?: string | null
  nsfw_status?: string | null
  title: string | null
  description?: string | null
  share_name?: string | null
  short_code?: string | null
  url_slug?: string | null
  canonical_url?: string | null
  like_count: number
  favorite_count: number
  view_count: number
  comment_count?: number
  fork_count?: number
  is_shared?: boolean
  share_status?: string | null
  is_liked?: boolean
  is_favorited?: boolean
  hidden?: boolean
  created_at: string
  user?: UserSummary | null
  params?: JsonObject | null
}

export type WorkMedia = Pick<Work, 'type' | 'thumbnail_url' | 'canonical_url' | 'file_url'> & {
  work_type?: string
}

export interface GenerationCompleteEvent {
  type: 'generation_complete'
  work_id: number
  status: 'success' | 'failed'
  file_url?: string | null
  nsfw_status?: string | null
  error_message?: string | null
}

export interface NotificationEvent {
  type: 'notification'
  message?: string | null
}

export type ServerWebSocketEvent = GenerationCompleteEvent | NotificationEvent
export type ClientWebSocketMessage = JsonObject
