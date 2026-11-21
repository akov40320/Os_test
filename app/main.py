from fastapi import FastAPI

from app.api.bookings import router as bookings_router
from app.repositories.memory_booking_repository import MemoryBookingRepository
from app.services.booking_service import BookingService


def create_app() -> FastAPI:
    app = FastAPI(title="Бронирование столиков")
    app.state.booking_service = BookingService(MemoryBookingRepository())
    app.include_router(bookings_router)
    return app


app = create_app()
