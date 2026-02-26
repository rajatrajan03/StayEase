from django.urls import path
from . import views

urlpatterns = [
    path("", views.booking_list, name="booking_list"),
    path("create/<int:room_id>/", views.create_booking, name="create_booking"),
    path("update/<int:booking_id>/<str:status>/", views.update_booking_status, name="update_booking_status"),
    path("book-room/<int:room_id>/", views.book_room, name="book_room"),]