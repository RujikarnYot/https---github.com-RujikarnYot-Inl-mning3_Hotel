
from datetime import date
from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy import Enum as SqlEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base,int_pk
from models.mixin import SoftDeletionMixin, TimestampMixin

if TYPE_CHECKING:
    from models.invoice import Invoice
    from models.room import Rooms

class StatusEnum(Enum):
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

class Booking(Base,TimestampMixin,SoftDeletionMixin):
    __tablename__="booking"

    id: Mapped[int_pk]
    check_in: Mapped[date] = mapped_column(nullable=False)
    check_out: Mapped[date] = mapped_column(nullable=False)
    total_guest: Mapped[date] = mapped_column(nullable=False)
    extra_bed: Mapped[int] = mapped_column(default=0)
    status: Mapped[StatusEnum] = mapped_column(SqlEnum(StatusEnum, name="statusenum"), default=StatusEnum.ACTIVE)
    booking_date: Mapped[date]

    customer_id: Mapped[str] = mapped_column(String(36),ForeignKey("customers.id"))
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))

    invoice: Mapped["Invoice"] = relationship(back_populates="booking",uselist=False)
    room: Mapped["Rooms"] = relationship(back_populates="bookings")

    def __repr__(self) -> str:
        return f"customer:{self.customer_id}, booking date:{self.booking_date}, room:{self.room_id}, check-in:{self.check_in}, check-out:{self.check_out}, guest:{self.total_guest}, status:{self.status}"