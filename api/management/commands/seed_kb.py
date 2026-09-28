from django.core.management.base import BaseCommand
from api.models import KBEntry

ENTRIES = [
    {
        'question': 'What is select_related in Django ORM?',
        'answer': 'select_related performs a SQL JOIN and fetches related objects in the same query, avoiding extra database hits for foreign keys.',
        'category': 'database',
    },
    {
        'question': 'When should I use select_related vs prefetch_related?',
        'answer': 'Use select_related for foreign key and one-to-one relations, and prefetch_related for many-to-many or reverse foreign key relations.',
        'category': 'database',
    },
    {
        'question': 'How does transaction.atomic() work?',
        'answer': 'transaction.atomic() wraps a block of code so that all database writes inside it succeed together or are rolled back together if any of them fails.',
        'category': 'database',
    },
    {
        'question': 'Why wrap a query log write in transaction.atomic()?',
        'answer': 'Wrapping related writes in transaction.atomic() keeps them consistent, so a search result and its log entry are never saved partially.',
        'category': 'database',
    },
    {
        'question': 'What is a JWT token?',
        'answer': 'A JWT token is a signed, self-contained token used to authenticate requests without the server needing to store session state.',
        'category': 'api',
    },
    {
        'question': 'How do I implement JWT authentication in Django REST Framework?',
        'answer': 'Install djangorestframework-simplejwt, add JWTAuthentication to DEFAULT_AUTHENTICATION_CLASSES, and issue tokens using RefreshToken.for_user().',
        'category': 'api',
    },
    {
        'question': 'When should I use Q objects in Django?',
        'answer': 'Q objects let you build complex queries with OR conditions or nested AND/OR logic that plain keyword filtering cannot express.',
        'category': 'framework',
    },
    {
        'question': 'How do I search two fields with Q objects and icontains?',
        'answer': 'Combine Q(field1__icontains=term) | Q(field2__icontains=term) inside filter() to match either field case-insensitively.',
        'category': 'framework',
    },
    {
        'question': 'How do Django signals work?',
        'answer': 'Signals let one piece of code notify other parts of the app when an event happens, such as post_save firing after a model instance is saved.',
        'category': 'framework',
    },
    {
        'question': 'How do I auto-create a related profile using signals in Django?',
        'answer': 'Connect a post_save receiver on the User model and check the created flag to create a related profile only the first time a user is saved.',
        'category': 'framework',
    },
    {
        'question': 'How do I run PostgreSQL locally with Docker?',
        'answer': 'Define a postgres service in docker-compose.yml with POSTGRES_DB, POSTGRES_USER and POSTGRES_PASSWORD, then run docker compose up -d.',
        'category': 'cloud',
    },
    {
        'question': 'What is the difference between REST and GraphQL?',
        'answer': 'REST exposes fixed endpoints per resource, while GraphQL exposes a single endpoint where clients specify exactly the fields they need.',
        'category': 'general',
    },
]


class Command(BaseCommand):
    help = 'Seed the knowledge base with sample Q&A entries'

    def handle(self, *args, **options):
        created = 0
        for entry in ENTRIES:
            _, was_created = KBEntry.objects.get_or_create(
                question=entry['question'],
                defaults={'answer': entry['answer'], 'category': entry['category']},
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'Seeded {created} KB entries ({len(ENTRIES)} total defined).'))
