
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

ClubMember = get_user_model()


# ─────────────────────────────────────────────
#  USER FIXTURES
# ─────────────────────────────────────────────

@pytest.fixture
def api_client():
    """Return an unauthenticated DRF APIClient."""
    return APIClient()


@pytest.fixture
def regular_member(db):
    """Create and return a regular (non-VIP) club member."""
    user = ClubMember.objects.create_user(
        username='regular_archer',
        email='regular@archery.club',
        password='testpass123',
        first_name='Robin',
        last_name='Hood',
        gender='M',
        height_cm=175,
        arm_length_cm=65,
        strength_lbs=28,
        age=25,
        experience='adept',
        accuracy_pct=62.5,
        is_vip=False,
    )
    return user


@pytest.fixture
def vip_member(db):
    """Create and return a VIP club member."""
    user = ClubMember.objects.create_user(
        username='vip_archer',
        email='vip@archery.club',
        password='testpass123',
        first_name='Artemis',
        last_name='Fletcher',
        gender='F',
        height_cm=165,
        arm_length_cm=62,
        strength_lbs=40,
        age=30,
        experience='advanced',
        accuracy_pct=78.0,
        is_vip=True,
    )
    return user


@pytest.fixture
def short_strong_member(db):
    """Create a short but strong member (special case for VIP suggestion)."""
    user = ClubMember.objects.create_user(
        username='short_strong',
        email='short@archery.club',
        password='testpass123',
        gender='M',
        height_cm=158,
        arm_length_cm=58,
        strength_lbs=45,
        age=28,
        experience='advanced',
        accuracy_pct=70.0,
        is_vip=True,
    )
    return user


@pytest.fixture
def beginner_member(db):
    """Create a beginner member."""
    user = ClubMember.objects.create_user(
        username='beginner_alice',
        email='alice@archery.club',
        password='testpass123',
        gender='F',
        height_cm=162,
        arm_length_cm=60,
        strength_lbs=20,
        age=18,
        experience='beginner',
        accuracy_pct=35.0,
        is_vip=False,
    )
    return user


@pytest.fixture
def admin_member(db):
    """Create a superuser / admin member."""
    user = ClubMember.objects.create_superuser(
        username='admin',
        email='admin@archery.club',
        password='adminpass123',
    )
    return user


# ─────────────────────────────────────────────
#  AUTHENTICATED API CLIENT FIXTURES
# ─────────────────────────────────────────────

@pytest.fixture
def auth_client(api_client, regular_member):
    """APIClient authenticated as a regular member."""
    api_client.force_authenticate(user=regular_member)
    return api_client


@pytest.fixture
def vip_client(api_client, vip_member):
    """APIClient authenticated as a VIP member."""
    api_client.force_authenticate(user=vip_member)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_member):
    """APIClient authenticated as an admin."""
    api_client.force_authenticate(user=admin_member)
    return api_client


# ─────────────────────────────────────────────
#  BOW FIXTURES
# ─────────────────────────────────────────────

@pytest.fixture
def sample_bows(db, regular_member):
    """Create a set of sample bows for testing."""
    from club_app.models import Bow

    bows = [
        Bow.objects.create(
            name='Forest Hunter',
            bow_type='longbow',
            draw_weight_lbs=28,
            length_cm=180,
            material='wood',
            added_by=regular_member,
            notes='Classic long bow for medium-strength archers',
        ),
        Bow.objects.create(
            name='Shadow Short',
            bow_type='shortbow',
            draw_weight_lbs=22,
            length_cm=120,
            material='wood',
            added_by=regular_member,
            notes='Light short bow for beginners',
        ),
        Bow.objects.create(
            name='Carbon Recurve Pro',
            bow_type='recurve',
            draw_weight_lbs=38,
            length_cm=165,
            material='carbon',
            added_by=regular_member,
            notes='Professional recurve for experienced archers',
        ),
        Bow.objects.create(
            name='Compound Beast',
            bow_type='compound',
            draw_weight_lbs=55,
            length_cm=95,
            material='composite',
            added_by=regular_member,
            notes='Heavy compound for masters',
        ),
        Bow.objects.create(
            name='Short Power',
            bow_type='shortbow',
            draw_weight_lbs=42,
            length_cm=115,
            material='composite',
            added_by=regular_member,
            notes='Short but strong – for compact powerful archers',
        ),
    ]
    return bows


@pytest.fixture
def single_bow(db, regular_member):
    """Create a single bow for testing."""
    from club_app.models import Bow
    return Bow.objects.create(
        name='Test Bow',
        bow_type='recurve',
        draw_weight_lbs=30,
        length_cm=155,
        material='composite',
        added_by=regular_member,
    )
