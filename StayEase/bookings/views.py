from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import Notification
from django.shortcuts import render
from properties.models import Room
from django.db.models import Count
from django.contrib import messages
from django.db.models import Sum
from .models import Booking
from django.db import models
from datetime import date

# Booking_List
@login_required
def booking_list(request):
    bookings = Booking.objects.select_related("room", "tenant") \
        .filter(room__property__owner=request.user)
    total_earnings = bookings.filter(status="confirmed") \
        .aggregate(total=Sum("rent_amount"))["total"] or 0 \
        

    total_bookings = bookings.count()
    pending_count = bookings.filter(status="pending").count()
    confirmed_count = bookings.filter(status="confirmed").count()

    # Seats calculation 
    for booking in bookings:
        confirmed = Booking.objects.filter(
            room=booking.room,
            status="confirmed"
        ).count()

        booking.room_confirmed = confirmed
        booking.room_available = booking.room.capacity - confirmed

    context = {
        "bookings": bookings,
        "total_earnings": total_earnings,
        "total_bookings": total_bookings,
        "pending_count": pending_count,
        "confirmed_count": confirmed_count,
    }
    return render(request, "bookings/booking_list.html", context)

# Create_Booking
@login_required
def create_booking(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    # Prevent booking if room not available
    if not room.is_available:
        return redirect("booking_list")

    if request.method == "POST":
        move_in_date = request.POST.get("move_in_date")

        Booking.objects.create(
            room=room,
            tenant=request.user,
            move_in_date=move_in_date
        )

        return redirect("booking_list")

    return redirect("booking_list")

# Update_Booking
@login_required
def update_booking_status(request, booking_id, status):
    # Secure: only owner of property can update
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        room__property__owner=request.user
    )

    room = booking.room

    # Allow only valid statuses
    allowed_status = ["confirmed", "cancelled", "pending"]
    if status not in allowed_status:
        return redirect("booking_list")

    # Update booking status
    booking.status = status
    booking.save()

    # Tenant Notification Logic
    if status == "confirmed":
        Notification.objects.create(
            user=booking.tenant,
            message=f"Your booking for Room {room.room_number} has been approved!"
        )

    elif status == "cancelled":
        Notification.objects.create(
            user=booking.tenant,
            message=f"Your booking for Room {room.room_number} has been cancelled by owner."
        )
        
    # Recalculate confirmed bookings for that room
    confirmed_count = Booking.objects.filter(
        room=room,
        status__iexact="confirmed"
    ).count()

    # Apply capacity logic 
    if confirmed_count >= room.capacity:
        room.is_available = False
    else:
        room.is_available = True

    room.save()

    return redirect("booking_list")

# Book_Room
@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    # Block only if already pending
    pending_exists = Booking.objects.filter(
        tenant=request.user,
        room=room,
        status="pending"
    ).exists()

    if pending_exists:
        messages.warning(
            request,
            "You already have a pending request for this room."
        )
        return redirect("tenant_property_detail", pk=room.property.id)

    # Allow booking even if previously confirmed or cancelled

    booking = Booking.objects.create(
        tenant=request.user,
        room=room,
        move_in_date=date.today(),
        status="pending"
    )

    # Notify Owner every time new booking request created
    Notification.objects.create(
        user=room.property.owner,
        message=f"New booking request for Room {room.room_number} by {request.user.first_name}"
    )

    messages.success(
        request,
        "Booking request sent. Waiting for owner approval."
    )

    return redirect("tenant_property_detail", pk=room.property.id)