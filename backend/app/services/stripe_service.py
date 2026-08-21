"""Stripe payment service integration."""
import os
import stripe
from dotenv import load_dotenv
from typing import Dict, Any, Optional

from ..utils.logger import logger

load_dotenv()

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Initialize stripe
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY
else:
    logger.warning("Stripe Secret Key not configured")


class StripeService:
    """Service for managing Stripe payments."""
    
    def __init__(self):
        self.secret_key = STRIPE_SECRET_KEY
        self.webhook_secret = STRIPE_WEBHOOK_SECRET
        
    def create_checkout_session(
        self,
        amount_usd: float,
        credits: int,
        order_id: int,
        user_email: str,
        success_url: str,
        cancel_url: str,
        product_name: str = "VidGen Credits"
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout Session.
        
        Args:
            amount_usd: Amount in USD
            credits: Number of credits
            order_id: Internal system order ID
            user_email: User email for the stripe session
            success_url: Redirect URL after success
            cancel_url: Redirect URL after cancellation
            product_name: Name shown on checkout page
            
        Returns:
            Dictionary with session_id and checkout_url
        """
        if not self.secret_key:
            raise Exception("Stripe Secret Key not configured")
            
        try:
            # Stripe amounts are in cents
            amount_cents = int(round(amount_usd * 100))
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product_name,
                            'description': f"{credits} credits for VidGen",
                        },
                        'unit_amount': amount_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=user_email,
                client_reference_id=str(order_id),  # Store internal order ID
                metadata={
                    "order_id": str(order_id),
                    "credits": str(credits)
                },
                payment_intent_data={
                    "metadata": {
                        "order_id": str(order_id),
                        "credits": str(credits)
                    }
                }
            )
            
            logger.info(f"Stripe checkout session created: {session.id} for order {order_id}")
            
            return {
                "session_id": session.id,
                "checkout_url": session.url
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating session: {str(e)}")
            raise Exception(f"Stripe error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating Stripe session: {str(e)}")
            raise Exception(f"Failed to create Stripe session: {str(e)}")
            
    def construct_event(self, payload: bytes, sig_header: str):
        """
        Verify and construct a Stripe webhook event.
        """
        if not self.webhook_secret:
            raise Exception("Stripe Webhook Secret not configured")
            
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            return event
        except ValueError as e:
            # Invalid payload
            raise Exception("Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            raise Exception("Invalid signature")

    def retrieve_checkout_session(self, session_id: str):
        """
        Retrieve a Checkout Session from Stripe for return-url reconciliation.
        """
        if not self.secret_key:
            raise Exception("Stripe Secret Key not configured")

        try:
            return stripe.checkout.Session.retrieve(session_id)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving session {session_id}: {str(e)}")
            raise Exception(f"Stripe error: {str(e)}")

    def retrieve_checkout_session_for_payment_intent(self, payment_intent_id: str):
        """
        Retrieve the Checkout Session associated with a PaymentIntent.
        Useful as a webhook fallback when Stripe sends payment_intent.succeeded.
        """
        if not self.secret_key:
            raise Exception("Stripe Secret Key not configured")

        try:
            sessions = stripe.checkout.Session.list(
                payment_intent=payment_intent_id,
                limit=1,
            )
            if not sessions.data:
                return None
            return sessions.data[0]
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error listing sessions for payment intent {payment_intent_id}: {str(e)}")
            raise Exception(f"Stripe error: {str(e)}")


# Singleton instance
_stripe_service = None


def get_stripe_service() -> StripeService:
    """
    Get or create StripeService singleton instance.
    """
    global _stripe_service
    if _stripe_service is None:
        _stripe_service = StripeService()
    return _stripe_service
