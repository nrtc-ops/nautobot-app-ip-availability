"""Views for nautobot_ip_availability."""

from django.shortcuts import render
from django_tables2 import RequestConfig

from nautobot.apps.views import GenericView

from nautobot_ip_availability.forms import PrefixAvailabilityForm
from nautobot_ip_availability.tables import AvailablePrefixTable
from nautobot_ip_availability.utils import get_available_prefixes_for_parent


class PrefixAvailabilityView(GenericView):
    """View for querying available IP prefixes within a parent prefix."""

    def get(self, request):
        """Render the empty query form."""
        form = PrefixAvailabilityForm()
        return render(request, "nautobot_ip_availability/prefix_availability.html", {"form": form})

    def post(self, request):
        """Process the form and display available prefixes."""
        form = PrefixAvailabilityForm(request.POST)
        table = None
        result_count = 0
        truncated = False

        if form.is_valid():
            parent_prefix = form.cleaned_data["parent_prefix"]
            prefix_lengths = form.cleaned_data["prefix_lengths"]

            results, truncated = get_available_prefixes_for_parent(
                parent_prefix=parent_prefix,
                prefix_lengths=prefix_lengths,
            )
            result_count = len(results)
            table = AvailablePrefixTable(results)
            table.configure(request)

        return render(
            request,
            "nautobot_ip_availability/prefix_availability.html",
            {
                "form": form,
                "table": table,
                "result_count": result_count,
                "truncated": truncated,
            },
        )
