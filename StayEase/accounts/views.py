from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db import transaction, DatabaseError
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from datetime import date
from .models import UserProfile, PasswordResetToken, Notification
from bookings.models import Booking
from properties.models import Property, Room
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash

# HOME
def home(request):
    return render(request, "home.html")


# SIGNUP
def signup(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        email = (request.POST.get("email") or "").strip().lower()
        password = request.POST.get("password")
        role = request.POST.get("role") or "tenant"

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already exists")
            return render(request, "accounts/signup.html")
        
        if not request.POST.get("agree_terms"):
            messages.error(request, "You must agree to Terms & Privacy Policy")
            return render(request, "accounts/signup.html")

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=full_name
                )

                UserProfile.objects.create(
                    user=user,
                    phone=phone,
                    role=role
                )
        except DatabaseError:
            messages.error(request, "Signup is temporarily unavailable. Please try again in a minute.")
            return render(request, "accounts/signup.html")

        user = authenticate(request, username=email, password=password)
        if user is None:
            messages.success(request, "Account created successfully. Please log in.")
            return redirect("login")

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect("dashboard")
    return render(request, "accounts/signup.html")

# LOGIN
def login_view(request):
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        password = (request.POST.get("password") or "").strip()

        if not email or not password:
            messages.error(request, "Please enter both email and password")
            return render(request, "accounts/login.html")

        user = authenticate(request, username=email, password=password)

        if user is None:
            # Fallback: if username is not exactly the email string, resolve by email first.
            existing_user = User.objects.filter(email__iexact=email).first()
            if existing_user:
                user = authenticate(request, username=existing_user.username, password=password)

        if user is not None:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid email or password")
            return render(request, "accounts/login.html")

    return render(request, "accounts/login.html")


@login_required(login_url="login")
def dashboard(request):

    profile = request.user.userprofile
    if profile.role == "owner":

        properties = Property.objects.filter(owner=request.user)
        bookings = Booking.objects.filter(room__property__owner=request.user)
        pending_count = bookings.filter(status="pending").count()
        
        total_properties = properties.count()
        total_bookings = bookings.count()

        # ✅ FIXED LINE
        total_earnings = bookings.filter(status="confirmed").aggregate(
            total=Sum("rent_amount")
        )["total"] or 0

        # Monthly revenue
        current_month = now().month
        monthly_revenue = bookings.filter(
            created_at__month=current_month,
            status="confirmed"
        ).aggregate(total=Sum("rent_amount"))["total"] or 0

        recent_bookings = bookings.order_by("-created_at")[:5]

        return render(request, "dashboard/owner_dashboard.html", {
            "total_properties": total_properties,
            "total_bookings": total_bookings,
            "total_earnings": total_earnings,
            "monthly_revenue": monthly_revenue,
            "recent_bookings": recent_bookings,
            "active_listings": properties.filter(is_active=True).count(),
            "pending_count": pending_count,
            "active_page": "overview"
        })

    else:

        bookings = Booking.objects.filter(tenant=request.user)

        total_earnings = bookings.filter(status="confirmed").aggregate(
            total=Sum("rent_amount")
        )["total"] or 0

        context = {
            "bookings": bookings,
            "total_bookings": bookings.count(),
            "confirmed_bookings": bookings.filter(status="confirmed").count(),
            "total_earnings": total_earnings,
        }

        return render(request, "dashboard/tenant_dashboard.html", context)

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Email not found")
            return render(request, "accounts/forgot_password.html")

        PasswordResetToken.objects.filter(user=user).delete()
        token_obj = PasswordResetToken.objects.create(user=user)

        reset_link = f"http://127.0.0.1:8000/reset-password/{token_obj.token}/"

        send_mail(
            "Reset Your StayEase Password",
            f"Click below link:\n{reset_link}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=True,
        )

        messages.success(request, "Reset link sent to your email")
        return render(request, "accounts/forgot_password.html")

    return render(request, "accounts/forgot_password.html")


def reset_password(request, token):
    try:
        token_obj = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        return render(request, "accounts/reset_password.html", {"error": "Invalid or expired link"})

    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(request, "accounts/reset_password.html", {"error": "Passwords do not match"})

        user = token_obj.user
        user.password = make_password(password)
        user.save()

        token_obj.delete()
        return redirect("login")

    return render(request, "accounts/reset_password.html")

def terms(request):
    return render(request, "accounts/terms.html")

def privacy(request):
    return render(request, "accounts/privacy.html")

from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch


def download_terms_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="StayEase_Terms_of_Service_Enterprise.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=60,
        bottomMargin=40
    )

    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("StayEase Terms of Service", styles["Heading1"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Effective Date: 20 February 2026", styles["Normal"]))
    elements.append(Spacer(1, 24))

    sections = [
        ("1. Introduction",
         """StayEase is a technology-driven digital marketplace that enables property owners to list rental properties and allows tenants to discover and book accommodations.
         These Terms of Service ("Terms") govern your access to and use of StayEase services, website, mobile interfaces, and related features.
         By accessing or using StayEase, you acknowledge that you have read, understood, and agreed to these Terms."""),

        ("2. Definitions",
         """“Platform” refers to the StayEase website and associated services.
         “User” refers to any individual or entity accessing the platform.
         “Owner” refers to users listing properties.
         “Tenant” refers to users booking properties."""),

        ("3. Eligibility and Account Registration",
         """Users must be at least 18 years of age and legally capable of entering binding agreements.
         Users agree to provide accurate, current, and complete information.
         StayEase reserves the right to suspend accounts that provide misleading or false data."""),

        ("4. Platform Role and Disclaimer",
         """StayEase acts solely as an intermediary technology platform.
         StayEase does not own, control, manage, or inspect listed properties.
         Rental agreements are formed directly between Owners and Tenants.
         StayEase is not responsible for property conditions, disputes, or contract breaches."""),

        ("5. User Responsibilities",
         """Users agree to use the platform lawfully and ethically.
         Owners must provide accurate property descriptions, pricing, and availability.
         Tenants agree to respect property terms and local laws.
         Misuse of the platform may result in permanent suspension."""),

        ("6. Payments and Financial Terms",
         """Listing fees, booking charges, and service fees may apply.
         Payments are processed via third-party secure payment providers.
         StayEase does not store full credit/debit card information.
         Refund policies are subject to booking terms and applicable laws."""),

        ("7. Cancellation and Refund Policy",
         """Refund eligibility depends on property-specific cancellation terms.
         StayEase may assist in dispute resolution but is not obligated to issue refunds.
         Service fees may be non-refundable unless legally required."""),

        ("8. Intellectual Property",
         """All software, branding, trademarks, content, and design elements belong to StayEase.
         Users may not reproduce, copy, distribute, or reverse engineer any part of the platform."""),

        ("9. Prohibited Activities",
         """Users may not:
         • Engage in fraud or misrepresentation
         • Attempt hacking or unauthorized access
         • Post illegal or discriminatory content
         • Circumvent payment mechanisms"""),

        ("10. Limitation of Liability",
         """To the maximum extent permitted by law, StayEase shall not be liable for indirect, incidental,
         special, consequential, or punitive damages arising from platform use.
         Total liability shall not exceed the amount paid by the user in the preceding 12 months."""),

        ("11. Indemnification",
         """Users agree to indemnify and hold harmless StayEase and its affiliates
         from claims, liabilities, and damages arising from misuse of the platform."""),

        ("12. Data Protection and Privacy",
         """User data is processed in accordance with our Privacy Policy.
         We implement reasonable security measures but cannot guarantee absolute security."""),

        ("13. Force Majeure",
         """StayEase shall not be liable for delays or failure to perform due to events beyond reasonable control,
         including natural disasters, government actions, cyberattacks, or service outages."""),

        ("14. Termination",
         """StayEase may suspend or terminate accounts that violate these Terms.
         Users may delete their accounts at any time."""),

        ("15. Dispute Resolution and Arbitration",
         """Disputes arising under these Terms shall first be attempted to be resolved amicably.
         If unresolved, disputes shall be subject to binding arbitration under applicable Indian laws."""),

        ("16. Governing Law",
         """These Terms shall be governed by the laws of India.
         Courts located in India shall have exclusive jurisdiction."""),

        ("17. Changes to Terms",
         """StayEase reserves the right to modify these Terms at any time.
         Continued use after updates constitutes acceptance of revised Terms."""),
    ]

    for title, content in sections:
        elements.append(Paragraph(title, styles["Heading2"]))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(content.replace("\n", "<br/>"), styles["Normal"]))
        elements.append(Spacer(1, 14))

    doc.build(elements)
    return response


def download_privacy_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="StayEase_Privacy_Policy_Enterprise.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("StayEase Privacy Policy", styles["Heading1"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Effective Date: 20 February 2026", styles["Normal"]))
    elements.append(Spacer(1, 24))

    sections = [
        ("1. Introduction",
         "StayEase is committed to protecting user privacy and personal data."),

        ("2. Information We Collect",
         """We collect:
         • Personal Data (name, email, phone)
         • Booking Data
         • Payment confirmations
         • Device & browser information"""),

        ("3. Legal Basis for Processing",
         """We process personal data based on:
         • User consent
         • Contractual necessity
         • Legal compliance
         • Legitimate business interests"""),

        ("4. How We Use Data",
         """Data is used for:
         • Account management
         • Booking processing
         • Fraud prevention
         • Platform improvement"""),

        ("5. Data Sharing",
         """We may share data with:
         • Property Owners
         • Payment processors
         • Regulatory authorities (if required by law)"""),

        ("6. International Transfers",
         "Data may be processed in jurisdictions with different data protection laws."),

        ("7. Data Retention",
         "Personal data is retained only as long as necessary for business and legal obligations."),

        ("8. Security Measures",
         "We implement administrative, technical, and physical safeguards."),

        ("9. User Rights",
         """Users may:
         • Request access
         • Request correction
         • Request deletion
         • Withdraw consent"""),

        ("10. Cookies and Tracking",
         "Cookies are used for analytics and improving user experience."),

        ("11. Children’s Privacy",
         "StayEase is not intended for individuals under 18 years of age."),

        ("12. Changes to Privacy Policy",
         "We may update this Privacy Policy periodically."),

        ("13. Contact Information",
         "For privacy inquiries: support@stayease.com"),
    ]

    for title, content in sections:
        elements.append(Paragraph(title, styles["Heading2"]))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(content.replace("\n", "<br/>"), styles["Normal"]))
        elements.append(Spacer(1, 14))

    doc.build(elements)
    return response

@login_required
def profile_view(request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        total_properties = 0
        total_bookings = 0
        total_earnings = 0
        total_security = 0
        active_listings = 0
        pending_bookings = 0
        confirmed_bookings = 0
        occupancy_rate = 0

        # ---------------- OWNER ----------------
        if profile.role == "owner":

            properties = Property.objects.filter(owner=request.user)
            bookings = Booking.objects.filter(room__property__owner=request.user)
            rooms = Room.objects.filter(property__owner=request.user)

            total_properties = properties.count()
            total_bookings = bookings.count()

            total_earnings = bookings.filter(status="confirmed").aggregate(
                total=Sum("rent_amount")
            )["total"] or 0

            total_security = bookings.filter(status="confirmed").aggregate(
                total=Sum("security_amount")
            )["total"] or 0

            active_listings = properties.filter(is_active=True).count()

            pending_bookings = bookings.filter(status="pending").count()
            confirmed_bookings = bookings.filter(status="confirmed").count()

            total_capacity = sum(room.capacity for room in rooms)

            if total_capacity > 0:
                occupancy_rate = round((confirmed_bookings / total_capacity) * 100)

        # ---------------- TENANT ----------------
        else:

            bookings = Booking.objects.filter(tenant=request.user)

            tenant_total_bookings = bookings.count()
            tenant_pending = bookings.filter(status="pending").count()
            tenant_confirmed = bookings.filter(status="confirmed").count()

            tenant_total_paid = bookings.filter(status="confirmed").aggregate(
                total=Sum("total_amount")
            )["total"] or 0

            return render(request, "dashboard/profile_view.html", {
                "profile": profile,
                "tenant_total_bookings": tenant_total_bookings,
                "tenant_pending": tenant_pending,
                "tenant_confirmed": tenant_confirmed,
                "tenant_total_paid": tenant_total_paid,
                "active_page": "profile"
            })

        # OWNER RENDER
        return render(request, "dashboard/profile_view.html", {
            "profile": profile,
            "total_properties": total_properties,
            "total_bookings": total_bookings,
            "total_earnings": total_earnings,
            "total_security": total_security,
            "active_listings": active_listings,
            "pending_bookings": pending_bookings,
            "confirmed_bookings": confirmed_bookings,
            "occupancy_rate": occupancy_rate,
            "active_page": "profile"
        })
        
# 🔹 SETTINGS (Edit Profile)

@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":

        # =============================
        # 🔹 Password Change Logic
        # =============================
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if old_password or new_password or confirm_password:

            # Check all fields filled
            if not old_password or not new_password or not confirm_password:
                messages.error(request, "Please fill all password fields.")
                return redirect("settings")

            # Verify old password
            if not request.user.check_password(old_password):
                messages.error(request, "Old password is incorrect.")
                return redirect("settings")

            # Match new passwords
            if new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
                return redirect("settings")

            # Set new password
            request.user.set_password(new_password)
            request.user.save()

            # Keep user logged in
            update_session_auth_hash(request, request.user)

            messages.success(request, "Password changed successfully!")
            return redirect("settings")

        # =============================
        # 🔹 Profile Info Update
        # =============================
        request.user.first_name = request.POST.get("first_name")
        request.user.last_name = request.POST.get("last_name")
        request.user.email = request.POST.get("email")

        profile.phone = request.POST.get("phone")

        # =============================
        # 🔹 Profile Image Upload
        # =============================
        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES.get("profile_image")
            messages.success(request, "Profile image uploaded successfully!")
        else:
            messages.success(request, "Changes saved successfully!")

        request.user.save()
        profile.save()

        return redirect("settings")

    return render(request, "accounts/profile.html", {
        "profile": profile,
        "active_page": "profile"
    })
    
def logout_view(request):
    logout(request)
    return redirect("home")


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

    # 🔔 Notify Owner every time new booking request created
    Notification.objects.create(
        user=room.property.owner,
        message=f"New booking request for Room {room.room_number} by {request.user.first_name}"
    )

    messages.success(
        request,
        "Booking request sent. Waiting for owner approval."
    )

    return redirect("tenant_property_detail", pk=room.property.id)

@login_required
def mark_notifications_read(request):
    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)

    return JsonResponse({"status": "ok"})