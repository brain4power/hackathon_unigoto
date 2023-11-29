from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

# Project
from config import DeclarativeBase

__all__ = [
    "RawData",
]


class RawData(DeclarativeBase):
    __tablename__ = "h_raw_data"

    record_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid(),
    )
    time_created: Mapped[datetime] = mapped_column(default=datetime.now, server_default=func.now())
    time_updated: Mapped[datetime] = mapped_column(
        default=datetime.now,
        onupdate=datetime.now,
        server_default=func.now(),
        server_onupdate=func.now(),
    )
    meta_data: Mapped[dict | None] = mapped_column(JSONB)
    # main data
    page_number: Mapped[int]
    deactivated: Mapped[str]
    country_id: Mapped[int]
    country_title: Mapped[str]
    city_id: Mapped[int]
    city_title: Mapped[str]
    about: Mapped[str]
    activities: Mapped[str]
    books: Mapped[str]
    games: Mapped[str]
    interests: Mapped[str]
    education_form: Mapped[str]
    education_status: Mapped[str]
    university_id: Mapped[int]
    university_name: Mapped[str]
    faculty_id: Mapped[int]
    faculty_name: Mapped[str]
    graduation_year: Mapped[int]
