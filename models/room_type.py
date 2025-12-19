

from enum import Enum
from typing import TYPE_CHECKING #python enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SqlEnum #sql enum
from .base import Base,int_pk


if TYPE_CHECKING:
    from models.room import Rooms 

class RoomtypeEnum(Enum):
    SINGLE = "SINGLE"
    DOUBLE = "DOUBLE"

class RoomType(Base):
    __tablename__="room_type"

    id: Mapped[int_pk]
    room_type: Mapped[RoomtypeEnum] = mapped_column(SqlEnum(RoomtypeEnum, name="roomtypeenum"), nullable=False)
    extra_bed: Mapped[int] = mapped_column(nullable=False, default=0)
    guest_capacity: Mapped[int] = mapped_column(nullable=False)

    rooms: Mapped[list["Rooms"]] = relationship(back_populates="room_type")

    def __repr__(self) -> str:
        return f"room type:{self.room_type.value}  extra bed:{self.extra_bed}  guest capacity:{self.guest_capacity}"