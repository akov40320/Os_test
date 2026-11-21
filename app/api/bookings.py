from datetime import date

from fastapi import APIRouter, Depends, Query, status

from app.dependencies import get_booking_service
from app.schemas import BookingCreate, BookingOut
from app.services.booking_service import BookingService

router = APIRouter(prefix="/bookings", tags=["Брони"])


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    data: BookingCreate,
    service: BookingService = Depends(get_booking_service),
) -> BookingOut:
    return service.create_booking(data)


@router.get("", response_model=list[BookingOut])
def get_bookings(
    booking_date: date | None = Query(default=None, alias="date"),
    service: BookingService = Depends(get_booking_service),
) -> list[BookingOut]:
    return service.get_bookings(booking_date)


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: int,
    service: BookingService = Depends(get_booking_service),
) -> BookingOut:
    return service.get_booking(booking_id)


@router.delete("/{booking_id}", response_model=BookingOut)
def cancel_booking(
    booking_id: int,
    service: BookingService = Depends(get_booking_service),
) -> BookingOut:
    return service.cancel_booking(booking_id)
