"""Seed the development database with users and barks."""

from itertools import cycle

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import BarkModel, DogUserModel


DEFAULT_USER_COUNT = 20
DEFAULT_BARK_COUNT = 10_000
DEFAULT_BATCH_SIZE = 1_000
DEFAULT_PASSWORD = "seed-password"

TOYS = ("tennis ball", "rope", "frisbee", "squeaky duck", "chew bone")
MESSAGES = (
    "Spotted a squirrel on the morning walk",
    "The post carrier is back again",
    "Who wants to play fetch?",
    "Just found the perfect sunny spot",
    "Dinner was at least five minutes late",
    "Can confirm: the park is excellent today",
    "I heard a suspicious noise outside",
    "Dreaming about an unlimited supply of treats",
)


class Command(BaseCommand):
    help = "Create seed users and barks for local pagination testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--users",
            type=int,
            default=DEFAULT_USER_COUNT,
            help=f"Number of seed users to ensure exist (default: {DEFAULT_USER_COUNT}).",
        )
        parser.add_argument(
            "--barks",
            type=int,
            default=DEFAULT_BARK_COUNT,
            help=f"Number of new barks to create (default: {DEFAULT_BARK_COUNT}).",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=DEFAULT_BATCH_SIZE,
            help=f"Rows per bulk insert (default: {DEFAULT_BATCH_SIZE}).",
        )
        parser.add_argument(
            "--password",
            default=DEFAULT_PASSWORD,
            help=f"Password assigned to newly created seed users (default: {DEFAULT_PASSWORD}).",
        )

    def handle(self, *args, **options):
        user_count = options["users"]
        bark_count = options["barks"]
        batch_size = options["batch_size"]

        if user_count < 1:
            raise CommandError("--users must be at least 1")
        if bark_count < 0:
            raise CommandError("--barks cannot be negative")
        if batch_size < 1:
            raise CommandError("--batch-size must be at least 1")

        users, created_user_count = self._ensure_users(
            count=user_count,
            password=options["password"],
        )
        created_bark_count = self._create_barks(
            users=users,
            count=bark_count,
            batch_size=batch_size,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete: {created_user_count} users created "
                f"({len(users)} available), {created_bark_count} barks created."
            )
        )

    @staticmethod
    @transaction.atomic
    def _ensure_users(count: int, password: str) -> tuple[list[DogUserModel], int]:
        users = []
        created_count = 0

        for index in range(1, count + 1):
            user, created = DogUserModel.objects.get_or_create(
                username=f"seed_dog_{index:03d}",
                defaults={"favorite_toy": TOYS[(index - 1) % len(TOYS)]},
            )
            if created:
                user.set_password(password)
                user.save(update_fields=["password"])
                created_count += 1
            users.append(user)

        return users, created_count

    @staticmethod
    def _create_barks(
        users: list[DogUserModel], count: int, batch_size: int
    ) -> int:
        user_ids = cycle(user.id for user in users)

        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            barks = [
                BarkModel(
                    user_id=next(user_ids),
                    message=f"{MESSAGES[index % len(MESSAGES)]} (seed #{index + 1})",
                )
                for index in range(batch_start, batch_end)
            ]
            BarkModel.objects.bulk_create(barks, batch_size=batch_size)

        return count
