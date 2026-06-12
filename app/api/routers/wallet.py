from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from app.services.wallet_service import WalletService
from app.services.payment_service import PaymentService
from app.api.dependencies import get_current_user, require_permission
from app.models.user import User

router = APIRouter(prefix="/wallet", tags=["wallet"])

class ChargeRequest(BaseModel):
    amount: int = Field(..., ge=10000, le=100000000)
    method: str = Field(..., regex="^(card|online|receipt)$")

class TransactionResponse(BaseModel):
    id: int
    amount: int
    type: str
    status: str
    description: str
    balance_after: int
    created_at: str

@router.get("/balance")
async def get_balance(current_user: User = Depends(get_current_user)):
    return await WalletService.get_balance(current_user.telegram_id)

@router.post("/charge")
async def charge_wallet(
    request: ChargeRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a payment request for wallet charge"""
    payment_request = await PaymentService.create_payment_request(
        user_id=current_user.telegram_id,
        amount=request.amount,
        method=request.method
    )
    return {
        "request_id": payment_request.id,
        "amount": request.amount,
        "method": request.method,
        "status": "pending",
        "instructions": "لطفاً رسید پرداخت را از طریق ربات ارسال کنید."
    }

@router.get("/transactions")
async def get_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    current_user: User = Depends(get_current_user)
):
    return await WalletService.get_transactions(current_user.telegram_id, page, limit)

@router.get("/leaderboard")
async def get_leaderboard(limit: int = Query(10, ge=1, le=50)):
    return await WalletService.get_leaderboard(limit)

# Admin endpoints
@router.get("/admin/pending-requests")
async def get_pending_requests(
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    current_user: User = Depends(require_permission("approve_payment"))
):
    return await WalletService.get_pending_requests(current_user.telegram_id, page, limit)

@router.post("/admin/approve/{request_id}")
async def approve_payment(
    request_id: int,
    current_user: User = Depends(require_permission("approve_payment"))
):
    success = await WalletService.approve_payment_request(request_id, current_user.telegram_id)
    if not success:
        raise HTTPException(status_code=404, detail="Request not found or already processed")
    return {"message": "Payment approved"}

@router.post("/admin/reject/{request_id}")
async def reject_payment(
    request_id: int,
    reason: str = Query(...),
    current_user: User = Depends(require_permission("approve_payment"))
):
    success = await WalletService.reject_payment_request(request_id, current_user.telegram_id, reason)
    if not success:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"message": "Payment rejected"}
