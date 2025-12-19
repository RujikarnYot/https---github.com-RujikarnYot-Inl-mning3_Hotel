
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import DECIMAL,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, int_pk, str_255


if TYPE_CHECKING:
    from models.booking import Booking
class PaidEnum(Enum):
    PAID ="PAID"
    UNPAID = "UNPAID"

class Invoice (Base):
    __tablename__="invoices"

    id: Mapped[int_pk]
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10,2), nullable=False)
    duedate:  Mapped[date] = mapped_column(nullable=False)
    is_paid: Mapped[PaidEnum] = mapped_column(SqlEnum(PaidEnum, name="paidenum"), default=PaidEnum.UNPAID, nullable=False)
    paid_date: Mapped[Optional[date]]= mapped_column(nullable=True, default=None)
    paid_by: Mapped[Optional[str_255]]= mapped_column(nullable=True, default=None)

    booking_id: Mapped[int] = mapped_column(ForeignKey("booking.id"))

    booking:Mapped["Booking"] = relationship(back_populates="invoice")

    def __repr__(self) -> str:
        return f"{self.id} amount:{self.amount} duedate:{self.duedate} ({self.is_paid}) paid date:{self.paid_date}"