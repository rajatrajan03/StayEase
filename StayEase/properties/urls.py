from django.urls import path
from . import views

urlpatterns = [
    path("", views.property_list, name="property_list"),
    path("add/", views.add_property, name="add_property"),
    path("edit/<int:pk>/", views.edit_property, name="edit_property"),
    path("archive/<int:pk>/", views.archive_property, name="archive_property"),
    path("restore/<int:pk>/", views.restore_property, name="restore_property"),
    path("<int:property_id>/add-room/", views.add_room, name="add_room"),
    path("<int:pk>/", views.property_detail, name="property_detail"),
    path("<int:pk>/payment/", views.property_payment, name="property_payment"),
    path("browse/", views.tenant_property_list, name="tenant_property_list"),
    path("browse/<int:pk>/", views.tenant_property_detail, name="tenant_property_detail"),
    path("room/<int:pk>/", views.room_detail, name="room_detail"),
    path("room/edit/<int:room_id>/", views.edit_room, name="edit_room"),
    path("room/delete/<int:room_id>/", views.delete_room, name="delete_room"),
]