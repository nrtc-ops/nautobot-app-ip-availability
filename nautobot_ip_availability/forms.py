"""Forms for nautobot_ip_availability."""

from django import forms
from nautobot.apps.forms import DynamicModelChoiceField
from nautobot.ipam.models import Namespace, Prefix


class PrefixAvailabilityForm(forms.Form):
    """Form for querying available IP prefixes within a parent prefix."""

    namespace = DynamicModelChoiceField(
        queryset=Namespace.objects.all(),
        required=False,
        label="Namespace",
        help_text="Filter parent prefixes by namespace.",
    )
    parent_prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.filter(status__name="Leasable"),
        required=True,
        label="Parent Prefix",
        query_params={"namespace": "$namespace", "status": "Leasable"},
        help_text="Only prefixes in 'Leasable' status are shown.",
    )
    prefix_lengths = forms.CharField(
        required=True,
        label="Desired Prefix Length(s)",
        help_text="Comma-separated CIDR prefix lengths, e.g. '24,28'. Must be larger than the parent prefix length.",
        widget=forms.TextInput(attrs={"placeholder": "e.g. 24,28"}),
    )

    def clean_prefix_lengths(self):
        """Parse and validate comma-separated prefix lengths."""
        raw = self.cleaned_data["prefix_lengths"]
        parent = self.cleaned_data.get("parent_prefix")

        lengths = []
        for part in raw.split(","):
            part = part.strip().lstrip("/")
            if not part:
                continue
            try:
                length = int(part)
            except ValueError:
                raise forms.ValidationError(f"Invalid prefix length: '{part}'. Must be an integer.")

            if length < 1 or length > 128:
                raise forms.ValidationError(f"Prefix length {length} out of range (1-128).")

            if parent:
                max_length = 32 if parent.ip_version == 4 else 128
                if length > max_length:
                    raise forms.ValidationError(
                        f"Prefix length /{length} exceeds maximum for IPv{parent.ip_version} (/{max_length})."
                    )
                if length <= parent.prefix_length:
                    raise forms.ValidationError(
                        f"Prefix length /{length} must be greater than parent prefix length /{parent.prefix_length}."
                    )

            lengths.append(length)

        if not lengths:
            raise forms.ValidationError("At least one prefix length is required.")

        return sorted(set(lengths))


class QuickPrefixCreateForm(forms.Form):
    """Simplified prefix creation form for guided reservation workflow."""

    description = forms.CharField(
        required=True,
        max_length=255,
        label="Description",
        help_text="Description for this prefix reservation.",
        widget=forms.TextInput(attrs={"placeholder": "e.g. Customer ABC allocation"}),
    )
    sdp_ticket_id = forms.CharField(
        required=True,
        max_length=100,
        label="ServiceDesk Ticket #",
        help_text="The SDP ticket number associated with this reservation.",
        widget=forms.TextInput(attrs={"placeholder": "e.g. SDP-12345"}),
    )
