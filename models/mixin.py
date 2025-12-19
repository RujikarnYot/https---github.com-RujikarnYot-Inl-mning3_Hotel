
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    create_at: Mapped[datetime] = mapped_column(default=datetime.now)
    update_at: Mapped[Optional[datetime]] = mapped_column(default=None, onupdate=datetime.now)

class SoftDeletionMixin:
    is_delete: Mapped[bool] = mapped_column(Boolean, default=False)

    def soft_delete(self):
        self.is_delete = True

    def restore(self):
        self.is_delete = False