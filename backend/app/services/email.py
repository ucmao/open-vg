import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import random
import string
import asyncio
from typing import Optional, Tuple

from ..utils.logger import logger

from email.header import Header
from email.utils import formataddr

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER)
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "VidGen")


_EMAIL_CODE_KEY_PREFIX = "auth:email_code"


def _email_code_key(email: str) -> str:
    # Keep key stable; global prefix is applied in redis_cache.build_key()
    return f"{_EMAIL_CODE_KEY_PREFIX}:{email.strip().lower()}"


def _set_email_code(email: str, code: str, ttl_seconds: int) -> None:
    """
    Store email code in Redis (best-effort).
    Falls back to in-memory only if Redis is not configured.
    """
    try:
        from ..utils.redis_cache import get_redis, build_key

        r = get_redis()
        if r:
            r.setex(build_key(_email_code_key(email)), ttl_seconds, code)
            return
    except Exception as e:
        logger.warning(f"Failed to store email code in Redis: {e}")

    # Fallback (dev / Redis not configured)
    global verification_codes
    if "verification_codes" not in globals():
        verification_codes = {}  # type: ignore
    verification_codes[email] = code  # type: ignore


def _get_email_code(email: str) -> Optional[str]:
    try:
        from ..utils.redis_cache import get_redis, build_key

        r = get_redis()
        if r:
            return r.get(build_key(_email_code_key(email)))
    except Exception as e:
        logger.warning(f"Failed to read email code from Redis: {e}")

    # Fallback
    vc = globals().get("verification_codes")
    if isinstance(vc, dict):
        return vc.get(email)
    return None


def _delete_email_code(email: str) -> None:
    try:
        from ..utils.redis_cache import get_redis, build_key

        r = get_redis()
        if r:
            r.delete(build_key(_email_code_key(email)))
            return
    except Exception as e:
        logger.warning(f"Failed to delete email code from Redis: {e}")

    vc = globals().get("verification_codes")
    if isinstance(vc, dict):
        vc.pop(email, None)


def generate_verification_code(length: int = 6) -> str:
    """Generate a random verification code."""
    return ''.join(random.choices(string.digits, k=length))


async def send_email(to_email: str, subject: str, html_content: str) -> tuple[bool, Optional[str]]:

    """
    Send an email using SMTP.
    Returns (success: bool, error_message: Optional[str])
    """
    # Sanitize input
    to_email = to_email.strip()
    
    # Check if we should actually send email or just mock it
    if os.getenv("ENVIRONMENT") == "development" or not SMTP_USER:
        logger.info(f"DEV MODE: Skipping real email send to {to_email}. Subject: {subject}")
        return True, None

    try:
        message = MIMEMultipart('alternative')
        message['Subject'] = Header(subject, 'utf-8').encode()
        
        # Encode display name with RFC2047 Base64 so the resulting string is
        # pure ASCII — formataddr is NOT used here because it would attempt
        # to re-encode an already-mangled Header string and aiosmtplib would
        # then fail with "ascii codec can't encode" on the non-ASCII bytes.
        import base64 as _b64
        _name_b64 = _b64.b64encode(SMTP_FROM_NAME.encode('utf-8')).decode('ascii')
        from_header = f"=?utf-8?b?{_name_b64}?= <{SMTP_FROM_EMAIL}>"
        message['From'] = from_header
        message['To'] = to_email
        
        html_part = MIMEText(html_content, 'html', 'utf-8')
        message.attach(html_part)
        
        # Determine connection type based on port
        use_ssl = SMTP_PORT == 465
        
        await asyncio.wait_for(
            aiosmtplib.send(
                message,
                hostname=SMTP_HOST,
                port=SMTP_PORT,
                username=SMTP_USER,
                password=SMTP_PASSWORD,
                use_tls=use_ssl,
                start_tls=not use_ssl,
            ),
            timeout=15.0
        )
        
        logger.info(f"Email sent successfully to {to_email}")
        return True, None
        
    except asyncio.TimeoutError:
        error_msg = f"SMTP connection timeout. Please check your network connection and SMTP settings."
        logger.error(f"Failed to send email to {to_email}: {error_msg}")
        return False, error_msg
    except Exception as e:
        error_str = str(e)
        # Check for non-ASCII address error specifically to provide better context
        if "non-ASCII characters" in error_str:
            logger.error(f"Non-ASCII character detected in address or header. Recipient: {to_email}, From: {SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>")
        
        error_msg = f"Failed to send email: {error_str}"
        logger.error(f"Failed to send email to {to_email}: {error_str}")
        return False, error_msg



async def send_verification_code(email: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Generate and send a verification code to the email.
    Returns (code: Optional[str], error_message: Optional[str])
    """
    code = generate_verification_code()
    
    # Check if we should actually send email or just mock it
    if os.getenv("ENVIRONMENT") == "development" or not SMTP_USER:
        logger.info(f"DEV MODE: Skipping real email send. Code for {email}: {code}")
        _set_email_code(email, code, ttl_seconds=5 * 60)
        return code, None

    # Store code in memory first to ensure it's available when user receives the email
    _set_email_code(email, code, ttl_seconds=5 * 60)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .code {{ font-size: 32px; font-weight: bold; color: #667eea; 
                     letter-spacing: 5px; text-align: center; padding: 20px; 
                     background: white; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Email Verification</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>Thank you for signing up for VidGen! To complete your registration, 
                   please use the verification code below:</p>
                <div class="code">{code}</div>
                <p>This code will expire in 5 minutes.</p>
                <p>If you didn't request this code, please ignore this email.</p>
                <p>Best regards,<br>VidGen Team</p>
            </div>
            <div class="footer">
                <p>© 2024 VidGen. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    success, error_msg = await send_email(email, "Verification Code - VidGen", html_content)
    
    if success:
        return code, None
    else:
        # If email sending fails, remove the stored code
        _delete_email_code(email)
        return None, error_msg


def verify_code(email: str, code: str, remove_on_success: bool = True) -> bool:
    """
    Verify if the provided code matches the stored code for the email.
    
    Args:
        email: Email address
        code: Verification code to check
        remove_on_success: Whether to remove the code after successful verification (default: True)
    """
    stored_code = _get_email_code(email)
    
    if stored_code and stored_code == code:
        # Remove code after successful verification if requested
        # In development, keep it for easier retries if remove_on_success is False
        if remove_on_success:
            if os.getenv("ENVIRONMENT") != "development":
                _delete_email_code(email)
        return True
    
    return False


async def send_welcome_email(email: str, nickname: str, credits: int) -> Tuple[bool, Optional[str]]:
    """
    Send a welcome email to new users.
    
    Args:
        email: User email address
        nickname: User nickname
        credits: Welcome credits amount
        
    Returns:
        (success: bool, error_message: Optional[str])
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .credits {{ font-size: 24px; font-weight: bold; color: #667eea; text-align: center; 
                        padding: 15px; background: white; border-radius: 5px; margin: 20px 0; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #667eea; 
                       color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to VidGen! 🎨</h1>
            </div>
            <div class="content">
                <p>Hello {nickname},</p>
                <p>Welcome to VidGen! We're excited to have you join our community 
                   of AI content creators.</p>
                <div class="credits">
                    You've received {credits} welcome credits! 🎁
                </div>
                <p>Use your credits to:</p>
                <ul>
                    <li>Generate amazing AI images</li>
                    <li>Create stunning AI videos</li>
                    <li>Transform your photos with AI</li>
                    <li>Share your creations with the community</li>
                </ul>
                <p style="text-align: center;">
                    <a href="{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/generate" class="button">
                        Start Creating
                    </a>
                </p>
                <p>If you have any questions, feel free to reach out to our support team.</p>
                <p>Happy creating!<br>VidGen Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return await send_email(email, "Welcome to VidGen!", html_content)


async def send_recharge_success_email(
    email: str,
    nickname: str,
    credits: int,
    amount_usd: float,
) -> Tuple[bool, Optional[str]]:
    """
    Send a recharge success email to the user (English).

    Args:
        email: User email address
        nickname: User nickname
        credits: Credits purchased
        amount_usd: Amount paid in USD

    Returns:
        (success: bool, error_message: Optional[str])
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                       color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .credits {{ font-size: 24px; font-weight: bold; color: #667eea; text-align: center;
                        padding: 15px; background: white; border-radius: 5px; margin: 20px 0; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #667eea;
                       color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Payment Successful</h1>
            </div>
            <div class="content">
                <p>Hello {nickname or 'there'},</p>
                <p>Thank you for your purchase. Your payment has been completed successfully.</p>
                <div class="credits">
                    {credits} credits have been added to your account.
                </div>
                <p><strong>Order details:</strong></p>
                <ul>
                    <li>Credits: {credits}</li>
                    <li>Amount: ${amount_usd:.2f} USD</li>
                </ul>
                <p style="text-align: center;">
                    <a href="{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/generate" class="button">
                        Start Creating
                    </a>
                </p>
                <p>If you have any questions, please contact our support team.</p>
                <p>Best regards,<br>VidGen Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    return await send_email(email, "Payment Successful - VidGen", html_content)


async def send_password_reset_code(email: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Generate and send a password reset code to the email.
    """
    code = generate_verification_code()
    
    # Check if we should actually send email or just mock it
    if os.getenv("ENVIRONMENT") == "development" or not SMTP_USER:
        logger.info(f"DEV MODE: Skipping real email send. Reset code for {email}: {code}")
        _set_email_code(email, code, ttl_seconds=10 * 60)
        return code, None

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .code {{ font-size: 32px; font-weight: bold; color: #667eea; 
                     letter-spacing: 5px; text-align: center; padding: 20px; 
                     background: white; border-radius: 5px; margin: 20px 0; }}
            .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; 
                       padding: 15px; margin: 20px 0; border-radius: 5px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Password Reset Request</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>We received a request to reset your password for your VidGen account. 
                   Please use the verification code below to reset your password:</p>
                <div class="code">{code}</div>
                <p>This code will expire in 10 minutes.</p>
                <div class="warning">
                    <strong>⚠️ Security Notice:</strong> If you didn't request this password reset, 
                    please ignore this email. Your password will remain unchanged.
                </div>
                <p>Best regards,<br>VidGen Team</p>
            </div>
            <div class="footer">
                <p>© 2024 VidGen. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    success, error_msg = await send_email(email, "Password Reset Code - VidGen", html_content)
    
    if success:
        # Store code (expires in 10 minutes)
        _set_email_code(email, code, ttl_seconds=10 * 60)
        return code, None
    
    return None, error_msg


# Recharge promo email presets (admin selects when sending; label for UI, subject for email)
PROMO_EMAIL_PRESETS = {
    "exclusive": {
        "label": "",
        "subject": "Your exclusive recharge bonus: +{extra}% extra credits",
    },
    "limit_time": {
        "label": "",
        "subject": "Limited time: Your exclusive bonus link",
    },
    "reserved": {
        "label": "",
        "subject": "We saved a bonus for you: +{extra}% extra credits",
    },
    "surprise": {
        "label": "",
        "subject": "A little surprise: Your exclusive recharge bonus is ready",
    },
    "payment_cancelled": {
        "label": "",
        "subject": "We saved a bonus for you: +{extra}% extra credits (payment not completed)",
    },
}


def build_recharge_promo_email_content(
    nickname: str,
    recharge_url: str,
    extra_credits_percent: float,
    valid_until_str: Optional[str],
    reason_key: str = "exclusive",
) -> Tuple[str, str]:
    """
    Build subject and HTML body for recharge promo email (for preview or send).
    Returns (subject, html_content).
    """
    preset = PROMO_EMAIL_PRESETS.get(reason_key) or PROMO_EMAIL_PRESETS["exclusive"]
    subject = preset["subject"].format(extra=int(extra_credits_percent))
    valid_line = f" Valid until {valid_until_str}." if valid_until_str else ""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                       color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; padding: 14px 28px; background: #667eea;
                       color: white; text-decoration: none; border-radius: 8px; margin: 20px 0; font-weight: bold; }}
            .highlight {{ background: #e8eaf6; padding: 15px; border-radius: 8px; margin: 15px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Exclusive Recharge Bonus</h1>
            </div>
            <div class="content">
                <p>Hello {nickname or 'there'},</p>
                <p>We've prepared an exclusive recharge bonus for you: use the link below to buy any credit package and get <strong>{int(extra_credits_percent)}%</strong> extra credits.{valid_line}</p>
                <div class="highlight">
                    <p style="margin: 0 0 10px 0;">Click the button below to use your exclusive link:</p>
                    <p style="text-align: center; margin: 0;">
                        <a href="{recharge_url}" class="button">Use My Exclusive Link</a>
                    </p>
                    <p style="font-size: 12px; color: #666; margin: 10px 0 0 0;">Or copy and open in your browser:<br>{recharge_url}</p>
                </div>
                <p>If you have any questions, please contact our support team.</p>
                <p>Best regards,<br>VidGen Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    return subject, html_content


async def send_recharge_promo_email(
    email: str,
    nickname: str,
    recharge_url: str,
    extra_credits_percent: float,
    valid_until_str: Optional[str],
    reason_key: str = "exclusive",
) -> Tuple[bool, Optional[str]]:
    """
    Send a recharge promo email with the dedicated link.
    reason_key selects subject from PROMO_EMAIL_PRESETS.
    """
    subject, html_content = build_recharge_promo_email_content(
        nickname=nickname,
        recharge_url=recharge_url,
        extra_credits_percent=extra_credits_percent,
        valid_until_str=valid_until_str,
        reason_key=reason_key,
    )
    return await send_email(email, subject, html_content)

