
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model

from club_app.models import Bow, MemberBow, ClubMember

ClubMemberModel = get_user_model()


# ═══════════════════════════════════════════════════
#  AUTH API TESTS
# ═══════════════════════════════════════════════════

@pytest.mark.django_db
class TestAuthAPI:
    """Tests for /api/auth/ endpoints."""

    def test_register_new_member_success(self, api_client):
        """
        POST /api/auth/register/ with valid data should return 201.
        """
        data = {
            'username': 'new_archer',
            'email': 'new@archery.club',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'gender': 'M',
            'height_cm': 178,
            'arm_length_cm': 67,
            'strength_lbs': 30,
            'age': 22,
            'experience': 'beginner',
            'accuracy_pct': 45.0,
        }
        response = api_client.post('/api/auth/register/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'member' in response.data
        assert response.data['member']['username'] == 'new_archer'
        assert response.data['member']['is_vip'] is False

    def test_register_password_mismatch_returns_400(self, api_client):
        """POST with mismatched passwords should return 400."""
        data = {
            'username': 'bad_archer',
            'email': 'bad@archery.club',
            'password': 'password123',
            'password_confirm': 'different456',
            'height_cm': 170,
            'arm_length_cm': 65,
            'strength_lbs': 25,
            'age': 20,
            'experience': 'beginner',
            'accuracy_pct': 50.0,
        }
        response = api_client.post('/api/auth/register/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_confirm' in response.data

    def test_register_duplicate_username_returns_400(self, api_client, regular_member):
        """POST with already-taken username should return 400."""
        data = {
            'username': regular_member.username,  # duplicate
            'email': 'other@archery.club',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'height_cm': 170,
            'arm_length_cm': 65,
            'strength_lbs': 25,
            'age': 20,
            'experience': 'beginner',
            'accuracy_pct': 50.0,
        }
        response = api_client.post('/api/auth/register/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_valid_credentials_returns_200(self, api_client, regular_member):
        """POST /api/auth/login/ with correct credentials should return 200."""
        data = {
            'username': regular_member.username,
            'password': 'testpass123',
        }
        response = api_client.post('/api/auth/login/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'member' in response.data
        assert response.data['member']['username'] == regular_member.username

    def test_login_wrong_password_returns_400(self, api_client, regular_member):
        """POST /api/auth/login/ with wrong password should return 400."""
        data = {
            'username': regular_member.username,
            'password': 'wrongpassword!',
        }
        response = api_client.post('/api/auth/login/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_nonexistent_user_returns_400(self, api_client):
        """POST /api/auth/login/ with unknown user should return 400."""
        data = {'username': 'nobody', 'password': 'nopass'}
        response = api_client.post('/api/auth/login/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ═══════════════════════════════════════════════════
#  MEMBER API TESTS
# ═══════════════════════════════════════════════════

@pytest.mark.django_db
class TestMemberAPI:
    """Tests for /api/members/ and /api/me/ endpoints."""

    def test_list_members_requires_auth(self, api_client):
        """Unauthenticated GET /api/members/ should return 403."""
        response = api_client.get('/api/members/')
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]

    def test_list_members_authenticated(self, auth_client, regular_member, vip_member):
        """Authenticated GET /api/members/ returns list with count."""
        response = auth_client.get('/api/members/')
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'results' in response.data
        assert response.data['count'] >= 2

    def test_get_own_profile(self, auth_client, regular_member):
        """GET /api/me/ returns the authenticated user's profile."""
        response = auth_client.get('/api/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == regular_member.username
        assert response.data['height_cm'] == regular_member.height_cm
        assert response.data['is_vip'] == regular_member.is_vip

    def test_update_own_profile(self, auth_client, regular_member):
        """PUT /api/me/ updates the user's attributes."""
        data = {
            'height_cm': 180,
            'strength_lbs': 35,
            'accuracy_pct': 70.0,
            'experience': 'advanced',
        }
        response = auth_client.put('/api/me/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['height_cm'] == 180
        assert response.data['strength_lbs'] == 35
        assert response.data['accuracy_pct'] == 70.0

    def test_update_another_member_forbidden(self, auth_client, vip_member):
        """PUT /api/members/<other_id>/ by a non-admin should return 403."""
        data = {'height_cm': 200}
        response = auth_client.put(f'/api/members/{vip_member.pk}/', data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_filter_members_by_experience(self, auth_client, beginner_member, vip_member):
        """GET /api/members/?experience=beginner should filter correctly."""
        response = auth_client.get('/api/members/?experience=beginner')
        assert response.status_code == status.HTTP_200_OK
        usernames = [m['username'] for m in response.data['results']]
        assert beginner_member.username in usernames
        for member in response.data['results']:
            assert member['experience'] == 'beginner'

    def test_filter_members_vip_only(self, auth_client, vip_member, beginner_member):
        """GET /api/members/?is_vip=true should only return VIP members."""
        response = auth_client.get('/api/members/?is_vip=true')
        assert response.status_code == status.HTTP_200_OK
        for member in response.data['results']:
            assert member['is_vip'] is True

    def test_member_detail_includes_bows(self, auth_client, regular_member, single_bow):
        """GET /api/members/<id>/ includes the member's bows."""
        MemberBow.objects.create(member=regular_member, bow=single_bow)
        response = auth_client.get(f'/api/members/{regular_member.pk}/')
        assert response.status_code == status.HTTP_200_OK
        assert 'bows' in response.data
        assert len(response.data['bows']) >= 1

    def test_member_profile_has_strength_category(self, auth_client, regular_member):
        """GET /api/me/ should include computed strength_category field."""
        response = auth_client.get('/api/me/')
        assert response.status_code == status.HTTP_200_OK
        assert 'strength_category' in response.data
        assert response.data['strength_category'] in ['light', 'medium', 'heavy']


# ═══════════════════════════════════════════════════
#  BOW API TESTS
# ═══════════════════════════════════════════════════

@pytest.mark.django_db
class TestBowAPI:
    """Tests for /api/bows/ CRUD endpoints."""

    def test_list_bows_authenticated(self, auth_client, sample_bows):
        """GET /api/bows/ returns all bows."""
        response = auth_client.get('/api/bows/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == len(sample_bows)
        assert 'results' in response.data

    def test_list_bows_unauthenticated(self, api_client):
        """GET /api/bows/ without auth returns 403."""
        response = api_client.get('/api/bows/')
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]

    def test_create_bow_success(self, auth_client, regular_member):
        """POST /api/bows/ creates a new bow."""
        data = {
            'name': 'New Test Bow',
            'bow_type': 'recurve',
            'draw_weight_lbs': 32,
            'length_cm': 160,
            'material': 'composite',
            'notes': 'A test bow',
        }
        response = auth_client.post('/api/bows/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Test Bow'
        assert response.data['bow_type'] == 'recurve'
        assert Bow.objects.filter(name='New Test Bow').exists()

    def test_create_bow_missing_required_field(self, auth_client):
        """POST /api/bows/ without name returns 400."""
        data = {
            'bow_type': 'longbow',
            'draw_weight_lbs': 25,
            'length_cm': 170,
            'material': 'wood',
        }
        response = auth_client.post('/api/bows/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_bow_detail(self, auth_client, single_bow):
        """GET /api/bows/<id>/ returns bow details."""
        response = auth_client.get(f'/api/bows/{single_bow.pk}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == single_bow.name
        assert response.data['draw_weight_lbs'] == single_bow.draw_weight_lbs
        assert 'strength_category' in response.data
        assert 'size_category' in response.data
        assert 'bow_type_display' in response.data

    def test_update_own_bow(self, auth_client, single_bow):
        """PUT /api/bows/<id>/ updates the bow (by creator)."""
        data = {
            'name': 'Updated Bow Name',
            'draw_weight_lbs': 35,
            'length_cm': 160,
            'bow_type': 'recurve',
            'material': 'composite',
        }
        response = auth_client.put(f'/api/bows/{single_bow.pk}/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        single_bow.refresh_from_db()
        assert single_bow.name == 'Updated Bow Name'
        assert single_bow.draw_weight_lbs == 35

    def test_update_others_bow_forbidden(self, api_client, vip_member, single_bow):
        """PUT /api/bows/<id>/ by non-creator returns 403."""
        api_client.force_authenticate(user=vip_member)
        data = {'name': 'Stolen Bow'}
        response = api_client.put(f'/api/bows/{single_bow.pk}/', data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_own_bow(self, auth_client, single_bow):
        """DELETE /api/bows/<id>/ removes the bow (by creator)."""
        bow_pk = single_bow.pk
        response = auth_client.delete(f'/api/bows/{bow_pk}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Bow.objects.filter(pk=bow_pk).exists()

    def test_delete_others_bow_forbidden(self, api_client, vip_member, single_bow):
        """DELETE /api/bows/<id>/ by non-creator returns 403."""
        api_client.force_authenticate(user=vip_member)
        response = api_client.delete(f'/api/bows/{single_bow.pk}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_filter_bows_by_type(self, auth_client, sample_bows):
        """GET /api/bows/?type=longbow should return only longbows."""
        response = auth_client.get('/api/bows/?type=longbow')
        assert response.status_code == status.HTTP_200_OK
        for bow in response.data['results']:
            assert bow['bow_type'] == 'longbow'

    def test_filter_bows_by_weight_range(self, auth_client, sample_bows):
        """GET /api/bows/?min_weight=30&max_weight=40 filters by draw weight."""
        response = auth_client.get('/api/bows/?min_weight=30&max_weight=40')
        assert response.status_code == status.HTTP_200_OK
        for bow in response.data['results']:
            assert 30 <= bow['draw_weight_lbs'] <= 40

    def test_bow_has_computed_fields(self, auth_client, sample_bows):
        """GET /api/bows/ results include computed strength_category and size_category."""
        response = auth_client.get('/api/bows/')
        assert response.status_code == status.HTTP_200_OK
        for bow in response.data['results']:
            assert 'strength_category' in bow
            assert 'size_category' in bow
            assert bow['strength_category'] in ['light', 'medium', 'heavy']
            assert bow['size_category'] in ['short', 'medium', 'long']

    def test_bow_nonexistent_returns_404(self, auth_client):
        """GET /api/bows/9999/ returns 404."""
        response = auth_client.get('/api/bows/9999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ═══════════════════════════════════════════════════
#  MY BOWS API TESTS
# ═══════════════════════════════════════════════════

@pytest.mark.django_db
class TestMyBowsAPI:
    """Tests for /api/my-bows/ endpoints."""

    def test_list_my_bows_empty(self, auth_client):
        """GET /api/my-bows/ returns empty list for new member."""
        response = auth_client.get('/api/my-bows/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert response.data['can_add_more'] is True
        assert response.data['bow_limit'] == 3  # Regular member limit

    def test_add_bow_to_profile(self, auth_client, single_bow, regular_member):
        """POST /api/my-bows/ links a bow to the member's profile."""
        data = {'bow_id': single_bow.pk}
        response = auth_client.post('/api/my-bows/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert MemberBow.objects.filter(member=regular_member, bow=single_bow).exists()

    def test_add_same_bow_twice_returns_200(self, auth_client, single_bow, regular_member):
        """POST /api/my-bows/ with already-owned bow returns 200 with message."""
        MemberBow.objects.create(member=regular_member, bow=single_bow)
        data = {'bow_id': single_bow.pk}
        response = auth_client.post('/api/my-bows/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'already' in response.data['message'].lower()

    def test_remove_bow_from_profile(self, auth_client, single_bow, regular_member):
        """DELETE /api/my-bows/<bow_id>/ removes the bow from the member's profile."""
        MemberBow.objects.create(member=regular_member, bow=single_bow)
        response = auth_client.delete(f'/api/my-bows/{single_bow.pk}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not MemberBow.objects.filter(member=regular_member, bow=single_bow).exists()

    def test_vip_member_has_no_bow_limit(self, vip_client):
        """GET /api/my-bows/ for VIP member shows bow_limit=None."""
        response = vip_client.get('/api/my-bows/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['bow_limit'] is None
        assert response.data['can_add_more'] is True


# ═══════════════════════════════════════════════════
#  BOW LIMIT TESTS
# ═══════════════════════════════════════════════════

@pytest.mark.django_db
class TestBowLimits:
    """Tests for the 3-bow limit on regular members."""

    def test_regular_member_limited_to_3_bows(self, auth_client, regular_member):
        """Regular members cannot add more than 3 bows via API."""
        # Create 3 bows and link them
        for i in range(3):
            bow = Bow.objects.create(
                name=f'Bow {i}',
                bow_type='recurve',
                draw_weight_lbs=25,
                length_cm=150,
                material='wood',
                added_by=regular_member,
            )
            MemberBow.objects.create(member=regular_member, bow=bow)

        # 4th bow should be rejected
        data = {
            'name': 'One Too Many',
            'bow_type': 'longbow',
            'draw_weight_lbs': 30,
            'length_cm': 170,
            'material': 'wood',
        }
        response = auth_client.post('/api/bows/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_vip_member_unlimited_bows(self, vip_client, vip_member):
        """VIP members can create more than 3 bows."""
        for i in range(5):
            data = {
                'name': f'VIP Bow {i}',
                'bow_type': 'recurve',
                'draw_weight_lbs': 35,
                'length_cm': 160,
                'material': 'composite',
            }
            response = vip_client.post('/api/bows/', data, format='json')
            assert response.status_code == status.HTTP_201_CREATED, f"Failed at bow {i}: {response.data}"

    def test_member_bow_count_property(self, regular_member, single_bow):
        """ClubMember.bow_count property reflects actual linked bows."""
        assert regular_member.bow_count == 0
        MemberBow.objects.create(member=regular_member, bow=single_bow)
        regular_member.refresh_from_db()
        assert regular_member.bow_count == 1

    def test_can_add_bow_property_true(self, regular_member):
        """can_add_bow is True when member has < 3 bows."""
        assert regular_member.can_add_bow is True

    def test_can_add_bow_property_false_at_limit(self, regular_member):
        """can_add_bow is False when regular member has 3 bows."""
        for i in range(3):
            bow = Bow.objects.create(
                name=f'Bow {i}',
                bow_type='shortbow',
                draw_weight_lbs=20,
                length_cm=120,
                material='wood',
                added_by=regular_member,
            )
            MemberBow.objects.create(member=regular_member, bow=bow)
        regular_member.refresh_from_db()
        assert regular_member.can_add_bow is False


# ═══════════════════════════════════════════════════
#  VIP API TESTS
# ═══════════════════════════════════════════════════

@pytest.mark.django_db
class TestVIPAPI:
    """Tests for /api/vip/ endpoints."""

    def test_suggest_bow_for_vip_member(self, vip_client, sample_bows):
        """GET /api/vip/suggest-bow/ returns a suggested bow for VIP members."""
        response = vip_client.get('/api/vip/suggest-bow/')
        assert response.status_code == status.HTTP_200_OK
        assert 'suggested_bow' in response.data
        assert response.data['suggested_bow'] is not None
        assert 'score_explanation' in response.data
        assert 'member_profile_summary' in response.data

    def test_suggest_bow_denied_for_regular_member(self, auth_client):
        """GET /api/vip/suggest-bow/ returns 403 for non-VIP member."""
        response = auth_client.get('/api/vip/suggest-bow/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_suggest_bow_no_bows_in_db(self, vip_client):
        """GET /api/vip/suggest-bow/ with empty DB returns informative 200."""
        response = vip_client.get('/api/vip/suggest-bow/')
        assert response.status_code == status.HTTP_200_OK

    def test_generate_bow_for_vip_member(self, vip_client):
        """GET /api/vip/generate-bow/ returns a bow specification."""
        response = vip_client.get('/api/vip/generate-bow/')
        assert response.status_code == status.HTTP_200_OK
        assert 'generated_bow' in response.data
        generated = response.data['generated_bow']
        assert 'name' in generated
        assert 'bow_type' in generated
        assert 'draw_weight_lbs' in generated
        assert 'length_cm' in generated
        assert 'material' in generated
        assert 'reasoning' in generated

    def test_generate_bow_denied_for_regular_member(self, auth_client):
        """GET /api/vip/generate-bow/ returns 403 for non-VIP member."""
        response = auth_client.get('/api/vip/generate-bow/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_generate_bow_post_saves_to_db(self, vip_client, vip_member):
        """POST /api/vip/generate-bow/ creates a bow in the DB."""
        initial_count = Bow.objects.count()
        response = vip_client.post('/api/vip/generate-bow/', {}, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Bow.objects.count() == initial_count + 1
        assert 'saved_bow' in response.data
        assert response.data['saved_to_db'] is True

    def test_generate_bow_logic_beginner_no_heavy_compound(self, api_client, beginner_member):
        """
        Generate bow for beginner should NOT suggest compound or heavy draw weight.
        General logic: beginner → light-to-medium, no compound.
        """
        beginner_member.is_vip = True
        beginner_member.save()
        api_client.force_authenticate(user=beginner_member)

        response = api_client.get('/api/vip/generate-bow/')
        assert response.status_code == status.HTTP_200_OK
        generated = response.data['generated_bow']
        # Beginners should not get compound
        assert generated['bow_type'] != 'compound', \
            "Beginner should not receive a compound bow"
        # Beginners with 20 lbs should not get heavy draw weight
        assert generated['draw_weight_lbs'] < 40, \
            f"Beginner bow draw weight too heavy: {generated['draw_weight_lbs']} lbs"

    def test_suggest_bow_prefers_matching_strength(self, api_client, sample_bows):
        """VIP member with high strength should receive a heavier bow suggestion."""
        heavy_member = ClubMemberModel.objects.create_user(
            username='strong_archer',
            email='strong@archery.club',
            password='testpass',
            height_cm=180,
            arm_length_cm=68,
            strength_lbs=55,
            age=30,
            experience='master',
            accuracy_pct=80.0,
            is_vip=True,
        )
        api_client.force_authenticate(user=heavy_member)
        response = api_client.get('/api/vip/suggest-bow/')
        assert response.status_code == status.HTTP_200_OK
        suggested = response.data['suggested_bow']
        assert suggested is not None
        # Should suggest a heavier bow (not the lightest one)
        assert suggested['draw_weight_lbs'] >= 25


# ═══════════════════════════════════════════════════
#  STATS API TESTS
# ═══════════════════════════════════════════════════

@pytest.mark.django_db
class TestStatsAPI:
    """Tests for /api/stats/ endpoint."""

    def test_stats_endpoint_returns_200(self, auth_client, regular_member, vip_member):
        """GET /api/stats/ returns 200 with correct structure."""
        response = auth_client.get('/api/stats/')
        assert response.status_code == status.HTTP_200_OK
        assert 'total_members' in response.data
        assert 'vip_members' in response.data
        assert 'regular_members' in response.data
        assert 'total_bows' in response.data
        assert 'experience_distribution' in response.data
        assert 'average_accuracy_pct' in response.data

    def test_stats_counts_correct(self, auth_client, regular_member, vip_member, sample_bows):
        """Stats should reflect actual DB state."""
        response = auth_client.get('/api/stats/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_bows'] == len(sample_bows)
        assert response.data['total_members'] >= 2
        assert response.data['vip_members'] >= 1

    def test_stats_unauthenticated(self, api_client):
        """GET /api/stats/ without auth returns 403."""
        response = api_client.get('/api/stats/')
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]


# ═══════════════════════════════════════════════════
#  MODEL UNIT TESTS
# ═══════════════════════════════════════════════════

@pytest.mark.django_db
class TestModels:
    """Unit tests for model properties and methods."""

    def test_bow_strength_category_light(self):
        """Bow with draw_weight < 25 is 'light'."""
        bow = Bow(draw_weight_lbs=20, length_cm=150, bow_type='shortbow', material='wood', name='t')
        assert bow.strength_category == 'light'

    def test_bow_strength_category_medium(self):
        """Bow with 25 <= draw_weight < 35 is 'medium'."""
        bow = Bow(draw_weight_lbs=30, length_cm=150, bow_type='recurve', material='wood', name='t')
        assert bow.strength_category == 'medium'

    def test_bow_strength_category_heavy(self):
        """Bow with draw_weight >= 35 is 'heavy'."""
        bow = Bow(draw_weight_lbs=50, length_cm=150, bow_type='compound', material='composite', name='t')
        assert bow.strength_category == 'heavy'

    def test_bow_size_category_short(self):
        """Bow with length < 130 cm is 'short'."""
        bow = Bow(length_cm=110, draw_weight_lbs=30, bow_type='shortbow', material='wood', name='t')
        assert bow.size_category == 'short'

    def test_bow_size_category_long(self):
        """Bow with length >= 170 cm is 'long'."""
        bow = Bow(length_cm=175, draw_weight_lbs=30, bow_type='longbow', material='wood', name='t')
        assert bow.size_category == 'long'

    def test_member_strength_category(self, regular_member):
        """ClubMember.strength_category reflects draw weight preference."""
        regular_member.strength_lbs = 20
        assert regular_member.strength_category == 'light'
        regular_member.strength_lbs = 28
        assert regular_member.strength_category == 'medium'
        regular_member.strength_lbs = 45
        assert regular_member.strength_category == 'heavy'

    def test_vip_member_suggest_bow(self, vip_member, sample_bows):
        """VIPMember.suggest_bow() returns a Bow instance."""
        from club_app.models import VIPMember, Bow
        vip = VIPMember.objects.get(pk=vip_member.pk)
        all_bows = Bow.objects.all()
        suggested = vip.suggest_bow(all_bows)
        assert suggested is not None
        assert isinstance(suggested, Bow)

    def test_vip_member_generate_perfect_bow(self, vip_member):
        """VIPMember.generate_perfect_bow() returns a valid dict."""
        from club_app.models import VIPMember
        vip = VIPMember.objects.get(pk=vip_member.pk)
        result = vip.generate_perfect_bow()

        assert 'name' in result
        assert 'bow_type' in result
        assert 'draw_weight_lbs' in result
        assert 'length_cm' in result
        assert 'material' in result
        assert 'reasoning' in result
        assert result['draw_weight_lbs'] > 0
        assert result['length_cm'] > 0
        assert result['generated_for'] == vip_member.username

    def test_member_str_representation(self, regular_member, vip_member):
        """ClubMember.__str__() includes VIP status."""
        assert 'Regular' in str(regular_member)
        assert 'VIP' in str(vip_member)

    def test_member_get_full_name(self, regular_member):
        """ClubMember.get_full_name() returns 'First Last'."""
        assert regular_member.get_full_name() == 'Robin Hood'

    def test_member_bow_str_representation(self, regular_member, single_bow):
        """MemberBow.__str__() shows member → bow."""
        mb = MemberBow.objects.create(member=regular_member, bow=single_bow)
        assert regular_member.username in str(mb)
        assert single_bow.name in str(mb)
