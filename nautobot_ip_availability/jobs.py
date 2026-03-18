"""Jobs for nautobot_ip_availability."""

from datetime import timedelta

from django.utils import timezone
from nautobot.apps.jobs import Job
from nautobot.core.celery import register_jobs
from nautobot.ipam.models import Prefix

Name = "Nautobot IP Availability"  # pylint: disable=invalid-name


class ExpiredPrefixReservationCleanup(Job):
    """Delete prefixes that have been in 'Reserved' status for more than 2 months.

    This job finds all prefixes with status='Reserved' where the date_allocated
    is older than 2 months and deletes them, freeing the space back up.
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """Job metadata."""

        name = "Expired Reservation Cleanup"
        description = "Deletes reserved prefixes where the reservation is older than 2 months."

    def run(self):  # pylint: disable=arguments-differ
        """Find and delete expired reserved prefixes."""
        cutoff_date = timezone.now() - timedelta(days=60)

        expired_prefixes = Prefix.objects.filter(
            status__name="Reserved",
            role__name="Member",
            date_allocated__lte=cutoff_date,
        )

        count = expired_prefixes.count()

        if count == 0:
            self.logger.info("No expired reservations found.")
            return

        self.logger.info("Found %d expired reservation(s) to clean up.", count)

        for prefix in expired_prefixes:
            self.logger.info(
                "Deleting expired reservation: %s (namespace=%s, allocated=%s, description=%s, ticket=%s)",
                prefix.prefix,
                prefix.namespace,
                prefix.date_allocated,
                prefix.description,
                prefix.cf.get("sdp_ticket_id", "N/A"),
            )
            prefix.delete()

        self.logger.info("Deleted %d expired reservation(s).", count)


jobs = [ExpiredPrefixReservationCleanup]
register_jobs(*jobs)
