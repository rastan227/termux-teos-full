from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from app.services.user_service import UserService
from app.services.music_service import MusicService
from app.services.service_catalog import ServiceCatalogService
from app.services.ticket_service import TicketService
from app.api.dependencies import require_permission, get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/admin", tags=["admin"])

class UserUpdateRequest(BaseModel):
    role: Optional[str] = None
    is_banned: Optional[bool] = None
    ban_reason: Optional[str] = None
    wallet_balance: Optional[int] = None

@router.get("/stats")
async def admin_stats(current_user: User = Depends(require_permission("view_stats"))):
    user_stats = await UserService.get_user_stats()
    music_stats = await MusicService.get_admin_stats()
    return {
        "users": user_stats,
        "music": music_stats,
        "system": {
            "version": "1.0.0",
            "uptime_seconds": 0  # would be from monitoring
        }
    }

@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(50, le=200),
    role: Optional[str] = None,
    current_user: User = Depends(require_permission("manage_users"))
):
    role_enum = UserRole(role) if role else None
    return await UserService.get_all_users(page, limit, role_enum)

@router.get("/users/{telegram_id}")
async def get_user_detail(
    telegram_id: int,
    current_user: User = Depends(require_permission("manage_users"))
):
    user = await UserService.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.to_dict(include_sensitive=True)

@router.put("/users/{telegram_id}")
async def update_user(
    telegram_id: int,
    data: UserUpdateRequest,
    current_user: User = Depends(require_permission("manage_users"))
):
    if data.role:
        role = UserRole(data.role)
        await UserService.change_role(telegram_id, role, current_user.telegram_id)
    if data.is_banned is not None:
        if data.is_banned:
            await UserService.ban_user(telegram_id, data.ban_reason or "No reason", current_user.telegram_id)
        else:
            await UserService.unban_user(telegram_id, current_user.telegram_id)
    if data.wallet_balance is not None:
        # Admin adjustment
        from app.services.wallet_service import WalletService
        user = await UserService.get_user_by_telegram_id(telegram_id)
        if user:
            diff = data.wallet_balance - user.wallet_balance
            if diff > 0:
                await WalletService.add_balance(telegram_id, diff, "Admin adjustment", tx_type="admin_adjustment")
            elif diff < 0:
                await WalletService.deduct_balance(telegram_id, -diff, "Admin adjustment")
    return {"message": "User updated"}

@router.get("/audit-logs")
async def get_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, le=200),
    current_user: User = Depends(require_permission("view_audit_logs"))
):
    from app.services.audit_service import AuditService
    return await AuditService.get_logs(page, limit)

@router.post("/broadcast")
async def broadcast_message(
    message: str,
    role_filter: Optional[str] = None,
    current_user: User = Depends(require_permission("broadcast"))
):
    from app.services.notification_service import NotificationService
    # In production, use background task
    await NotificationService.broadcast_to_admins(message, role_filter)
    return {"message": "Broadcast sent"}
