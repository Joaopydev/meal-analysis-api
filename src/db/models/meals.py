from datetime import datetime, timezone
from typing import Dict, Any
import uuid
from enum import Enum

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, Enum as SQLEnum, DateTime, JSON

from .base import Base


class MealStatus(Enum):
    uploading = "uploading"
    processing = "processing"
    success = "success"
    failed = "failed"


class InputType(Enum):
    audio = "audio"
    picture = "picture"


class Meal(Base):
    __tablename__ = "meals"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    status: Mapped[MealStatus] = mapped_column(
        SQLEnum(MealStatus),
        default=MealStatus.uploading
    )

    input_type: Mapped[InputType] = mapped_column(SQLEnum(InputType))

    input_file_key: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    icon: Mapped[str] = mapped_column(String(255))

    foods: Mapped[JSON] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        default=lambda: datetime.now(timezone.utc)
    )

    @property
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "status": self.status.value,
            "input_file_key": self.input_file_key,
            "input_type": self.input_type.value,
            "name": self.name,
            "icon": self.icon,
            "foods": self.foods,
            "created_at": self.created_at.isoformat(),
        }