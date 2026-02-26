from django.shortcuts import render
from django.db.models import Sum
from bookings.models import Booking
from django.contrib.auth import logout
from django.shortcuts import redirect
from datetime import datetime
import calendar

# Owner_Dashboard
def owner_dashboard(request):

    # Only confirmed bookings 
    bookings = Booking.objects.filter(
        room__property__owner=request.user,
        status="confirmed"
    )

    total_properties = request.user.properties.count()
    total_bookings = bookings.count()
    total_earnings = bookings.aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    active_listings = request.user.properties.filter(
        is_active=True
    ).count()

    # Current Year only
    current_year = datetime.now().year
    year_bookings = bookings.filter(created_at__year=current_year)

    months = [calendar.month_abbr[i] for i in range(1, 13)]
    revenues = [0] * 12
    booking_counts = [0] * 12

    for booking in year_bookings:
        month_index = booking.created_at.month - 1
        revenues[month_index] += float(booking.total_amount)
        booking_counts[month_index] += 1

    # Pending booking requests for approval
    pending_bookings = Booking.objects.filter(
        room__property__owner=request.user,
        status="pending"
    )

    context = {
        'total_properties': total_properties,
        'total_bookings': total_bookings,
        'total_earnings': total_earnings,
        'active_listings': active_listings,
        'months': months,
        'revenues': revenues,
        'booking_counts': booking_counts,
        'recent_bookings': bookings.order_by('-created_at')[:5],
        'pending_bookings': pending_bookings,
    }

    return render(request, 'dashboard/owner_dashboard.html', context)

# Logout_View
def logout_view(request):
    logout(request)
    return redirect('login')   


