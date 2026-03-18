"""Views for nautobot_ip_availability."""

from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone
from nautobot.apps.views import GenericView
from nautobot.extras.models import Role, Status
from nautobot.ipam.models import RIR, Namespace, Prefix

from nautobot_ip_availability.forms import PrefixAvailabilityForm, QuickPrefixCreateForm
from nautobot_ip_availability.utils import find_available_prefixes


class PrefixAvailabilityView(GenericView):
    """View for finding available IP prefixes across all Leasable supernets."""

    def get(self, request):
        """Render the empty query form."""
        form = PrefixAvailabilityForm()
        return render(request, "nautobot_ip_availability/prefix_availability.html", {"form": form})

    def post(self, request):
        """Search all Leasable supernets for available prefixes."""
        form = PrefixAvailabilityForm(request.POST)
        results = None
        result_count = 0
        truncated = False

        if form.is_valid():
            prefix_length = form.cleaned_data["prefix_length"]

            results, truncated = find_available_prefixes(
                prefix_length=prefix_length,
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
    """Guided prefix creation — auto-sets status, type, role, rir, date_allocated."""

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

        # Look up required objects
        reserved_status = Status.objects.get_for_model(Prefix).filter(name="Reserved").first()
        if not reserved_status:
            messages.error(request, "Status 'Reserved' not found. Please create it in Nautobot first.")
            return redirect("plugins:nautobot_ip_availability:prefix_availability")

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
        member_role = Role.objects.filter(name="Member").first()
        now = timezone.now()

        new_prefix = Prefix(
            prefix=prefix_cidr,
            namespace=namespace,
            type="network",
            status=reserved_status,
            role=member_role,
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
                "role": "Member",
                "date_allocated": now,
            },
        )
