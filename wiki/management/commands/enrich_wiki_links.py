from django.core.management.base import BaseCommand

from wiki.models import WikiPage
from .generate_massive_wiki import KEYWORD_LINKS, cleanup_link_artifacts, inject_link


class Command(BaseCommand):
    help = "Apply keyword-based wiki links across existing wiki pages."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Only process this many pages (useful for incremental runs).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report how many pages would change without writing to the database.",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        dry_run = options["dry_run"]

        queryset = WikiPage.objects.order_by("id")
        if limit is not None:
            queryset = queryset[:limit]

        updated = 0
        for page in queryset:
            original = page.content
            enriched, _ = cleanup_link_artifacts(original)
            for term, target in KEYWORD_LINKS:
                enriched = inject_link(enriched, term, target)

            if enriched != original:
                updated += 1
                if not dry_run:
                    page.content = enriched
                    page.save(update_fields=["content"])

        action = "would be updated" if dry_run else "updated"
        self.stdout.write(f"{updated} page(s) {action}.")
