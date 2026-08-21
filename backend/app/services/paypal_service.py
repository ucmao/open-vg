"""PayPal payment service integration."""
import os
from dotenv import load_dotenv
from typing import Dict, Any
import httpx

from ..utils.logger import logger

load_dotenv()

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox")  # sandbox or live

# PayPal API URLs
PAYPAL_API_BASE = (
    "https://api-m.sandbox.paypal.com"
    if PAYPAL_MODE == "sandbox"
    else "https://api-m.paypal.com"
)


class PayPalService:
    """Service for managing PayPal payments."""
    
    def __init__(self):
        if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
            logger.warning("PayPal credentials not configured")
        
        self.client_id = PAYPAL_CLIENT_ID
        self.client_secret = PAYPAL_CLIENT_SECRET
        self.base_url = PAYPAL_API_BASE
        self._access_token = None
    
    async def get_access_token(self) -> str:
        """
        Get PayPal OAuth access token.
        
        Returns:
            Access token string
        """
        # Check if credentials are configured
        if not self.client_id or not self.client_secret:
            error_msg = "PayPal credentials not configured. Please set PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET in .env"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/oauth2/token",
                    auth=(self.client_id, self.client_secret),
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={"grant_type": "client_credentials"}
                )
                
                # Log detailed error information
                if response.status_code != 200:
                    error_detail = response.text
                    logger.error(
                        f"PayPal OAuth failed - Status: {response.status_code}, "
                        f"Response: {error_detail}, "
                        f"Mode: {PAYPAL_MODE}, "
                        f"Base URL: {self.base_url}, "
                        f"Client ID (first 10 chars): {self.client_id[:10]}..."
                    )
                    raise Exception(f"PayPal authentication failed: {response.status_code} - {error_detail}")
                
                response.raise_for_status()
                data = response.json()
                self._access_token = data["access_token"]
                return self._access_token
                
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text if e.response else str(e)
            logger.error(
                f"PayPal OAuth HTTP error - Status: {e.response.status_code if e.response else 'unknown'}, "
                f"Response: {error_detail}"
            )
            raise Exception(f"PayPal authentication failed: {e.response.status_code if e.response else 'unknown'} - {error_detail}")
        except Exception as e:
            import traceback
            logger.error(
                f"Failed to get PayPal access token. Details:\n"
                f"Error: {str(e)}\n"
                f"Traceback: {traceback.format_exc()}\n"
                f"Mode: {PAYPAL_MODE}\n"
                f"Base URL: {self.base_url}"
            )
            raise Exception(f"PayPal authentication failed: {str(e)}")
    
    async def create_order(
        self,
        amount_usd: float,
        currency: str = "USD",
        return_url: str = None,
        cancel_url: str = None
    ) -> Dict[str, Any]:
        """
        Create a PayPal order.
        
        Args:
            amount_usd: Amount in USD
            currency: Currency code (default: USD)
            return_url: URL to redirect after successful payment
            cancel_url: URL to redirect after cancelled payment
            
        Returns:
            Dictionary with order_id and approval_url
        """
        try:
            # Get access token
            token = await self.get_access_token()
            
            # Create order payload
            payload = {
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "amount": {
                            "currency_code": currency,
                            "value": f"{amount_usd:.2f}"
                        }
                    }
                ],
                "application_context": {
                    "return_url": return_url or f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/payment/success",
                    "cancel_url": cancel_url or f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/payment/cancel",
                }
            }
            
            # Create order
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v2/checkout/orders",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {token}"
                    },
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Extract approval URL
                approval_url = None
                for link in data.get("links", []):
                    if link.get("rel") == "approve":
                        approval_url = link.get("href")
                        break
                
                logger.info(f"PayPal order created: {data['id']}")
                
                return {
                    "order_id": data["id"],
                    "approval_url": approval_url,
                    "status": data.get("status")
                }
                
        except Exception as e:
            logger.error(f"Failed to create PayPal order: {str(e)}")
            raise Exception(f"PayPal order creation failed: {str(e)}")
    
    async def capture_order(self, order_id: str) -> Dict[str, Any]:
        """
        Capture (complete) a PayPal order.
        
        Args:
            order_id: PayPal order ID
            
        Returns:
            Dictionary with capture details
        """
        try:
            # Get access token
            token = await self.get_access_token()
            
            # Capture order
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v2/checkout/orders/{order_id}/capture",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {token}"
                    }
                )
                response.raise_for_status()
                
                data = response.json()
                
                logger.info(f"PayPal order captured: {order_id}")
                
                return {
                    "order_id": data["id"],
                    "status": data.get("status"),
                    "payer": data.get("payer"),
                    "purchase_units": data.get("purchase_units")
                }
                
        except Exception as e:
            logger.error(f"Failed to capture PayPal order: {str(e)}")
            raise Exception(f"PayPal order capture failed: {str(e)}")
    
    async def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """
        Get details of a PayPal order.
        
        Args:
            order_id: PayPal order ID
            
        Returns:
            Order details dictionary
        """
        try:
            # Get access token
            token = await self.get_access_token()
            
            # Get order details
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v2/checkout/orders/{order_id}",
                    headers={
                        "Authorization": f"Bearer {token}"
                    }
                )
                response.raise_for_status()
                
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to get PayPal order details: {str(e)}")
            raise Exception(f"Failed to get order details: {str(e)}")


# Singleton instance
_paypal_service = None


def get_paypal_service() -> PayPalService:
    """
    Get or create PayPalService singleton instance.
    
    Returns:
        PayPalService instance
    """
    global _paypal_service
    if _paypal_service is None:
        _paypal_service = PayPalService()
    return _paypal_service

