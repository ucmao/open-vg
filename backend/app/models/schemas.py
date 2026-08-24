"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, Field, validator, model_validator, field_validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


# Authentication schemas
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    nickname: str = Field(..., min_length=2, max_length=50)
    verification_code: str = Field(..., min_length=6, max_length=6)
    invite_code: Optional[str] = Field(None, max_length=20, description="Optional invitation code")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleCallbackRequest(BaseModel):
    code: str = Field(..., description="Authorization code from Google OAuth")
    invite_code: Optional[str] = Field(None, description="Optional invitation code for referral rewards")


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class SendCodeRequest(BaseModel):
    email: EmailStr


class VerifyCodeRequest(BaseModel):
    email: EmailStr
    verification_code: str = Field(..., min_length=6, max_length=6)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    verification_code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=6, max_length=100)


# User schemas
class UserResponse(BaseModel):
    id: int
    handle: str
    email: str
    nickname: str
    avatar_url: Optional[str]
    bio: Optional[str]
    instagram_handle: Optional[str] = None
    twitter_handle: Optional[str] = None
    discord_handle: Optional[str] = None
    location: Optional[str] = None
    gender: Optional[str] = None
    total_credits: int
    is_admin: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }


class UpdateProfileRequest(BaseModel):
    nickname: Optional[str] = Field(None, min_length=2, max_length=50)
    handle: Optional[str] = Field(None, min_length=6, max_length=15, pattern="^[a-zA-Z][a-zA-Z0-9_]*$")
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    instagram_handle: Optional[str] = Field(None, max_length=100)
    twitter_handle: Optional[str] = Field(None, max_length=100)
    discord_handle: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=80)
    gender: Optional[Literal["male", "female", "other", "prefer_not_to_say"]] = None


# Work schemas
class GenerateRequest(BaseModel):
    type: str = Field(..., description="Generation type (level 1 category name from generate-pages)")
    model_name: str
    params: dict

    model_config = {
        "protected_namespaces": ()
    }


class WorkResponse(BaseModel):
    id: int
    user_id: int
    parent_id: Optional[int] = None
    type: str
    prompt: str
    negative_prompt: Optional[str] = ""
    prompt_id: Optional[str] = None
    source: str = "UGC"
    model_key: str
    model_name: str
    model_version: Optional[str] = ""
    params: Optional[dict]
    tags: List[str] = []
    file_url: Optional[str]
    thumbnail_url: Optional[str]
    status: str
    is_shared: bool
    share_status: Optional[str]
    share_name: Optional[str]
    title: Optional[str]
    description: Optional[str]
    storage_key: Optional[str]
    canonical_url: Optional[str]
    short_code: Optional[str]
    category: Optional[str]
    like_count: int
    favorite_count: int
    view_count: int
    comment_count: int = 0
    fork_count: int = 0
    created_at: datetime
    completed_at: Optional[datetime]
    user: Optional[dict] = None

    model_config = {
        "from_attributes": True,
        "protected_namespaces": (),
        "populate_by_name": True
    }


class SubmitShareRequest(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    category: str = Field(..., max_length=100)  # Supports hierarchical categories: "Level1" or "Level1|Level2"


class UpdateWorkRequest(BaseModel):
    share_name: Optional[str] = Field(None, min_length=1, max_length=200)
    title: Optional[str] = Field(None, min_length=1, max_length=200)


# Comment schemas
class CreateCommentRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    parent_id: Optional[int] = Field(None, description="Parent comment ID for replies")


class CommentResponse(BaseModel):
    id: int
    work_id: int
    user_id: int
    parent_id: Optional[int] = None
    content: str
    created_at: datetime
    updated_at: datetime
    user: Optional[dict] = None
    replies: Optional[list] = None
    reply_count: Optional[int] = 0

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }


# Credit schemas
class CreditRecordResponse(BaseModel):
    id: int
    user_id: int
    amount: int
    type: str
    description: Optional[str]
    expire_at: Optional[datetime]
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }


# Payment schemas
class CreatePaymentRequest(BaseModel):
    credits: int = Field(..., gt=0)
    provider: Optional[str] = Field("paypal", pattern="^(paypal|stripe)$")
    promo_code: Optional[str] = Field(None, max_length=64, description="Promo code for extra credits %")
    

class PaymentOrderResponse(BaseModel):
    id: int
    user_id: int
    amount_usd: float
    credits: int
    paypal_order_id: Optional[str]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }


# Admin schemas
class ReviewActionRequest(BaseModel):
    action: str = Field(..., pattern="^(approve|reject)$")
    reject_reason: Optional[str] = Field(None, max_length=500)


# Blog schemas
class BlogCategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }


class CreateBlogCategoryRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    slug: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)


class UpdateBlogCategoryRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    slug: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)


class BlogTagResponse(BaseModel):
    id: int
    name: str
    slug: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }


class CreateBlogTagRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    slug: str = Field(..., min_length=1, max_length=50)


class UpdateBlogTagRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    slug: Optional[str] = Field(None, min_length=1, max_length=50)


class CreateBlogPostRequest(BaseModel):
    slug: str = Field(..., min_length=1, max_length=200)
    title: str = Field(..., min_length=1, max_length=200)
    excerpt: Optional[str] = Field(None, max_length=500)
    content: str = Field(..., min_length=1)
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None, max_length=500)
    meta_keywords: Optional[str] = Field(None, max_length=500)
    og_image: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    category_id: Optional[int] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    status: str = Field(default="draft", pattern="^(draft|published|archived)$")
    is_featured: bool = Field(default=False)
    sort_order: int = Field(default=0, ge=0)
    published_at: Optional[datetime] = None
    author_id: Optional[int] = Field(None, description="Author user ID. If not provided, uses current admin.")

    model_config = {
        "protected_namespaces": ()
    }


class UpdateBlogPostRequest(BaseModel):
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    excerpt: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None, max_length=500)
    meta_keywords: Optional[str] = Field(None, max_length=500)
    og_image: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = Field(None, pattern="^(draft|published|archived)$")
    is_featured: Optional[bool] = None
    sort_order: Optional[int] = Field(None, ge=0)
    published_at: Optional[datetime] = None
    author_id: Optional[int] = Field(None, description="Author user ID. If not provided, keeps current author.")

    model_config = {
        "protected_namespaces": ()
    }


# API Library schemas
class CreateAPILibraryRequest(BaseModel):
    api_key: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    task_type: Optional[str] = Field(None, max_length=100)
    output_type: Optional[str] = Field(None, pattern="^(image|video|text)$", description="Output type: image, video, or text")
    provider: str = Field(..., pattern="^(siliconflow|replicate|gemini|a2e)$")
    provider_model_id: str = Field(..., max_length=200)
    params_schema: Dict[str, Any] = Field(default_factory=dict)
    api_docs_url: Optional[str] = Field(None, max_length=500)
    official_price: Optional[float] = None
    official_currency: Optional[str] = "USD"
    official_unit: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = Field(default=True)


class UpdateAPILibraryRequest(BaseModel):
    api_key: Optional[str] = Field(None, min_length=1, max_length=100)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    task_type: Optional[str] = Field(None, max_length=100)
    output_type: Optional[str] = Field(None, pattern="^(image|video|text)$", description="Output type: image, video, or text")
    provider: Optional[str] = Field(None, pattern="^(siliconflow|replicate|gemini|a2e)$")
    provider_model_id: Optional[str] = Field(None, max_length=200)
    params_schema: Optional[Dict[str, Any]] = None
    api_docs_url: Optional[str] = Field(None, max_length=500)
    official_price: Optional[float] = None
    official_currency: Optional[str] = None
    official_unit: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


# Generation Model schemas
class ExampleGalleryItem(BaseModel):
    """Example gallery item schema."""
    before_url: Optional[str] = Field(None, max_length=500, description="Before effect URL (optional)")
    before_prompt: Optional[str] = Field(None, max_length=5000, description="Before effect prompt text (optional)")
    after_url: str = Field(..., max_length=500, description="After effect URL (required)")
    after_prompt: Optional[str] = Field(None, max_length=5000, description="After effect prompt text (optional)")
    notes: Optional[str] = Field(None, max_length=500, description="Example notes (optional)")


class CreateGenerationModelRequest(BaseModel):
    workflow_id: int = Field(..., gt=0, description="Workflow ID (required, workflow-based system only)")
    model_key: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    # work_type  generate_pages
    work_type: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    cost: int = Field(..., ge=0)
    is_active: bool = Field(default=True)
    is_featured: bool = Field(default=False, description="Whether this model is featured/")
    sort_order: int = Field(default=0, ge=0)
    params_config: Dict[str, Any] = Field(default_factory=dict, description="Parameter overrides")
    model_level: Optional[str] = Field(None, description="Model level (e.g., basic, pro)")
    category: Optional[str] = Field(None, description="Model category (e.g., quality, portrait)")
    notes: Optional[str] = None
    example_galleries: Optional[List[ExampleGalleryItem]] = Field(default_factory=list, description="Example galleries")
    icon_url: Optional[str] = Field(None, max_length=500, description="Icon URL shown before model name")
    badge: Optional[str] = Field(None, description="Badge: free, new, hot, beta, 50off, pro, limited, verified, top, best")

    @field_validator("badge")
    @classmethod
    def normalize_badge(cls, v: Optional[str]) -> Optional[str]:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        allowed = ("free", "new", "hot", "beta", "50off", "pro", "limited", "verified", "top", "best")
        if v not in allowed:
            raise ValueError(f"badge must be one of: {', '.join(allowed)}")
        return v

    @field_validator("icon_url")
    @classmethod
    def normalize_icon_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        return v.strip()[:500]


class UpdateGenerationModelRequest(BaseModel):
    workflow_id: Optional[int] = Field(None, gt=0, description="Workflow ID (workflow-based system only)")
    model_key: Optional[str] = Field(None, min_length=1, max_length=100)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    # work_type  generate_pages
    work_type: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    cost: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = Field(None, description="Whether this model is featured/")
    sort_order: Optional[int] = Field(None, ge=0)
    params_config: Optional[Dict[str, Any]] = None
    model_level: Optional[str] = Field(None, description="Model level (e.g., basic, pro)")
    category: Optional[str] = Field(None, description="Model category (e.g., quality, portrait)")
    notes: Optional[str] = None
    example_galleries: Optional[List[ExampleGalleryItem]] = Field(None, description="Example galleries")
    icon_url: Optional[str] = Field(None, max_length=500, description="Icon URL shown before model name")
    badge: Optional[str] = Field(None, description="Badge: free, new, hot, beta, 50off, pro, limited, verified, top, best")

    @field_validator("badge")
    @classmethod
    def normalize_badge(cls, v: Optional[str]) -> Optional[str]:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        allowed = ("free", "new", "hot", "beta", "50off", "pro", "limited", "verified", "top", "best")
        if v not in allowed:
            raise ValueError(f"badge must be one of: {', '.join(allowed)}")
        return v

    @field_validator("icon_url")
    @classmethod
    def normalize_icon_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        return v.strip()[:500]


# Upload schemas
class UploadResponse(BaseModel):
    url: str
    presigned_url: Optional[str] = None


# Topic schemas (topic =  or  when generation_model_id is set)
class TopicResponse(BaseModel):
    id: int
    slug: str
    title: str
    excerpt: Optional[str]
    content: Optional[str]
    meta_title: Optional[str]
    meta_description: Optional[str]
    category: Optional[str]
    category_id: Optional[int]
    category_name: Optional[str]
    tags: List[str]
    featured_image: Optional[str]
    icon: Optional[str]
    config: Dict[str, Any]
    generation_model_id: Optional[int] = None
    status: str
    is_featured: bool
    view_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }


class CreateTopicRequest(BaseModel):
    slug: str = Field(..., min_length=1, max_length=200)
    title: str = Field(..., min_length=1, max_length=200)
    excerpt: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None, max_length=500)
    meta_keywords: Optional[str] = Field(None, max_length=500)
    og_image: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    category_id: Optional[int] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    featured_image: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=100)
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    generation_model_id: Optional[int] = None
    status: str = Field(default="draft", pattern="^(draft|published|archived)$")
    is_featured: bool = Field(default=False)
    sort_order: int = Field(default=0, ge=0)
    published_at: Optional[datetime] = None


class UpdateTopicRequest(BaseModel):
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    excerpt: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None, max_length=500)
    meta_keywords: Optional[str] = Field(None, max_length=500)
    og_image: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None
    featured_image: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=100)
    config: Optional[Dict[str, Any]] = None
    generation_model_id: Optional[int] = None
    status: Optional[str] = Field(None, pattern="^(draft|published|archived)$")
    is_featured: Optional[bool] = None
    sort_order: Optional[int] = Field(None, ge=0)
    published_at: Optional[datetime] = None


# Model page schemas (landing page for generation model, /magic/:slug)
class CreateModelPageRequest(BaseModel):
    slug: str = Field(..., min_length=1, max_length=200)
    generation_model_id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=200)
    excerpt: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None, max_length=500)
    meta_keywords: Optional[str] = Field(None, max_length=500)
    og_image: Optional[str] = None
    featured_image: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=100)
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    status: str = Field(default="draft", pattern="^(draft|published|archived)$")
    sort_order: int = Field(default=0, ge=0)
    published_at: Optional[datetime] = None


class UpdateModelPageRequest(BaseModel):
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    generation_model_id: Optional[int] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    excerpt: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None, max_length=500)
    meta_keywords: Optional[str] = Field(None, max_length=500)
    og_image: Optional[str] = None
    featured_image: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=100)
    config: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, pattern="^(draft|published|archived)$")
    sort_order: Optional[int] = Field(None, ge=0)
    published_at: Optional[datetime] = None


# SEO Configuration Schemas
class SeoConfigRequest(BaseModel):
    config_key: str = Field(..., min_length=1, max_length=100)
    config_value: Optional[str] = None
    is_enabled: bool = True
    description: Optional[str] = None


class UpdateSeoConfigRequest(BaseModel):
    config_value: Optional[str] = None
    is_enabled: Optional[bool] = None
    description: Optional[str] = None


# Page SEO Schemas
class PageSeoResponse(BaseModel):
    id: int
    page_name: str
    page_path: str
    title: Optional[str]
    description: Optional[str]
    keywords: Optional[str]
    is_enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }


class CreatePageSeoRequest(BaseModel):
    page_name: str = Field(..., min_length=1, max_length=50)
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    keywords: Optional[str] = None


class UpdatePageSeoRequest(BaseModel):
    page_path: Optional[str] = Field(None, max_length=200)
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    keywords: Optional[str] = None
    is_enabled: Optional[bool] = None


# System Configuration Schemas
class SystemConfigRequest(BaseModel):
    config_group: str = Field(default="general", max_length=50)
    config_key: str = Field(..., min_length=1, max_length=100)
    config_value: Optional[str] = None
    is_encrypted: bool = False
    description: Optional[str] = None

class UpdateSystemConfigRequest(BaseModel):
    config_group: Optional[str] = Field(None, max_length=50)
    config_value: Optional[str] = None
    is_encrypted: Optional[bool] = None
    description: Optional[str] = None


# Recharge Package Schemas
class RechargePackageResponse(BaseModel):
    id: int
    name: str
    amount: float
    credits: int
    is_active: bool
    is_featured: bool
    tag_text: Optional[str]
    order: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }


class CreateRechargePackageRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    credits: int = Field(..., gt=0)
    is_active: bool = True
    is_featured: bool = False
    tag_text: Optional[str] = Field(None, max_length=50)
    order: int = 0
    description: Optional[str] = Field(None, description="Rich text (HTML) description for recharge card")


class UpdateRechargePackageRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    amount: Optional[float] = Field(None, gt=0)
    credits: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    tag_text: Optional[str] = Field(None, max_length=50)
    order: Optional[int] = None
    description: Optional[str] = Field(None, description="Rich text (HTML) description for recharge card")


class ManualAdjustCreditRequest(BaseModel):
    user_id: int = Field(..., gt=0, description="User ID")
    amount: int = Field(..., description="Credit amount (positive for add, negative for deduct)")
    description: str = Field(..., min_length=1, max_length=500, description="Reason for adjustment")


class CreateRechargePromoRequest(BaseModel):
    user_id: Optional[int] = Field(None, gt=0, description="User ID for this promo; omit or null = ")
    extra_credits_percent: float = Field(..., ge=0, le=100, description="Extra credits % (e.g. 10 = 10%)")
    valid_from: Optional[datetime] = Field(None, description="Valid from (optional)")
    valid_until: datetime = Field(..., description="Valid until")
    name: Optional[str] = Field(None, max_length=100, description="Admin note / campaign name")


class UpdateRechargePromoRequest(BaseModel):
    extra_credits_percent: Optional[float] = Field(None, ge=0, le=100)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    name: Optional[str] = Field(None, max_length=100)


# Category Page Schemas
class CategoryPageResponse(BaseModel):
    id: int
    parent_id: Optional[int] = None
    category_name: str
    level: int
    sort_order: int
    page_path: str
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[str] = None
    display_description: Optional[str] = None
    is_active: bool
    show_in_explore: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    children: Optional[List['CategoryPageResponse']] = None

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }


class CreateCategoryPageRequest(BaseModel):
    parent_id: Optional[int] = Field(None, description="Parent category ID (for level 2 categories)")
    category_name: str = Field(..., min_length=1, max_length=50)
    page_path: Optional[str] = Field(None, max_length=200)  # Auto-generated if not provided
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    keywords: Optional[str] = None
    display_description: Optional[str] = None
    sort_order: Optional[int] = Field(0, ge=0)
    is_active: Optional[bool] = Field(False)
    show_in_explore: Optional[bool] = Field(False)


class UpdateCategoryPageRequest(BaseModel):
    parent_id: Optional[int] = Field(None, description="Parent category ID (for level 2 categories)")
    category_name: Optional[str] = Field(None, min_length=1, max_length=50)
    page_path: Optional[str] = Field(None, max_length=200)
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    keywords: Optional[str] = None
    display_description: Optional[str] = None
    sort_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    show_in_explore: Optional[bool] = None


# Effects Page Schemas
class EffectsPageResponse(BaseModel):
    id: int
    parent_id: Optional[int] = None
    category_name: str
    level: int
    sort_order: int
    page_path: str
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[str] = None
    display_description: Optional[str] = None
    is_active: bool
    show_in_explore: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    children: Optional[List['EffectsPageResponse']] = None

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }


class CreateEffectsPageRequest(BaseModel):
    parent_id: Optional[int] = Field(None, description="Parent category ID (for level 2 categories)")
    category_name: str = Field(..., min_length=1, max_length=50)
    page_path: Optional[str] = Field(None, max_length=200)  # Auto-generated if not provided
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    keywords: Optional[str] = None
    display_description: Optional[str] = None
    sort_order: Optional[int] = Field(0, ge=0)
    is_active: Optional[bool] = Field(False)
    show_in_explore: Optional[bool] = Field(False)


# Workflow schemas
class WorkflowNodeData(BaseModel):
    """Node data configuration."""
    preset_params: Dict[str, Any] = Field(default_factory=dict, description="Preset parameters (fixed values)")
    param_mappings: Dict[str, str] = Field(default_factory=dict, description="Parameter mappings (e.g., '$.user_input.prompt')")
    params_visibility: Dict[str, bool] = Field(default_factory=dict, description="Parameter visibility to users")
    # Input node fields
    value: Optional[str] = Field(None, description="Preset value for input nodes (prompt, image URL, etc.)")
    label: Optional[str] = Field(None, description="Node display label")
    param_name: Optional[str] = Field(None, description="Parameter name for param_input nodes")
    # API call node fields
    api_id: Optional[int] = Field(None, description="API Library ID (for api_call nodes)")
    provider: Optional[str] = Field(None, description="API provider name")
    params_schema: Optional[Dict[str, Any]] = Field(None, description="API parameters schema")
    param_defaults: Optional[Dict[str, Any]] = Field(None, description="Default parameter values")
    
    model_config = {
        "extra": "allow"  # Allow additional fields for flexibility
    }


class WorkflowNode(BaseModel):
    """Workflow node schema."""
    id: str = Field(..., description="Unique node ID")
    type: str = Field(..., description="Node type (e.g., 'api_call', 'prompt_input', 'image_default', 'param_input')")
    api_id: Optional[int] = Field(None, description="API Library ID (required only for 'api_call' type nodes)")
    position: Dict[str, float] = Field(..., description="Node position on canvas (x, y)")
    data: WorkflowNodeData = Field(..., description="Node configuration data")
    
    @model_validator(mode='after')
    def validate_api_id(self):
        """Validate that api_id is provided for api_call nodes."""
        if self.type == 'api_call':
            if self.api_id is None:
                raise ValueError("api_id is required for 'api_call' type nodes")
            if self.api_id <= 0:
                raise ValueError("api_id must be greater than 0")
        return self


class WorkflowEdge(BaseModel):
    """Workflow edge (connection) schema."""
    id: str = Field(..., description="Unique edge ID")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    sourceHandle: str = Field(default="output", description="Source handle name")
    targetHandle: str = Field(default="input", description="Target handle name")


class CreateWorkflowRequest(BaseModel):
    """Request schema for creating a workflow."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    # work_type  generate_pages
    work_type: str = Field(..., min_length=1, max_length=50)
    nodes: List[WorkflowNode] = Field(..., min_length=1, description="Workflow nodes")
    edges: List[WorkflowEdge] = Field(default_factory=list, description="Connections between nodes")
    viewport: Optional[Dict[str, Any]] = Field(None, description="Canvas viewport position")
    is_active: bool = Field(default=True)


class UpdateWorkflowRequest(BaseModel):
    """Request schema for updating a workflow."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    # work_type  generate_pages
    work_type: Optional[str] = Field(None, min_length=1, max_length=50)
    nodes: Optional[List[WorkflowNode]] = Field(None, min_length=1, description="Workflow nodes")
    edges: Optional[List[WorkflowEdge]] = Field(None, description="Connections between nodes")
    viewport: Optional[Dict[str, Any]] = Field(None, description="Canvas viewport position")
    is_active: Optional[bool] = None


class UpdateEffectsPageRequest(BaseModel):
    parent_id: Optional[int] = Field(None, description="Parent category ID (for level 2 categories)")
    category_name: Optional[str] = Field(None, min_length=1, max_length=50)
    page_path: Optional[str] = Field(None, max_length=200)
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    keywords: Optional[str] = None
    display_description: Optional[str] = None
    sort_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    show_in_explore: Optional[bool] = None


class GeneratePageResponse(BaseModel):
    id: int
    parent_id: Optional[int] = None
    category_name: str
    level: int
    sort_order: int
    page_path: str
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[str] = None
    display_description: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    children: Optional[List['GeneratePageResponse']] = None

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }


class CreateGeneratePageRequest(BaseModel):
    parent_id: Optional[int] = Field(None, description="Parent category ID (for level 2 categories)")
    category_name: str = Field(..., min_length=1, max_length=50)
    page_path: Optional[str] = Field(None, max_length=200)
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    keywords: Optional[str] = None
    display_description: Optional[str] = None
    sort_order: Optional[int] = Field(0, ge=0)
    is_active: Optional[bool] = Field(False)


class UpdateGeneratePageRequest(BaseModel):
    parent_id: Optional[int] = Field(None, description="Parent category ID (for level 2 categories)")
    category_name: Optional[str] = Field(None, min_length=1, max_length=50)
    page_path: Optional[str] = Field(None, max_length=200)
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    keywords: Optional[str] = None
    display_description: Optional[str] = None
    sort_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


# CheckIn schemas
class CheckInResponse(BaseModel):
    """Response schema for check-in."""
    consecutive_days: int = Field(..., description="")
    reward_credits: int = Field(..., description="")
    total_credits: int = Field(..., description="")
    next_reward: int = Field(..., description="")


class CheckInStatusResponse(BaseModel):
    """Response schema for check-in status."""
    has_checked_today: bool = Field(..., description="Whether checked in today")
    consecutive_days: int = Field(..., description="Consecutive check-in days")
    checkin_dates: List[str] = Field(..., description="")
    next_reward: Optional[int] = Field(None, description="")
    total_checkins: int = Field(..., description="Total check-in count")


class CheckInHistoryItem(BaseModel):
    """Single check-in history item."""
    check_date: str = Field(..., description="")
    consecutive_days: int = Field(..., description="")
    reward_credits: int = Field(..., description="")
    created_at: str = Field(..., description="")


class CheckInHistoryResponse(BaseModel):
    """Response schema for check-in history."""
    items: List[CheckInHistoryItem] = Field(..., description="Check-in records list")
    total: int = Field(..., description="Total records count")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")


# Promotion Banner Schemas
class CreatePromotionBannerRequest(BaseModel):
    """Banner"""
    title: str = Field(..., min_length=1, max_length=5000, description="Banner（ HTML）")
    content: Optional[str] = Field(None, description="Banner/")
    image_url: Optional[str] = Field(None, max_length=500, description="BannerURL（）")
    link_url: Optional[str] = Field(None, max_length=500, description="")
    link_text: Optional[str] = Field(None, max_length=5000, description="（ HTML）")
    background_color: Optional[str] = Field(None, max_length=50, description="（）")
    background_gradient: Optional[str] = Field(None, max_length=200, description="（CSS gradient）")
    background_image_url: Optional[str] = Field(None, max_length=500, description="URL（）")
    text_color: Optional[str] = Field(None, max_length=50, description="")
    is_enabled: bool = Field(True, description="")
    sort_order: int = Field(0, description="")
    start_time: Optional[datetime] = Field(None, description="")
    end_time: Optional[datetime] = Field(None, description="")
    show_countdown: bool = Field(False, description="")
    layout_config: Optional[dict] = Field(None, description=" JSON：textAlign、countdown、buttons、content_scroll_interval_seconds ")
    content_items: Optional[list] = Field(None, description="， { title, content, image_url }， title/content/image_url")


class UpdatePromotionBannerRequest(BaseModel):
    """Banner"""
    title: Optional[str] = Field(None, min_length=1, max_length=5000, description="Banner（ HTML）")
    content: Optional[str] = Field(None, description="Banner/")
    image_url: Optional[str] = Field(None, max_length=500, description="BannerURL（）")
    link_url: Optional[str] = Field(None, max_length=500, description="")
    link_text: Optional[str] = Field(None, max_length=5000, description="（ HTML）")
    background_color: Optional[str] = Field(None, max_length=50, description="（）")
    background_gradient: Optional[str] = Field(None, max_length=200, description="（CSS gradient）")
    background_image_url: Optional[str] = Field(None, max_length=500, description="URL（）")
    text_color: Optional[str] = Field(None, max_length=50, description="")
    is_enabled: Optional[bool] = Field(None, description="Is enabled")
    sort_order: Optional[int] = Field(None, description="Sort order")
    start_time: Optional[datetime] = Field(None, description="")
    end_time: Optional[datetime] = Field(None, description="")
    show_countdown: Optional[bool] = Field(None, description="")
    layout_config: Optional[dict] = Field(None, description=" JSON：textAlign、countdown、buttons、content_scroll_interval_seconds ")
    content_items: Optional[list] = Field(None, description="， { title, content, image_url }")


# Carousel Slide Schemas
class CreateCarouselSlideRequest(BaseModel):
    """"""
    title: Optional[str] = Field(None, max_length=10000, description="（ HTML）")
    image_url: str = Field(..., max_length=500, description="URL（）")
    video_url: Optional[str] = Field(None, max_length=500, description="URL（）")
    link_url: Optional[str] = Field(None, max_length=500, description="")
    link_text: Optional[str] = Field(None, max_length=5000, description="（ HTML）")
    button_style: Optional[str] = Field("primary", max_length=50, description="")
    overlay_opacity: Optional[int] = Field(50, ge=0, le=100, description="")
    text_position: Optional[str] = Field("center", max_length=50, description="")
    text_align: Optional[str] = Field("center", max_length=50, description="")
    is_enabled: bool = Field(True, description="")
    sort_order: int = Field(0, description="")
    start_time: Optional[datetime] = Field(None, description="")
    end_time: Optional[datetime] = Field(None, description="")


class UpdateCarouselSlideRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=10000, description="（ HTML）")
    image_url: Optional[str] = Field(None, max_length=500, description="URL")
    video_url: Optional[str] = Field(None, max_length=500, description="URL")
    link_url: Optional[str] = Field(None, max_length=500, description="")
    link_text: Optional[str] = Field(None, max_length=5000, description="（ HTML）")
    button_style: Optional[str] = Field(None, max_length=50, description="")
    overlay_opacity: Optional[int] = Field(None, ge=0, le=100, description="")
    text_position: Optional[str] = Field(None, max_length=50, description="")
    text_align: Optional[str] = Field(None, max_length=50, description="")
    is_enabled: Optional[bool] = Field(None, description="Is enabled")
    sort_order: Optional[int] = Field(None, description="Sort order")
    start_time: Optional[datetime] = Field(None, description="")
    end_time: Optional[datetime] = Field(None, description="")


# HomepageBlock Schemas (Banner + Carousel )
class CreateHomepageBlockRequest(BaseModel):
    """"""
    type: str = Field(..., description="banner | carousel")
    config: dict = Field(..., description=" JSON")
    sort_order: int = Field(0, description="")
    is_enabled: bool = Field(True, description="")


class UpdateHomepageBlockRequest(BaseModel):
    """Update homepage block"""
    config: Optional[dict] = Field(None, description="Full configuration JSON")
    sort_order: Optional[int] = Field(None, description="Sort order")
    is_enabled: Optional[bool] = Field(None, description="Is enabled")
