from datetime import date
from threading import Lock

from app.schemas import BookingCreate, BookingOut


class SlotAlreadyBookedError(Exception):
    pass


class MemoryBookingRepository:
    def __init__(self):
        self._bookings: dict[int, BookingOut] = {}
        self._next_id = 1
        self._lock = Lock()

    def create(self, data: BookingCreate) -> BookingOut:
        with self._lock:
            # Проверку и создание держим вместе под блокировкой:
            # так два одновременных запроса не займут один слот.
            for booking in self._bookings.values():
                same_slot = (
                    booking.booking_date == data.booking_date
                    and booking.booking_time == data.booking_time
                )
                if same_slot and booking.status == "active":
                    raise SlotAlreadyBookedError

            booking = BookingOut(
                id=self._next_id,
                **data.model_dump(),
                status="active",
            )
            self._bookings[self._next_id] = booking
            self._next_id += 1
            return booking.model_copy(deep=True)

    def get(self, booking_id: int) -> BookingOut | None:
        with self._lock:
            booking = self._bookings.get(booking_id)
            return booking.model_copy(deep=True) if booking else None

    def get_all(self, booking_date: date | None = None) -> list[BookingOut]:
        with self._lock:
            bookings = [
                booking
                for booking in self._bookings.values()
                if booking_date is None or booking.booking_date == booking_date
            ]
            bookings.sort(key=lambda item: (item.booking_date, item.booking_time))
            return [booking.model_copy(deep=True) for booking in bookings]

    def cancel(self, booking_id: int) -> BookingOut | None:
        with self._lock:
            booking = self._bookings.get(booking_id)
            if booking is None:
                return None

            cancelled_booking = booking.model_copy(update={"status": "cancelled"})
            self._bookings[booking_id] = cancelled_booking
            return cancelled_booking.model_copy(deep=True)
