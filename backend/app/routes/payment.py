from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from ..models.base import get_db
from ..models.user import User
from ..models.payment_order import PaymentOrder, PaymentStatus
from ..services.credit_service import add_credits as credit_service_add_credits
from ..models.credit_record import CreditType
from ..models.recharge_package import RechargePackage
from ..models.recharge_promo import RechargePromo
from ..models.schemas import CreatePaymentRequest
from ..utils.auth import get_current_active_user
from ..utils.responses import success_response, error_response
from ..utils.logger import logger, log_payment
from ..services.paypal_service import get_paypal_service
from ..services.stripe_service import get_stripe_service
from ..services.email import send_recharge_success_email

router = APIRouter()


def _complete_payment_order_and_notify(
    db: Session,
    payment_order: PaymentOrder,
    user: User,
    background_tasks: BackgroundTasks,
    *,
    paypal_payment_id: Optional[str] = None,
) -> None:
    """
    Generic: add credits (including promo extra %), mark order completed, commit, log, and send recharge success email.
    Used by PayPal capture or any future provider.
    """
    payment_order = db.query(PaymentOrder).filter(
        PaymentOrder.id == payment_order.id
    ).with_for_update().first()
    if not payment_order or payment_order.status == PaymentStatus.COMPLETED:
        return

    base_credits = payment_order.credits
    extra_percent = float(payment_order.extra_credits_percent or 0)
    if extra_percent > 0:
        final_credits = int(round(base_credits * (1 + extra_percent / 100)))
        description = f"Purchased {base_credits} credits + {extra_percent}% bonus = {final_credits} credits"
    else:
        final_credits = base_credits
        description = f"Purchased {base_credits} credits"
    credit_service_add_credits(
        db,
        user.id,
        final_credits,
        CreditType.RECHARGE,
        description,
        order_id=payment_order.id,
    )
    payment_order.status = PaymentStatus.COMPLETED
    payment_order.completed_at = datetime.now(timezone.utc)
    if paypal_payment_id is not None:
        payment_order.paypal_payment_id = paypal_payment_id
    db.commit()

    log_payment(user.id, float(payment_order.amount_usd), final_credits, "completed")
    logger.info(
        f"Payment completed: order_id={payment_order.id}, provider={payment_order.payment_provider}, "
        f"credits={final_credits}"
    )

    background_tasks.add_task(
        send_recharge_success_email,
        user.email,
        user.nickname or user.email or "there",
        final_credits,
        float(payment_order.amount_usd),
    )


@router.get("/tiers")
async def get_payment_tiers(db: Session = Depends(get_db)):
    """
    Get available credit purchase tiers from database.
    """
    try:
        packages = db.query(RechargePackage).filter(
            RechargePackage.is_active == True
        ).order_by(RechargePackage.order.asc()).all()
        
        tiers = [
            {
                "credits": p.credits,
                "price": float(p.amount),
                "per_credit": float(p.amount) / p.credits,
                "is_featured": p.is_featured,
                "tag_text": p.tag_text
            }
            for p in packages
        ]
        
        return success_response(
            data=tiers,
            message="Payment tiers retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting payment tiers: {str(e)}")
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/create")
async def create_payment(
    request: CreatePaymentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a PayPal payment order for credit purchase.
    """
    try:
        # Validate credits and get amount from database
        package = db.query(RechargePackage).filter(
            RechargePackage.credits == request.credits,
            RechargePackage.is_active == True
        ).first()
        
        if not package:
            return error_response(
                message=f"Invalid credit amount: {request.credits}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        amount_usd = package.amount
        extra_credits_percent = None
        if request.promo_code and request.promo_code.strip():
            promo = db.query(RechargePromo).filter(
                RechargePromo.promo_code == request.promo_code.strip()
            ).first()
            if promo and (promo.user_id is None or promo.user_id == current_user.id):
                now = datetime.now(timezone.utc)
                if (promo.valid_from is None or promo.valid_from <= now) and promo.valid_until >= now:
                    extra_credits_percent = promo.extra_credits_percent

        # Create payment order record
        payment_order = PaymentOrder(
            user_id=current_user.id,
            amount_usd=amount_usd,
            credits=request.credits,
            status=PaymentStatus.PENDING,
            extra_credits_percent=extra_credits_percent,
        )
        
        db.add(payment_order)
        db.commit()
        db.refresh(payment_order)
        
        if request.provider == "paypal":
            # Create PayPal order
            try:
                paypal = get_paypal_service()
                paypal_order = await paypal.create_order(
                    amount_usd=amount_usd,
                    return_url=f"{os.getenv('FRONTEND_URL')}/payment/success?order_id={payment_order.id}",
                    cancel_url=f"{os.getenv('FRONTEND_URL')}/payment/cancel?order_id={payment_order.id}"
                )
                
                # Update payment order with PayPal order ID
                payment_order.paypal_order_id = paypal_order["order_id"]
                payment_order.payment_provider = "paypal"
                db.commit()
                
                logger.info(f"PayPal payment order created: {payment_order.id} for user {current_user.id}")
                
                return success_response(
                    data={
                        "order_id": payment_order.id,
                        "paypal_order_id": paypal_order["order_id"],
                        "approval_url": paypal_order["approval_url"],
                        "amount_usd": float(amount_usd),
                        "credits": request.credits,
                        "provider": "paypal"
                    },
                    message="PayPal payment order created successfully"
                )
            except Exception as e:
                # Mark order as failed
                payment_order.status = PaymentStatus.FAILED
                payment_order.error_message = str(e)
                db.commit()
                
                logger.error(f"Failed to create PayPal order for user {current_user.id}: {str(e)}")
                return error_response(
                    message=f"Failed to create PayPal order: {str(e)}",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        elif request.provider == "stripe":
            # Stripe payment flow
            try:
                stripe_service = get_stripe_service()
                
                # Stripe urls
                success_url = f"{os.getenv('FRONTEND_URL')}/payment/success?session_id={{CHECKOUT_SESSION_ID}}&order_id={payment_order.id}"
                cancel_url = f"{os.getenv('FRONTEND_URL')}/payment/cancel?order_id={payment_order.id}"
                
                session = stripe_service.create_checkout_session(
                    amount_usd=float(amount_usd),
                    credits=request.credits,
                    order_id=payment_order.id,
                    user_email=current_user.email,
                    success_url=success_url,
                    cancel_url=cancel_url
                )
                
                # Update payment order with Stripe session ID
                payment_order.stripe_session_id = session["session_id"]
                payment_order.payment_provider = "stripe"
                db.commit()
                
                logger.info(f"Stripe checkout session created: {payment_order.id} for user {current_user.id}")
                
                return success_response(
                    data={
                        "order_id": payment_order.id,
                        "stripe_session_id": session["session_id"],
                        "checkout_url": session["checkout_url"],
                        "amount_usd": float(amount_usd),
                        "credits": request.credits,
                        "provider": "stripe"
                    },
                    message="Stripe checkout session created successfully"
                )
            except Exception as e:
                # Mark order as failed
                payment_order.status = PaymentStatus.FAILED
                payment_order.error_message = str(e)
                db.commit()
                
                logger.error(f"Failed to create Stripe session for user {current_user.id}: {str(e)}")
                return error_response(
                    message=f"Failed to create Stripe session: {str(e)}",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating payment: {str(e)}")
        return error_response(
            message="An error occurred while creating payment",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/capture")
async def capture_payment(
    background_tasks: BackgroundTasks,
    order_id: int = Query(...),
    session_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Capture (complete) a PayPal payment and add credits to user.
    """
    try:
        # Get payment order
        payment_order = db.query(PaymentOrder).filter(
            PaymentOrder.id == order_id
        ).first()
        
        if not payment_order:
            return error_response(
                message="Payment order not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Check ownership
        if payment_order.user_id != current_user.id:
            return error_response(
                message="Not authorized",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Check if already completed. Keep this endpoint idempotent so payment
        # success pages can safely retry after webhooks or browser refreshes.
        if payment_order.status == PaymentStatus.COMPLETED:
            new_total = db.query(User.total_credits).filter(User.id == current_user.id).scalar()
            return success_response(
                data={
                    "order_id": payment_order.id,
                    "credits_added": payment_order.credits,
                    "new_total": new_total,
                    "amount_usd": float(payment_order.amount_usd),
                },
                message="Payment already completed",
            )

        if payment_order.payment_provider == "stripe":
            try:
                stripe_session_id = session_id or payment_order.stripe_session_id
                if not stripe_session_id:
                    return error_response(
                        message="Stripe session ID not found",
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )

                if payment_order.stripe_session_id and stripe_session_id != payment_order.stripe_session_id:
                    return error_response(
                        message="Stripe session does not match this order",
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )

                stripe_service = get_stripe_service()
                # stripe SDK (v15+) returns a StripeObject without dict.get();
                # normalize to a nested plain dict before using .get().
                from .webhook import _stripe_obj_to_dict
                stripe_session = _stripe_obj_to_dict(
                    stripe_service.retrieve_checkout_session(stripe_session_id)
                ) or {}
                stripe_order_id = stripe_session.get("client_reference_id") or stripe_session.get("metadata", {}).get("order_id")

                if str(stripe_order_id) != str(payment_order.id):
                    return error_response(
                        message="Stripe session does not match this order",
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )

                if stripe_session.get("payment_status") != "paid":
                    return error_response(
                        message="Stripe payment is not paid yet",
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )

                payment_order.stripe_session_id = stripe_session_id
                payment_order.stripe_payment_intent_id = stripe_session.get("payment_intent")
                _complete_payment_order_and_notify(
                    db,
                    payment_order,
                    current_user,
                    background_tasks,
                )
                new_total = db.query(User.total_credits).filter(User.id == current_user.id).scalar()
                return success_response(
                    data={
                        "order_id": payment_order.id,
                        "credits_added": payment_order.credits,
                        "new_total": new_total,
                        "amount_usd": float(payment_order.amount_usd),
                    },
                    message="Payment completed successfully",
                )
            except Exception as e:
                logger.error(f"Failed to reconcile Stripe payment: {str(e)}")
                return error_response(
                    message="Failed to confirm Stripe payment",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # PayPal: capture then complete and send email
        try:
            paypal = get_paypal_service()
            capture_result = await paypal.capture_order(payment_order.paypal_order_id)
            if capture_result["status"] == "COMPLETED":
                _complete_payment_order_and_notify(
                    db,
                    payment_order,
                    current_user,
                    background_tasks,
                    paypal_payment_id=capture_result.get("id"),
                )
                new_total = db.query(User.total_credits).filter(User.id == current_user.id).scalar()
                return success_response(
                    data={
                        "order_id": payment_order.id,
                        "credits_added": payment_order.credits,
                        "new_total": new_total,
                        "amount_usd": float(payment_order.amount_usd),
                    },
                    message="Payment completed successfully",
                )
            payment_order.status = PaymentStatus.FAILED
            payment_order.error_message = f"PayPal status: {capture_result.get('status')}"
            db.commit()
            return error_response(
                message="Payment capture failed",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            payment_order.status = PaymentStatus.FAILED
            payment_order.error_message = str(e)
            db.commit()
            logger.error(f"Failed to capture PayPal payment: {str(e)}")
            return error_response(
                message="Failed to complete payment",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error capturing payment: {str(e)}")
        return error_response(
            message="An error occurred while processing payment",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/orders")
async def get_payment_orders(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's payment order history.
    """
    try:
        # Get total count
        total = db.query(PaymentOrder).filter(
            PaymentOrder.user_id == current_user.id
        ).count()
        
        # Get paginated orders
        orders = db.query(PaymentOrder).filter(
            PaymentOrder.user_id == current_user.id
        ).order_by(
            PaymentOrder.created_at.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        items = [order.to_dict() for order in orders]
        
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Payment orders retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting payment orders: {str(e)}")
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


import os
from ..utils.responses import paginated_response
