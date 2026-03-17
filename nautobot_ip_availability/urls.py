"""Django urlpatterns declaration for nautobot_ip_availability app."""

from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView

from nautobot_ip_availability import views

app_name = "nautobot_ip_availability"

urlpatterns = [
    path("", views.PrefixAvailabilityView.as_view(), name="prefix_availability"),
    path("docs/", RedirectView.as_view(url=static("nautobot_ip_availability/docs/index.html")), name="docs"),
]
