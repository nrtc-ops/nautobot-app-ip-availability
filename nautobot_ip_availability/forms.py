"""Forms for nautobot_ip_availability."""

from django import forms


class PrefixAvailabilityForm(forms.Form):
    """Form for finding available IP prefixes across all Leasable supernets."""

    prefix_length = forms.IntegerField(
        required=True,
        min_value=1,
        max_value=128,
        label="Desired Prefix Size",
        help_text="Enter the prefix length you need, e.g. 24 for a /24. All Leasable supernets will be searched.",
        widget=forms.NumberInput(attrs={"placeholder": "e.g. 24"}),
    )


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
