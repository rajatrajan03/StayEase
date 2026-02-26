# 🏠 StayEase -- Smart Room Booking Platform

StayEase is a role-based room booking platform built using Django.\
It connects property owners and tenants through a secure digital system
where owners can list properties and tenants can book rooms easily.

------------------------------------------------------------------------

## 🚀 Project Vision

StayEase simplifies room rentals by:

-   Helping owners manage properties efficiently
-   Allowing tenants to find and book rooms easily
-   Providing secure authentication and dashboards
-   Supporting a listing fee business model

------------------------------------------------------------------------

## 👥 User Roles

### Owner

-   Add properties and rooms
-   Manage bookings
-   View tenant details
-   Monitor dashboard data
-   Pay listing fee

### Tenant

-   Browse available rooms
-   View property details
-   Book rooms
-   Track booking status
-   Access personal dashboard

------------------------------------------------------------------------

## 🏗️ Project Structure

stayease/ │ ├── accounts/ ├── properties/ ├── bookings/ ├── payments/
├── dashboard/ ├── templates/ ├── static/ ├── media/ └── manage.py

------------------------------------------------------------------------

## 🔐 Authentication Features

-   Django authentication system
-   Django Allauth integration
-   Email-based login
-   Google & GitHub login
-   Role-based access

------------------------------------------------------------------------

## 💳 Business Model

-   Property owners pay a listing fee
-   Helps maintain platform sustainability

------------------------------------------------------------------------

## 🛠️ Tech Stack

-   Python
-   Django
-   SQLite
-   HTML / CSS / Bootstrap
-   Django Allauth
-   SMTP Email Integration

------------------------------------------------------------------------

## ⚙️ Installation

Clone repository:

git clone https://github.com/yourusername/stayease.git cd stayease

Create environment:

python -m venv venv venv`\Scripts`{=tex}`\activate`{=tex}

Install dependencies:

pip install -r requirements.txt

Create `.env`:

SECRET_KEY=your_secret_key DEBUG=True EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_password

Run:

python manage.py migrate python manage.py createsuperuser python
manage.py runserver

------------------------------------------------------------------------

## 📊 Features

-   Role-based dashboards
-   Property & booking management
-   Listing fee system
-   Social login
-   Email notifications
-   Secure configuration

------------------------------------------------------------------------

## 🔮 Future Scope

-   Payment gateway integration
-   AI recommendations
-   Reviews & ratings
-   Mobile app API
-   Cloud deployment

------------------------------------------------------------------------

## 📌 Author

Rajat\
Django Developer

------------------------------------------------------------------------

## 🌟 Final Note

StayEase is a complete room booking platform built with Django, designed
to simplify property listing and room booking through a secure and
scalable system.
