"""
Admin API Internationalization (i18n) Utility Module.

Provides translation dictionary and helper functions for Admin API responses.
Default language is English ('en'). Accepts 'zh' / 'zh-CN' via Accept-Language header or query param.
"""
from typing import Dict, Optional
from fastapi import Request

# Dictionary mapping message keys to English (default) and Chinese translations
ADMIN_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Auth & System
    "login_success": {"en": "Login successful", "zh": "登录成功"},
    "login_failed": {"en": "Invalid username or password", "zh": "用户名或密码错误"},
    "unauthorized": {"en": "Authentication required", "zh": "未登录或身份验证失效"},
    "forbidden": {"en": "Permission denied", "zh": "权限不足"},
    "account_disabled": {"en": "Account is disabled", "zh": "账号已被禁用"},
    "operation_success": {"en": "Operation completed successfully", "zh": "操作成功"},
    "operation_failed": {"en": "Operation failed", "zh": "操作失败"},
    "not_found": {"en": "Resource not found", "zh": "未找到相关资源"},
    "invalid_param": {"en": "Invalid parameter", "zh": "参数无效"},
    "server_error": {"en": "Internal server error", "zh": "服务器内部错误"},

    # Users
    "user_not_found": {"en": "User not found", "zh": "用户不存在"},
    "user_updated": {"en": "User updated successfully", "zh": "用户信息更新成功"},
    "user_deleted": {"en": "User deleted successfully", "zh": "用户已删除"},
    "user_status_changed": {"en": "User status updated successfully", "zh": "用户状态已更新"},

    # Works & Content
    "work_not_found": {"en": "Work not found", "zh": "作品不存在"},
    "work_updated": {"en": "Work updated successfully", "zh": "作品已更新"},
    "work_deleted": {"en": "Work deleted successfully", "zh": "作品已删除"},
    "work_approved": {"en": "Work approved successfully", "zh": "作品审核已通过"},
    "work_rejected": {"en": "Work rejected successfully", "zh": "作品已拒绝"},

    # Moderation & Comments
    "comment_not_found": {"en": "Comment not found", "zh": "评论不存在"},
    "comment_deleted": {"en": "Comment deleted successfully", "zh": "评论已删除"},
    "report_resolved": {"en": "Report resolved successfully", "zh": "举报处理完成"},
    "report_dismissed": {"en": "Report dismissed successfully", "zh": "举报已忽略"},

    # Promos & Banners
    "banner_created": {"en": "Banner created successfully", "zh": "Banner 创建成功"},
    "banner_updated": {"en": "Banner updated successfully", "zh": "Banner 更新成功"},
    "banner_deleted": {"en": "Banner deleted successfully", "zh": "Banner 删除成功"},

    # Settings & System
    "settings_updated": {"en": "System settings updated successfully", "zh": "系统设置已更新"},
    "cache_cleared": {"en": "Cache cleared successfully", "zh": "缓存清理成功"},
}


def get_admin_lang(request: Optional[Request] = None) -> str:
    """
    Extract active language from Request (Accept-Language header or lang query param).
    Defaults to 'en'. Returns 'zh' if language is Chinese.
    """
    if not request:
        return "en"

    # 1. Check query parameter e.g. ?lang=zh
    lang_param = request.query_params.get("lang")
    if lang_param:
        if lang_param.lower().startswith("zh"):
            return "zh"
        return "en"

    # 2. Check Accept-Language header
    accept_lang = request.headers.get("Accept-Language", "")
    if accept_lang:
        primary = accept_lang.split(",")[0].strip().lower()
        if primary.startswith("zh"):
            return "zh"

    return "en"


def admin_t(key: str, lang: str = "en", default: Optional[str] = None) -> str:
    """
    Translate message key to requested language ('en' or 'zh').
    If key is missing, returns default or key.
    """
    lang_code = "zh" if lang.lower().startswith("zh") else "en"

    if key in ADMIN_TRANSLATIONS:
        return ADMIN_TRANSLATIONS[key].get(lang_code, ADMIN_TRANSLATIONS[key]["en"])

    return default if default is not None else key
