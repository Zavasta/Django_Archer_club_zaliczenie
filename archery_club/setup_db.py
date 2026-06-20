
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mojprojekt.settings')

# Add the project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.core.management import call_command
from club_app.models import ClubMember, Bow, MemberBow


def run_migrations():
    print(" Running migrations...")
    call_command('makemigrations', 'club_app', verbosity=1)
    call_command('migrate', verbosity=1)
    print(" Migrations complete!\n")


def create_sample_data():
    print(" Creating sample data...\n")

    # ── Create Members ────────────────────────────

    # Admin / Superuser
    if not ClubMember.objects.filter(username='admin').exists():
        admin = ClubMember.objects.create_superuser(
            username='admin',
            email='admin@archery.club',
            password='admin123',
        )
        admin.height_cm = 180
        admin.arm_length_cm = 68
        admin.strength_lbs = 40
        admin.age = 35
        admin.experience = 'master'
        admin.accuracy_pct = 85.0
        admin.save()
        print(f"  Created admin: admin / admin123")

    # VIP Member 1
    if not ClubMember.objects.filter(username='artemis').exists():
        artemis = ClubMember.objects.create_user(
            username='artemis',
            email='artemis@archery.club',
            password='vip123',
            first_name='Artemis',
            last_name='Fletcher',
            gender='F',
            height_cm=165,
            arm_length_cm=62,
            strength_lbs=38,
            age=28,
            experience='advanced',
            accuracy_pct=78.0,
            is_vip=True,
        )
        print(f"  Created VIP: artemis / vip123")
    else:
        artemis = ClubMember.objects.get(username='artemis')

    # VIP Member 2 – short but strong
    if not ClubMember.objects.filter(username='titan').exists():
        titan = ClubMember.objects.create_user(
            username='titan',
            email='titan@archery.club',
            password='vip123',
            first_name='Marcus',
            last_name='Titan',
            gender='M',
            height_cm=158,
            arm_length_cm=59,
            strength_lbs=48,
            age=32,
            experience='master',
            accuracy_pct=82.0,
            is_vip=True,
        )
        print(f"  ⭐ Created VIP: titan / vip123")
    else:
        titan = ClubMember.objects.get(username='titan')

    # Regular Member 1
    if not ClubMember.objects.filter(username='robin').exists():
        robin = ClubMember.objects.create_user(
            username='robin',
            email='robin@archery.club',
            password='pass123',
            first_name='Robin',
            last_name='Hood',
            gender='M',
            height_cm=175,
            arm_length_cm=66,
            strength_lbs=28,
            age=24,
            experience='adept',
            accuracy_pct=62.5,
            is_vip=False,
        )
        print(f"  Created regular: robin / pass123")
    else:
        robin = ClubMember.objects.get(username='robin')

    # Regular Member 2 – beginner
    if not ClubMember.objects.filter(username='alice').exists():
        alice = ClubMember.objects.create_user(
            username='alice',
            email='alice@archery.club',
            password='pass123',
            first_name='Alice',
            last_name='Greenwood',
            gender='F',
            height_cm=162,
            arm_length_cm=60,
            strength_lbs=20,
            age=19,
            experience='beginner',
            accuracy_pct=38.0,
            is_vip=False,
        )
        print(f"  Created regular: alice / pass123")
    else:
        alice = ClubMember.objects.get(username='alice')

    # Regular Member 3
    if not ClubMember.objects.filter(username='thorin').exists():
        thorin = ClubMember.objects.create_user(
            username='thorin',
            email='thorin@archery.club',
            password='pass123',
            first_name='Thorin',
            last_name='Oakenshield',
            gender='M',
            height_cm=152,
            arm_length_cm=57,
            strength_lbs=35,
            age=40,
            experience='advanced',
            accuracy_pct=70.0,
            is_vip=False,
        )
        print(f"  🏹 Created regular: thorin / pass123")
    else:
        thorin = ClubMember.objects.get(username='thorin')

    print()

    # ── Create Bows ───────────────────────────────

    bows_data = [
        {
            'name': 'Forest Hunter',
            'bow_type': 'longbow',
            'draw_weight_lbs': 28,
            'length_cm': 182,
            'material': 'wood',
            'added_by': robin,
            'notes': 'Classic English longbow, great for medium-strength archers. Excellent for distances up to 80m.',
        },
        {
            'name': 'Shadow Short',
            'bow_type': 'shortbow',
            'draw_weight_lbs': 20,
            'length_cm': 118,
            'material': 'wood',
            'added_by': alice,
            'notes': 'Lightweight short bow, perfect for beginners. Easy to handle.',
        },
        {
            'name': 'Carbon Recurve Pro',
            'bow_type': 'recurve',
            'draw_weight_lbs': 38,
            'length_cm': 168,
            'material': 'carbon',
            'added_by': artemis,
            'notes': 'Olympic-style recurve with carbon riser. Competition-grade.',
        },
        {
            'name': 'Compound Beast',
            'bow_type': 'compound',
            'draw_weight_lbs': 55,
            'length_cm': 95,
            'material': 'composite',
            'added_by': artemis,
            'notes': 'High-performance compound with cam system. For masters and experienced hunters.',
        },
        {
            'name': 'Short Power',
            'bow_type': 'shortbow',
            'draw_weight_lbs': 42,
            'length_cm': 115,
            'material': 'composite',
            'added_by': titan,
            'notes': 'Compact but powerful – designed for shorter archers with strong pull.',
        },
        {
            'name': 'Elven Grace',
            'bow_type': 'recurve',
            'draw_weight_lbs': 25,
            'length_cm': 155,
            'material': 'hybrid',
            'added_by': alice,
            'notes': 'Lightweight recurve with hybrid construction. Beautiful grain, smooth draw.',
        },
        {
            'name': 'Iron Mountain',
            'bow_type': 'longbow',
            'draw_weight_lbs': 50,
            'length_cm': 195,
            'material': 'composite',
            'added_by': robin,
            'notes': 'Heavy longbow for advanced archers. Not for the faint-hearted.',
        },
        {
            'name': 'Ranger Crossbow',
            'bow_type': 'crossbow',
            'draw_weight_lbs': 60,
            'length_cm': 88,
            'material': 'composite',
            'added_by': titan,
            'notes': 'Heavy-duty crossbow with scope mount. Hunters choice.',
        },
    ]

    created_bows = []
    for bow_data in bows_data:
        bow, created = Bow.objects.get_or_create(
            name=bow_data['name'],
            defaults=bow_data
        )
        created_bows.append(bow)
        if created:
            print(f"   Created bow: {bow.name} ({bow.draw_weight_lbs}lbs, {bow.length_cm}cm)")

    print()

    # ── Link Bows to Members ──────────────────────

    bow_by_name = {b.name: b for b in created_bows}

    member_bow_links = [
        (robin, 'Forest Hunter', True),
        (robin, 'Iron Mountain', False),
        (alice, 'Shadow Short', True),
        (alice, 'Elven Grace', False),
        (thorin, 'Short Power', True),
        (artemis, 'Carbon Recurve Pro', True),
        (artemis, 'Compound Beast', False),
        (artemis, 'Elven Grace', False),
        (titan, 'Short Power', True),
        (titan, 'Ranger Crossbow', False),
        (titan, 'Compound Beast', False),
    ]

    for member, bow_name, is_primary in member_bow_links:
        if bow_name in bow_by_name:
            bow = bow_by_name[bow_name]
            _, created = MemberBow.objects.get_or_create(
                member=member,
                bow=bow,
                defaults={'is_primary': is_primary},
            )
            if created:
                print(f"   Linked: {member.username} → {bow_name}{'  [PRIMARY]' if is_primary else ''}")

    print()
    print(" Sample data loaded successfully!")
    print()
    print("=" * 50)
    print(" Accounts (username / password):")
    print()
    print("   admin    / admin123    (superuser + VIP)")
    print("   artemis  / vip123      (VIP member)")
    print("   titan    / vip123      (VIP member, short+strong)")
    print("   robin    / pass123     (regular member)")
    print("   alice    / pass123     (beginner member)")
    print("   thorin   / pass123     (regular member, short+strong)")
    print()
    print(" Run the server:")
    print("   python manage.py runserver")
    print()
    print(" Open: http://127.0.0.1:8000/")
    print(" Admin: http://127.0.0.1:8000/admin/")
    print(" API: http://127.0.0.1:8000/api/")
    print("=" * 50)


if __name__ == '__main__':
    run_migrations()
    create_sample_data()
