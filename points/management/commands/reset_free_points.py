from django.core.management.base import BaseCommand
from points.services import reset_all_wallets_free_points


class Command(BaseCommand):
    help = "Reset free points for all users"

    def handle(self, *args, **kwargs):
        reset_all_wallets_free_points()
        self.stdout.write(self.style.SUCCESS("Free points reset completed successfully."))