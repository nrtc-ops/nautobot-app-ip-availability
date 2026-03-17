"""Django API urlpatterns declaration for nautobot_ip_availability app."""

from django.urls import path

from nautobot_ip_availability.api import views

app_name = "nautobot_ip_availability-api"

urlpatterns = [
    path("available-prefixes/", views.AvailablePrefixesAPIView.as_view(), name="available_prefixes"),
]
