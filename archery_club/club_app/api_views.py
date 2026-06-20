"""
REST API Views for the Archery Club application.
Uses Django REST Framework.

API Endpoints:
  GET/POST   /api/members/                  ← list members / register
  GET/PUT    /api/members/<id>/             ← member detail / update
  GET/POST   /api/bows/                     ← list bows / create bow
  GET/PUT/DELETE /api/bows/<id>/            ← bow detail / update / delete
  POST       /api/bows/<id>/add-to-profile/ ← add bow to member's profile
  DELETE     /api/bows/<id>/remove-from-profile/ ← remove bow from profile
  GET        /api/my-bows/                  ← current user's bows
  POST       /api/auth/login/               ← login
  POST       /api/auth/register/            ← register
  GET        /api/vip/suggest-bow/          ← VIP: suggest a bow
  GET        /api/vip/generate-bow/         ← VIP: generate perfect bow
  POST       /api/vip/generate-bow/         ← VIP: generate + save to DB
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404

from .models import ClubMember, Bow, MemberBow, VIPMember
from .serializers import (
    ClubMemberSerializer,
    ClubMemberUpdateSerializer,
    RegisterSerializer,
    LoginSerializer,
    BowSerializer,
    BowCreateSerializer,
    MemberBowSerializer,
    VIPSuggestBowResponseSerializer,
    VIPGenerateBowResponseSerializer,
)


# ─────────────────────────────────────────────
#  AUTHENTICATION API
# ─────────────────────────────────────────────

class APIRegisterView(APIView):
    """
    POST /api/auth/register/
    Register a new club member.
    Permission: AllowAny
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            member = serializer.save()
            return Response(
                {
                    'message': 'Registration successful! Welcome to the Archery Club!',
                    'member': ClubMemberSerializer(member).data,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APILoginView(APIView):
    """
    POST /api/auth/login/
    Authenticate a member and start a session.
    Permission: AllowAny
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response(
                {
                    'message': f'Welcome back, {user.get_short_name()}!',
                    'member': ClubMemberSerializer(user).data,
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APILogoutView(APIView):
    """
    POST /api/auth/logout/
    Log out the current member.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────
#  MEMBER API VIEWS
# ─────────────────────────────────────────────

class APIMemberListView(APIView):
    """
    GET  /api/members/  → list all active members
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        members = ClubMember.objects.filter(is_active=True)

        # Optional filters via query params
        experience = request.query_params.get('experience')
        gender = request.query_params.get('gender')
        is_vip = request.query_params.get('is_vip')

        if experience:
            members = members.filter(experience=experience)
        if gender:
            members = members.filter(gender=gender)
        if is_vip is not None:
            members = members.filter(is_vip=is_vip.lower() == 'true')

        serializer = ClubMemberSerializer(members, many=True)
        return Response({
            'count': members.count(),
            'results': serializer.data,
        })


class APIMemberDetailView(APIView):
    """
    GET /api/members/<id>/   → member detail
    PUT /api/members/<id>/   → update own profile (or admin any profile)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        member = get_object_or_404(ClubMember, pk=pk, is_active=True)
        serializer = ClubMemberSerializer(member)
        return Response(serializer.data)

    def put(self, request, pk):
        member = get_object_or_404(ClubMember, pk=pk, is_active=True)
        # Only allow editing own profile (or admin)
        if member != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only edit your own profile.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = ClubMemberUpdateSerializer(member, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(ClubMemberSerializer(member).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        return self.put(request, pk)


class APIMeView(APIView):
    """
    GET  /api/me/  → current user's profile
    PUT  /api/me/  → update current user's profile
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ClubMemberSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = ClubMemberUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(ClubMemberSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        return self.put(request)


# ─────────────────────────────────────────────
#  BOW API VIEWS
# ─────────────────────────────────────────────

class APIBowListView(APIView):
    """
    GET  /api/bows/  → list all bows (with optional filters)
    POST /api/bows/  → create a new bow (auto-linked to current user)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bows = Bow.objects.select_related('added_by').all()

        # Filters
        bow_type = request.query_params.get('type')
        material = request.query_params.get('material')
        min_weight = request.query_params.get('min_weight')
        max_weight = request.query_params.get('max_weight')
        min_length = request.query_params.get('min_length')
        max_length = request.query_params.get('max_length')

        if bow_type:
            bows = bows.filter(bow_type=bow_type)
        if material:
            bows = bows.filter(material=material)
        if min_weight:
            bows = bows.filter(draw_weight_lbs__gte=int(min_weight))
        if max_weight:
            bows = bows.filter(draw_weight_lbs__lte=int(max_weight))
        if min_length:
            bows = bows.filter(length_cm__gte=int(min_length))
        if max_length:
            bows = bows.filter(length_cm__lte=int(max_length))

        serializer = BowSerializer(bows, many=True)
        return Response({
            'count': bows.count(),
            'results': serializer.data,
        })

    def post(self, request):
        serializer = BowCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            bow = serializer.save()
            return Response(
                BowSerializer(bow).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APIBowDetailView(APIView):
    """
    GET    /api/bows/<id>/  → bow detail
    PUT    /api/bows/<id>/  → update bow (only creator or admin)
    DELETE /api/bows/<id>/  → delete bow (only creator or admin)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        bow = get_object_or_404(Bow, pk=pk)
        serializer = BowSerializer(bow)
        return Response(serializer.data)

    def put(self, request, pk):
        bow = get_object_or_404(Bow, pk=pk)
        if bow.added_by != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only edit bows you added.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = BowCreateSerializer(bow, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(BowSerializer(bow).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        return self.put(request, pk)

    def delete(self, request, pk):
        bow = get_object_or_404(Bow, pk=pk)
        if bow.added_by != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only delete bows you added.'},
                status=status.HTTP_403_FORBIDDEN
            )
        bow_name = bow.name
        bow.delete()
        return Response(
            {'message': f"Bow '{bow_name}' deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )


class APIMyBowsView(APIView):
    """
    GET    /api/my-bows/        → list current user's bows
    POST   /api/my-bows/        → add existing bow to profile
    DELETE /api/my-bows/<bow_id>/ → remove bow from profile
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        member_bows = MemberBow.objects.filter(member=request.user).select_related('bow')
        serializer = MemberBowSerializer(member_bows, many=True)
        return Response({
            'count': member_bows.count(),
            'bow_limit': None if request.user.is_vip else 3,
            'can_add_more': request.user.can_add_bow,
            'results': serializer.data,
        })

    def post(self, request):
        bow_id = request.data.get('bow_id')
        if not bow_id:
            return Response({'error': 'bow_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        bow = get_object_or_404(Bow, pk=bow_id)

        if not request.user.can_add_bow:
            return Response(
                {'error': 'Regular members can only have up to 3 bows. Upgrade to VIP!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        member_bow, created = MemberBow.objects.get_or_create(member=request.user, bow=bow)
        if not created:
            return Response({'message': 'Bow already in your profile.'}, status=status.HTTP_200_OK)

        return Response(
            MemberBowSerializer(member_bow).data,
            status=status.HTTP_201_CREATED
        )


class APIRemoveBowFromProfileView(APIView):
    """DELETE /api/my-bows/<bow_id>/ → remove bow from current user's profile."""
    permission_classes = [IsAuthenticated]

    def delete(self, request, bow_id):
        member_bow = get_object_or_404(MemberBow, member=request.user, bow_id=bow_id)
        member_bow.delete()
        return Response({'message': 'Bow removed from your profile.'}, status=status.HTTP_204_NO_CONTENT)


# ─────────────────────────────────────────────
#  VIP API VIEWS
# ─────────────────────────────────────────────

class APIVIPSuggestBowView(APIView):
    """
    GET /api/vip/suggest-bow/
    Suggest the most fitting bow from the DB for the current VIP member.
    Permission: IsAuthenticated + is_vip
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_vip:
            return Response(
                {'error': 'This feature is available for VIP members only.'},
                status=status.HTTP_403_FORBIDDEN
            )

        vip_member = VIPMember.objects.get(pk=request.user.pk)
        all_bows = Bow.objects.all()

        if not all_bows.exists():
            return Response(
                {'message': 'No bows in the database yet. Add some first!'},
                status=status.HTTP_200_OK
            )

        suggested_bow = vip_member.suggest_bow(all_bows)

        return Response({
            'suggested_bow': BowSerializer(suggested_bow).data if suggested_bow else None,
            'member_profile_summary': {
                'height_cm': request.user.height_cm,
                'arm_length_cm': request.user.arm_length_cm,
                'strength_lbs': request.user.strength_lbs,
                'strength_category': request.user.strength_category,
                'experience': request.user.experience,
                'accuracy_pct': request.user.accuracy_pct,
            },
            'score_explanation': (
                "Score based on: draw weight match (40 pts), "
                "bow length vs height match (30 pts), "
                "experience compatibility (20 pts), "
                "strength+size special bonus (10 pts)"
            ),
        })


class APIVIPGenerateBowView(APIView):
    """
    GET  /api/vip/generate-bow/  → generate bow spec (not saved)
    POST /api/vip/generate-bow/  → generate bow spec + save to DB
    Permission: IsAuthenticated + is_vip
    """
    permission_classes = [IsAuthenticated]

    def _check_vip(self, request):
        if not request.user.is_vip:
            return Response(
                {'error': 'This feature is available for VIP members only.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return None

    def get(self, request):
        err = self._check_vip(request)
        if err:
            return err

        vip_member = VIPMember.objects.get(pk=request.user.pk)
        generated = vip_member.generate_perfect_bow()

        return Response({
            'generated_bow': generated,
            'saved_to_db': False,
            'message': 'This is your perfect bow specification. POST to this endpoint to save it to the database.',
        })

    def post(self, request):
        err = self._check_vip(request)
        if err:
            return err

        vip_member = VIPMember.objects.get(pk=request.user.pk)
        generated = vip_member.generate_perfect_bow()

        # Save to database
        bow = Bow.objects.create(
            name=generated['name'],
            bow_type=generated['bow_type'],
            draw_weight_lbs=generated['draw_weight_lbs'],
            length_cm=generated['length_cm'],
            material=generated['material'],
            added_by=request.user,
            notes=f"[AUTO-GENERATED] {generated['reasoning']}",
        )
        MemberBow.objects.get_or_create(member=request.user, bow=bow)

        return Response({
            'generated_bow': generated,
            'saved_bow': BowSerializer(bow).data,
            'saved_to_db': True,
            'message': f"Perfect bow '{bow.name}' generated and saved to the database!",
        }, status=status.HTTP_201_CREATED)


# ─────────────────────────────────────────────
#  UTILITY / STATS API
# ─────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_stats(request):
    """
    GET /api/stats/
    Returns overall club statistics.
    """
    total_members = ClubMember.objects.filter(is_active=True).count()
    vip_members = ClubMember.objects.filter(is_vip=True, is_active=True).count()
    total_bows = Bow.objects.count()

    from .models import ExperienceLevel
    experience_dist = {}
    for level in ExperienceLevel:
        count = ClubMember.objects.filter(experience=level.value, is_active=True).count()
        experience_dist[level.label] = count

    avg_accuracy = ClubMember.objects.filter(is_active=True).values_list('accuracy_pct', flat=True)
    avg_acc = round(sum(avg_accuracy) / len(avg_accuracy), 2) if avg_accuracy else 0

    return Response({
        'total_members': total_members,
        'vip_members': vip_members,
        'regular_members': total_members - vip_members,
        'total_bows': total_bows,
        'experience_distribution': experience_dist,
        'average_accuracy_pct': avg_acc,
    })
