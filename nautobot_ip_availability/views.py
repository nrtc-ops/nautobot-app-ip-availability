"""Views for nautobot_ip_availability."""

from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone
from nautobot.apps.views import GenericView
from nautobot.extras.models import Status
from nautobot.ipam.models import RIR, Namespace, Prefix

from nautobot_ip_availability.forms import PrefixAvailabilityForm, QuickPrefixCreateForm
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
        results = None
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

        return render(
            request,
            "nautobot_ip_availability/prefix_availability.html",
            {
                "form": form,
                "results": results,
                "result_count": result_count,
                "truncated": truncated,
            },
        )


class QuickPrefixCreateView(GenericView):
    """Guided prefix creation — auto-sets status=Reserved, type=network, rir=ARIN, date_allocated=now."""

    def get(self, request):
        """Show the simplified create form with prefix details."""
        prefix_cidr = request.GET.get("prefix")
        namespace_id = request.GET.get("namespace")

        if not prefix_cidr or not namespace_id:
            messages.error(request, "Missing prefix or namespace parameter.")
            return redirect("plugins:nautobot_ip_availability:prefix_availability")

        try:
            namespace = Namespace.objects.get(pk=namespace_id)
        except (Namespace.DoesNotExist, ValueError):
            messages.error(request, "Invalid namespace.")
            return redirect("plugins:nautobot_ip_availability:prefix_availability")

        form = QuickPrefixCreateForm()
        return render(
            request,
            "nautobot_ip_availability/quick_create.html",
            {
                "form": form,
                "prefix_cidr": prefix_cidr,
                "namespace": namespace,
            },
        )

    def post(self, request):
        """Create the prefix with auto-filled fields."""
        prefix_cidr = request.POST.get("prefix")
        namespace_id = request.POST.get("namespace")

        if not prefix_cidr or not namespace_id:
            messages.error(request, "Missing prefix or namespace parameter.")
            return redirect("plugins:nautobot_ip_availability:prefix_availability")

        try:
            namespace = Namespace.objects.get(pk=namespace_id)
        except (Namespace.DoesNotExist, ValueError):
            messages.error(request, "Invalid namespace.")
            return redirect("plugins:nautobot_ip_availability:prefix_availability")

        form = QuickPrefixCreateForm(request.POST)
        if not form.is_valid():
            return render(
                request,
                "nautobot_ip_availability/quick_create.html",
                {
                    "form": form,
                    "prefix_cidr": prefix_cidr,
                    "namespace": namespace,
                },
            )

        # Check that "Reserved" status exists for Prefix
        reserved_status = Status.objects.get_for_model(Prefix).filter(name="Reserved").first()
        if not reserved_status:
            messages.error(request, "Status 'Reserved' not found. Please create it in Nautobot first.")
            return redirect("plugins:nautobot_ip_availability:prefix_availability")

        # Check prefix doesn't already exist in this namespace
        if Prefix.objects.filter(prefix=prefix_cidr, namespace=namespace).exists():
            messages.error(request, f"Prefix {prefix_cidr} already exists in namespace '{namespace}'.")
            return render(
                request,
                "nautobot_ip_availability/quick_create.html",
                {
                    "form": form,
                    "prefix_cidr": prefix_cidr,
                    "namespace": namespace,
                },
            )

        arin = RIR.objects.filter(name="ARIN").first()
        now = timezone.now()

        new_prefix = Prefix(
            prefix=prefix_cidr,
            namespace=namespace,
            type="network",
            status=reserved_status,
            rir=arin,
            description=form.cleaned_data["description"],
            date_allocated=now,
        )
        new_prefix.cf["sdp_ticket_id"] = form.cleaned_data["sdp_ticket_id"]
        new_prefix.save()

        return render(
            request,
            "nautobot_ip_availability/reservation_confirmed.html",
            {
                "prefix": str(new_prefix.prefix),
                "namespace": str(namespace),
                "description": form.cleaned_data["description"],
                "sdp_ticket_id": form.cleaned_data["sdp_ticket_id"],
                "rir": "ARIN",
                "date_allocated": now,
            },
        )
