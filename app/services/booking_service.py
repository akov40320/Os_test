from datetime import date

from fastapi import HTTPException

from app.repositories.memory_booking_repository import (
    MemoryBookingRepository,
    SlotAlreadyBookedError,
)
from app.schemas import BookingCreate, BookingOut


class BookingService:
    def __init__(self, repository: MemoryBookingRepository):
        self.repository = repository

    def create_booking(self, data: BookingCreate) -> BookingOut:
        try:
            return self.repository.create(data)
        except SlotAlreadyBookedError:
            raise HTTPException(
                status_code=409,
                detail="Slot is already booked",
            )

    def get_bookings(self, booking_date: date | None = None) -> list[BookingOut]:
        return self.repository.get_all(booking_date)

    def get_booking(self, booking_id: int) -> BookingOut:
        booking = self.repository.get(booking_id)
        if booking is None:
            raise HTTPException(status_code=404, detail="Booking not found")
        return booking

    def cancel_booking(self, booking_id: int) -> BookingOut:
        booking = self.repository.cancel(booking_id)
        if booking is None:
            raise HTTPException(status_code=404, detail="Booking not found")
        return booking
