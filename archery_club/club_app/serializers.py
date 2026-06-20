
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import ClubMember, Bow, MemberBow, ExperienceLevel, BowType, BowMaterial


# ─────────────────────────────────────────────
#  BOW SERIALIZERS
# ─────────────────────────────────────────────

class BowSerializer(serializers.ModelSerializer):
    """Full read representation of a Bow."""

    bow_type_display = serializers.CharField(source='get_bow_type_display', read_only=True)
    material_display = serializers.CharField(source='get_material_display', read_only=True)
    strength_category = serializers.ReadOnlyField()
    size_category = serializers.ReadOnlyField()
    added_by_username = serializers.CharField(source='added_by.username', read_only=True, allow_null=True)

    class Meta:
        model = Bow
        fields = [
            'id',
            'name',
            'bow_type',
            'bow_type_display',
            'draw_weight_lbs',
            'length_cm',
            'material',
            'material_display',
            'strength_category',
            'size_category',
            'added_by',
            'added_by_username',
            'date_added',
            'notes',
        ]
        read_only_fields = ['id', 'date_added', 'added_by']


class BowCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating or updating a Bow.
    Validates that regular members don't exceed 3 bows.
    """

    class Meta:
        model = Bow
        fields = [
            'id',
            'name',
            'bow_type',
            'draw_weight_lbs',
            'length_cm',
            'material',
            'notes',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        """Check bow limit for regular members."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            # Only validate on create (not update)
            if not self.instance and not user.can_add_bow:
                raise serializers.ValidationError(
                    f"Regular members can only add up to 3 bows to their profile. "
                    f"You currently have {user.bow_count} bows. "
                    f"Upgrade to VIP for unlimited bows!"
                )
        return attrs

    def create(self, validated_data):
        """Automatically set added_by to the current user."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['added_by'] = request.user
        bow = Bow.objects.create(**validated_data)
        # Also link bow to the member
        member = validated_data.get('added_by')
        if member:
            MemberBow.objects.get_or_create(member=member, bow=bow)
        return bow


# ─────────────────────────────────────────────
#  MEMBER BOW SERIALIZER
# ─────────────────────────────────────────────

class MemberBowSerializer(serializers.ModelSerializer):
    """Serializer for MemberBow join model."""

    bow_detail = BowSerializer(source='bow', read_only=True)
    member_username = serializers.CharField(source='member.username', read_only=True)

    class Meta:
        model = MemberBow
        fields = ['id', 'member', 'member_username', 'bow', 'bow_detail', 'is_primary', 'date_added']
        read_only_fields = ['id', 'date_added', 'member']

    def validate(self, attrs):
        """Validate bow limit before linking."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if not self.instance and not user.can_add_bow:
                raise serializers.ValidationError(
                    "Regular members can only have up to 3 bows. Upgrade to VIP!"
                )
        return attrs


# ─────────────────────────────────────────────
#  CLUB MEMBER SERIALIZERS
# ─────────────────────────────────────────────

class ClubMemberSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for displaying member information.
    Includes nested bows and computed properties.
    """

    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    experience_display = serializers.CharField(source='get_experience_display', read_only=True)
    strength_category = serializers.ReadOnlyField()
    bow_count = serializers.ReadOnlyField()
    full_name = serializers.SerializerMethodField()
    bows = serializers.SerializerMethodField()

    class Meta:
        model = ClubMember
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'gender',
            'gender_display',
            'height_cm',
            'arm_length_cm',
            'strength_lbs',
            'strength_category',
            'age',
            'experience',
            'experience_display',
            'accuracy_pct',
            'is_vip',
            'bow_count',
            'bows',
            'date_joined',
        ]
        read_only_fields = fields  # This is a read-only serializer

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_bows(self, obj):
        """Return a list of bows linked to this member."""
        member_bows = obj.member_bows.select_related('bow').all()
        return [
            {
                'id': mb.bow.id,
                'name': mb.bow.name,
                'bow_type': mb.bow.get_bow_type_display(),
                'draw_weight_lbs': mb.bow.draw_weight_lbs,
                'length_cm': mb.bow.length_cm,
                'material': mb.bow.get_material_display(),
                'is_primary': mb.is_primary,
            }
            for mb in member_bows
        ]


class ClubMemberUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating member attributes.
    Does NOT allow changing username, email, or VIP status via this endpoint.
    """

    class Meta:
        model = ClubMember
        fields = [
            'first_name',
            'last_name',
            'gender',
            'height_cm',
            'arm_length_cm',
            'strength_lbs',
            'age',
            'experience',
            'accuracy_pct',
        ]

    def validate_accuracy_pct(self, value):
        if not (0 <= value <= 100):
            raise serializers.ValidationError("Accuracy must be between 0 and 100 percent.")
        return value

    def validate_strength_lbs(self, value):
        if not (10 <= value <= 100):
            raise serializers.ValidationError("Strength must be between 10 and 100 lbs.")
        return value


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new club member.
    Handles password confirmation and hashing.
    """

    password = serializers.CharField(write_only=True, min_length=6, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = ClubMember
        fields = [
            'username',
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'gender',
            'height_cm',
            'arm_length_cm',
            'strength_lbs',
            'age',
            'experience',
            'accuracy_pct',
        ]

    def validate(self, attrs):
        """Ensure passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        """Create a new ClubMember with hashed password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        member = ClubMember.objects.create_user(
            username=validated_data.pop('username'),
            email=validated_data.pop('email'),
            password=password,
            **validated_data
        )
        return member


class LoginSerializer(serializers.Serializer):
    """Serializer for authenticating a member."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid username or password.')
            if not user.is_active:
                raise serializers.ValidationError('Account is disabled.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must provide username and password.')
        return attrs


# ─────────────────────────────────────────────
#  VIP FEATURE SERIALIZERS
# ─────────────────────────────────────────────

class VIPSuggestBowResponseSerializer(serializers.Serializer):
    """Response serializer for the VIP 'suggest me a bow' feature."""

    suggested_bow = BowSerializer()
    score_explanation = serializers.CharField()
    member_profile_summary = serializers.DictField()


class VIPGenerateBowResponseSerializer(serializers.Serializer):
    """Response serializer for the VIP 'generate perfect bow' feature."""

    name = serializers.CharField()
    bow_type = serializers.CharField()
    draw_weight_lbs = serializers.IntegerField()
    length_cm = serializers.IntegerField()
    material = serializers.CharField()
    generated_for = serializers.CharField()
    reasoning = serializers.CharField()
    save_to_db = serializers.BooleanField(default=False, required=False)
