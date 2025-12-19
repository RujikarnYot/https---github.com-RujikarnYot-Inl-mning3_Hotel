
from datetime import date
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base,uuid_pk,str_255
from models.mixin import SoftDeletionMixin, TimestampMixin

class Customers(Base,TimestampMixin,SoftDeletionMixin):
    __tablename__="customers"

    id: Mapped[uuid_pk]
    first_name: Mapped[str] = mapped_column(String(255), nullable= False)
    last_name: Mapped[str] = mapped_column(String(255), nullable= False)
    birth_date: Mapped[date]
    telephone: Mapped[str_255]
    address: Mapped[str_255]
    email:Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    def __repr__(self):
        return(f"{self.first_name} {self.last_name} born:{self.birth_date} tel:{self.telephone} add: {self.address} email:{self.email}")