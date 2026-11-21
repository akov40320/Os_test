from datetime import date, time, timedelta
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class BookingCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    phone: str = Field(pattern=r"^\+7\d{10}$")
    booking_date: date
    booking_time: time
    guests: int = Field(ge=1, le=10)

    @field_validator("name", mode="before")
    @classmethod
    def clean_name(cls, value):
        # Убираем пробелы по краям имени.
        return value.strip() if isinstance(value, str) else value

    @field_validator("booking_date")
    @classmethod
    def check_booking_date(cls, value: date) -> date:
        today = date.today()
        if value < today or value > today + timedelta(days=30):
            raise ValueError("Дата должна быть от сегодняшнего дня до 30 дней вперёд")
        return value

    @field_validator("booking_time")
    @classmethod
    def check_booking_time(cls, value: time) -> time:
        if value.tzinfo is not None:
            raise ValueError("Часовой пояс для времени указывать не нужно")

        if not 12 <= value.hour <= 22:
            raise ValueError("Время должно быть с 12:00 до 22:00")

        if value.minute or value.second or value.microsecond:
            raise ValueError("Можно выбрать только целый час")

        return value


class BookingOut(BaseModel):
    id: int
    name: str
    phone: str
    booking_date: date
    booking_time: time
    guests: int
    status: Literal["active", "cancelled"]
