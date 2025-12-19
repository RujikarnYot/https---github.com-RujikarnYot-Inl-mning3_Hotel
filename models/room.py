

from decimal import Decimal
import decimal
from typing import TYPE_CHECKING
from sqlalchemy import DECIMAL, ForeignKey, String
from sqlalchemy.orm import Mapped, relationship, mapped_column
from models.base import Base, int_pk,str_255

if TYPE_CHECKING:
    from models.booking import Booking
    from models.room_type import RoomType

class Rooms(Base):
    __tablename__="rooms"

    id: Mapped[int_pk]
    room_no: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    floor: Mapped[str_255]
    price: Mapped[Decimal] = mapped_column(DECIMAL(10,2), nullable=False)

    room_type_id: Mapped[int] = mapped_column(ForeignKey("room_type.id"), nullable=False)

    room_type: Mapped["RoomType"] = relationship(back_populates="rooms")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="room")

    def __repr__(self) -> str_255:
        return f"room no:{self.room_no} fl:{self.floor} price:{self.price}"