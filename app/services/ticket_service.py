import logging
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, func, and_, or_
from app.core.database import async_session_maker
from app.models.ticket import Ticket, TicketMessage, TicketCategory, TicketStatus, TicketPriority
from app.models.user import User

logger = logging.getLogger(__name__)

class TicketService:
    
    @staticmethod
    async def create_ticket(telegram_id: int, subject: str, message: str, 
                            category_id: Optional[int] = None, priority: str = "medium") -> Optional[Ticket]:
        async with async_session_maker() as session:
            # Generate ticket number
            last_ticket = await session.execute(select(func.max(Ticket.id)))
            last_id = last_ticket.scalar() or 0
            ticket_number = f"T{last_id+1:06d}"
            
            ticket = Ticket(
                ticket_number=ticket_number,
                user_id=telegram_id,
                category_id=category_id,
                subject=subject,
                status=TicketStatus.OPEN,
                priority=TicketPriority(priority)
            )
            session.add(ticket)
            await session.commit()
            await session.refresh(ticket)
            
            # Add first message
            msg = TicketMessage(
                ticket_id=ticket.id,
                user_id=telegram_id,
                message=message,
                is_admin=False
            )
            session.add(msg)
            await session.commit()
            
            # Update user ticket count
            await session.execute(
                update(User).where(User.telegram_id == telegram_id).values(total_tickets=User.total_tickets + 1)
            )
            await session.commit()
            
            return ticket
    
    @staticmethod
    async def add_message(ticket_id: int, user_id: int, message: str, is_admin: bool = False) -> Optional[TicketMessage]:
        async with async_session_maker() as session:
            ticket = await session.get(Ticket, ticket_id)
            if not ticket:
                return None
            
            msg = TicketMessage(
                ticket_id=ticket_id,
                user_id=user_id,
                message=message,
                is_admin=is_admin
            )
            session.add(msg)
            
            # Update ticket status
            if is_admin:
                ticket.status = TicketStatus.IN_PROGRESS
            else:
                if ticket.status == TicketStatus.WAITING_CUSTOMER:
                    ticket.status = TicketStatus.IN_PROGRESS
            
            await session.commit()
            await session.refresh(msg)
            return msg
    
    @staticmethod
    async def get_ticket(ticket_id: int) -> Optional[Ticket]:
        async with async_session_maker() as session:
            return await session.get(Ticket, ticket_id)
    
    @staticmethod
    async def get_user_tickets(telegram_id: int, limit: int = 20) -> List[Ticket]:
        async with async_session_maker() as session:
            stmt = select(Ticket).where(Ticket.user_id == telegram_id)\
                .order_by(Ticket.created_at.desc()).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()
    
    @staticmethod
    async def get_all_tickets(status: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Ticket]:
        async with async_session_maker() as session:
            stmt = select(Ticket)
            if status:
                stmt = stmt.where(Ticket.status == status)
            stmt = stmt.order_by(Ticket.created_at.desc()).offset(offset).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()
    
    @staticmethod
    async def assign_ticket(ticket_id: int, admin_id: int) -> bool:
        async with async_session_maker() as session:
            ticket = await session.get(Ticket, ticket_id)
            if not ticket:
                return False
            ticket.assign(admin_id)
            await session.commit()
            return True
    
    @staticmethod
    async def close_ticket(ticket_id: int, closed_by_id: int) -> bool:
        async with async_session_maker() as session:
            ticket = await session.get(Ticket, ticket_id)
            if not ticket:
                return False
            ticket.close(closed_by_id)
            await session.commit()
            return True
    
    @staticmethod
    async def get_ticket_messages(ticket_id: int, limit: int = 50) -> List[Dict]:
        async with async_session_maker() as session:
            stmt = select(TicketMessage).where(TicketMessage.ticket_id == ticket_id)\
                .order_by(TicketMessage.created_at).limit(limit)
            result = await session.execute(stmt)
            msgs = result.scalars().all()
            return [{
                "id": m.id,
                "user_id": m.user_id,
                "message": m.message,
                "is_admin": m.is_admin,
                "created_at": m.created_at.isoformat()
            } for m in msgs]
    
    @staticmethod
    async def get_categories() -> List[TicketCategory]:
        async with async_session_maker() as session:
            stmt = select(TicketCategory).where(TicketCategory.is_active == True).order_by(TicketCategory.sort_order)
            result = await session.execute(stmt)
            return result.scalars().all()
