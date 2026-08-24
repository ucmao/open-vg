import type { Edge, Node } from '@vue-flow/core'

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
  pagination?: {
    total: number
    page?: number
    page_size?: number
    total_pages?: number
  }
}

export type AdminRole = 'super_admin' | 'admin' | 'editor' | 'moderator' | string

export interface AdminUser {
  id: number
  username: string
  email: string
  nickname: string | null
  role: AdminRole
  is_active?: boolean
  last_login?: string | null
  created_at?: string
  user?: UserSummary | null
}

export interface AdminLoginResult {
  access_token: string
  token_type: 'bearer' | string
  user: AdminUser
}

export interface UserSummary {
  id: number
  email: string
  nickname: string
  handle: string
  avatar_url?: string | null
  total_credits?: number | null
  is_active?: boolean
  is_admin?: boolean
}

export interface CreditRecord {
  id: number
  user_id: number
  amount: number
  type: string
  description: string | null
  expire_at: string | null
  created_at: string
  user: UserSummary
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
  stripe_session_id: string | null
  stripe_payment_intent_id: string | null
  status: string
  payment_provider?: string | null
  created_at: string
  completed_at: string | null
  user: UserSummary
}

export interface RechargePromo {
  id: number
  user_id: number | null
  extra_credits_percent: number
  valid_from: string | null
  valid_until: string
  promo_code: string
  promo_url: string
  recharge_url: string
  name: string | null
  status: 'pending' | 'active' | 'expired'
  created_at: string
  user: UserSummary | null
}

export interface EmailPreset {
  key: string
  label: string
}

export interface EmailPreview {
  subject: string
  html_content: string
}

export type WorkflowValue = JsonValue | undefined
export type WorkflowNodeType =
  | 'apiCall'
  | 'promptInput'
  | 'prompt_default_hidden'
  | 'image_default'
  | 'imageInput'
  | 'video_default'
  | 'videoInput'
  | 'media_list_default'
  | 'paramInput'
  | 'userInput'
  | 'input'
  | 'output'

export interface WorkflowParamDefinition {
  type?: string
  label?: string
  description?: string
  default?: WorkflowValue
  required?: boolean
  options?: JsonValue[]
  min?: number
  max?: number
  step?: number
}

export interface WorkflowNodeData extends Record<string, unknown> {
  label?: string
  value?: string | string[] | null
  type?: string
  param_name?: string
  default_value?: WorkflowValue
  api_id?: number | null
  provider?: string | null
  output_type?: string | null
  params_schema?: Record<string, WorkflowParamDefinition> | null
  preset_params?: Record<string, WorkflowValue>
  param_mappings?: Record<string, string>
  params_visibility?: Record<string, boolean>
  param_defaults?: Record<string, WorkflowValue>
  output_params?: Record<string, WorkflowParamDefinition>
  input_params?: Record<string, WorkflowParamDefinition>
}

export type WorkflowNode = Omit<Node<WorkflowNodeData, Record<string, never>, WorkflowNodeType>, 'data' | 'type'> & {
  data: WorkflowNodeData
  type: WorkflowNodeType
}
export interface WorkflowEdgeData {
  visible?: boolean
  paramName?: string
}

export type WorkflowEdge = Edge<WorkflowEdgeData>

export interface BackendWorkflowNode {
  id: string
  type: string
  api_id?: number | null
  position: { x: number; y: number }
  data: WorkflowNodeData
}

export interface BackendWorkflowEdge {
  id: string
  source: string
  target: string
  sourceHandle?: string | null
  targetHandle?: string | null
  type?: string
}

export interface WorkflowRecord {
  id: number
  name: string
  description: string | null
  work_type: string
  nodes: BackendWorkflowNode[]
  edges: BackendWorkflowEdge[]
  viewport: { x: number; y: number; zoom: number } | null
  is_active: boolean
  created_at: string
  updated_at: string
  created_by?: number | null
  created_by_name?: string | null
  created_by_username?: string | null
}

export interface ApiLibraryEntry {
  id: number
  name: string
  provider: string
  output_type: string | null
  params_schema: Record<string, WorkflowParamDefinition> | null
  api_docs_url?: string | null
  provider_model_id?: string | null
  official_price?: number | null
  official_currency?: string | null
  official_unit?: string | null
  notes?: string | null
}
