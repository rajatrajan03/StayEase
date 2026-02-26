from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Min
from .models import Property, Room
from .forms import PropertyForm, RoomForm
from payments.models import PropertyPayment
from bookings.models import Booking
from django.contrib import messages

# Property_List
@login_required
def property_list(request):
    properties = Property.objects.filter(owner=request.user)
    property_data = []

    for prop in properties:
        rooms = prop.rooms.all()

        min_rent = None
        if rooms.exists():
            min_rent = rooms.order_by("rent").first().rent

        property_data.append({
            "property": prop,
            "min_rent": min_rent,
            "room_count": rooms.count(),
        })

    context = {
        "property_data": property_data,
    }

    return render(request, "properties/property_list.html", context)

# Add_Property
@login_required
def add_property(request):
    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.owner = request.user
            
            property_obj.is_active = False
            property_obj.is_paid_listing = False
            property_obj.save()
            return redirect("property_payment", pk=property_obj.id)
    else:
        form = PropertyForm()

    return render(request, "properties/add_property.html", {"form": form})


# Edit_Property
@login_required
def edit_property(request, pk):
    property_obj = get_object_or_404(
        Property,
        pk=pk,
        owner=request.user
    )

    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            form.save()
            return redirect("property_list")
    else:
        form = PropertyForm(instance=property_obj)

    return render(request, "properties/add_property.html", {"form": form})

# Archive_Property
@login_required
def archive_property(request, pk):
    property_obj = get_object_or_404(
        Property,
        pk=pk,
        owner=request.user
    )

    property_obj.is_active = False
    property_obj.save()

    return redirect("property_list")


# Restore_Property
@login_required
def restore_property(request, pk):
    property_obj = get_object_or_404(
        Property,
        pk=pk,
        owner=request.user
    )

    property_obj.is_active = True
    property_obj.is_paid_listing = True  
    property_obj.save()

    return redirect("property_list")


# Add_Room
@login_required
def add_room(request, property_id):
    property_obj = get_object_or_404(
        Property,
        id=property_id,
        owner=request.user
    )

    if request.method == "POST":
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save(commit=False)
            room.property = property_obj
            room.save()
            return redirect("property_list")
    else:
        form = RoomForm()

    return render(request, "properties/add_room.html", {
        "form": form,
        "property": property_obj
    })

# Property_Detail
@login_required
def property_detail(request, pk):
    property_obj = get_object_or_404(
        Property,
        pk=pk,
        owner=request.user
    )
    rooms = property_obj.rooms.all()

    # Dynamic seat calculation
    for room in rooms:
        confirmed_count = Booking.objects.filter(
            room=room,
            status="confirmed"
        ).count()

        room.confirmed = confirmed_count
        room.available_seats = room.capacity - confirmed_count

    return render(request, "properties/property_detail.html", {
        "property": property_obj,
        "rooms": rooms,
    })
    

# Property_Payment
@login_required
def property_payment(request, pk):
    property_obj = get_object_or_404(Property, pk=pk, owner=request.user)

    if request.method == "POST":
        PropertyPayment.objects.create(
            owner=request.user,
            property=property_obj,
            amount=1000,
            status="Success"
        )

        property_obj.is_paid_listing = True
        property_obj.is_active = True
        property_obj.save()

        return redirect("property_list")

    return render(request, "properties/property_payment.html", {
        "property": property_obj
    })
    
# Tenant_Property_List
@login_required
def tenant_property_list(request):
    properties = Property.objects.filter(
        is_active=True,
        is_paid_listing=True
    )

    property_data = []

    for prop in properties:
        rooms = prop.rooms.all()

        min_rent = None
        if rooms.exists():
            min_rent = rooms.order_by("rent").first().rent

        property_data.append({
            "property": prop,
            "min_rent": min_rent,
            "room_count": rooms.count(),
        })

    return render(request, "properties/tenant_property_list.html", {
        "property_data": property_data
    })


# Tenant_Property_Detail
@login_required
def tenant_property_detail(request, pk):
    property_obj = get_object_or_404(
        Property,
        pk=pk,
        is_active=True,
        is_paid_listing=True
    )

    rooms = property_obj.rooms.all()

    for room in rooms:
        confirmed_count = Booking.objects.filter(
            room=room,
            status="confirmed"
        ).count()

        room.confirmed = confirmed_count
        room.available_seats = room.capacity - confirmed_count

    return render(request, "properties/tenant_property_detail.html", {
        "property": property_obj,
        "rooms": rooms,
    })
    
# Room_Detail
@login_required
def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)

    confirmed_count = Booking.objects.filter(
        room=room,
        status="confirmed"
    ).count()

    available_seats = room.capacity - confirmed_count

    return render(request, "properties/room_detail.html", {
        "room": room,
        "available_seats": available_seats
    })

# Edit_Room
@login_required
def edit_room(request, room_id):
    
    # Only property owner can edit
    room = get_object_or_404(
        Room,
        id=room_id,
        property__owner=request.user
    )

    if request.method == "POST":
        room.room_number = request.POST.get("room_number")
        room.rent = request.POST.get("rent")
        room.capacity = request.POST.get("capacity")
        room.description = request.POST.get("description")

        if request.FILES.get("image"):
            room.image = request.FILES.get("image")

        room.save()

        messages.success(request, "Room updated successfully!")
        return redirect("property_detail", pk=room.property.id)

    return render(request, "properties/edit_room.html", {
        "room": room
    })

# Delete_Room
@login_required
def delete_room(request, room_id):
    room = get_object_or_404(
        Room,
        id=room_id,
        property__owner=request.user
    )

    if request.method == "POST":
        property_id = room.property.id
        room.delete()
        messages.success(request, "Room deleted successfully!")
        return redirect("property_detail", pk=property_id)

    return redirect("property_detail", pk=room.property.id)