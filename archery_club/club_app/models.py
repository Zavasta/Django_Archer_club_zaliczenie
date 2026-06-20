"""
Models for the Archery Club application.

Class hierarchy:
  AbstractBaseUser (Django)
    └── ClubMember          ← custom user model with archery attributes
          └── VIPMember     ← proxy model with extra permissions/features

  Model
    └── Bow                 ← represents a bow in the database
    └── MemberBow           ← many-to-many linking members to their bows
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


# ─────────────────────────────────────────────
#  CHOICES
# ─────────────────────────────────────────────

class Gender(models.TextChoices):
    MALE = 'M', 'Male'
    FEMALE = 'F', 'Female'
    OTHER = 'O', 'Other'


class ExperienceLevel(models.TextChoices):
    BEGINNER = 'beginner', 'Beginner'
    ADEPT = 'adept', 'Adept'
    ADVANCED = 'advanced', 'Advanced'
    MASTER = 'master', 'Master'


class BowType(models.TextChoices):
    LONGBOW = 'longbow', 'Long Bow'
    SHORTBOW = 'shortbow', 'Short Bow'
    RECURVE = 'recurve', 'Recurve Bow'
    COMPOUND = 'compound', 'Compound Bow'
    CROSSBOW = 'crossbow', 'Crossbow'


class BowMaterial(models.TextChoices):
    WOOD = 'wood', 'Wood'
    COMPOSITE = 'composite', 'Composite'
    CARBON = 'carbon', 'Carbon Fiber'
    FIBERGLASS = 'fiberglass', 'Fiberglass'
    HYBRID = 'hybrid', 'Hybrid (Wood + Composite)'


# ─────────────────────────────────────────────
#  CUSTOM USER MANAGER
# ─────────────────────────────────────────────

class ClubMemberManager(BaseUserManager):
    """
    Custom manager for ClubMember.
    Handles create_user and create_superuser with our custom fields.
    """

    def create_user(self, username, email, password=None, **extra_fields):
        """Create and return a regular club member."""
        if not username:
            raise ValueError('The username must be set')
        if not email:
            raise ValueError('The email must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_vip', False)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """Create and return a superuser (admin)."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_vip', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

    def vip_members(self):
        """Return only VIP members."""
        return self.filter(is_vip=True)

    def regular_members(self):
        """Return only regular (non-VIP) members."""
        return self.filter(is_vip=False)


# ─────────────────────────────────────────────
#  CLUB MEMBER (Custom User Model)
# ─────────────────────────────────────────────

class ClubMember(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model representing an archery club member.

    Extends Django's AbstractBaseUser to include archery-specific attributes
    such as physical measurements and skill level.

    Attributes:
        username        -- unique login identifier
        email           -- contact email
        first_name      -- member's first name
        last_name       -- member's last name
        gender          -- M/F/O
        height_cm       -- height in centimeters (100-250)
        arm_length_cm   -- arm length / draw length in centimeters (40-120)
        strength_lbs    -- comfortable bow draw weight in lbs (20-80)
        age             -- member's age (5-100)
        experience      -- beginner / adept / advanced / master
        accuracy_pct    -- percentage of shots hitting the centre (0-100)
        is_vip          -- VIP members have extended privileges
        is_staff        -- can access Django admin
        date_joined     -- when the member registered
    """

    # ── Identity ──────────────────────────────
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)

    # ── Physical Attributes ───────────────────
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        default=Gender.OTHER
    )
    height_cm = models.PositiveIntegerField(
        default=170,
        validators=[MinValueValidator(100), MaxValueValidator(250)],
        help_text='Height in centimeters'
    )
    arm_length_cm = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(40), MaxValueValidator(120)],
        help_text='Arm length (draw length) in centimeters'
    )

    # ── Archery Attributes ────────────────────
    strength_lbs = models.PositiveIntegerField(
        default=25,
        validators=[MinValueValidator(10), MaxValueValidator(100)],
        help_text='Comfortable draw weight in lbs (20=light, 40+=heavy)'
    )
    age = models.PositiveIntegerField(
        default=25,
        validators=[MinValueValidator(5), MaxValueValidator(100)]
    )
    experience = models.CharField(
        max_length=20,
        choices=ExperienceLevel.choices,
        default=ExperienceLevel.BEGINNER
    )
    accuracy_pct = models.FloatField(
        default=50.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text='Percentage of shots hitting the centre (0-100%)'
    )

    # ── VIP & Admin Flags ─────────────────────
    is_vip = models.BooleanField(
        default=False,
        help_text='VIP members: unlimited bows + bow suggestion + bow generation'
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = ClubMemberManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'Club Member'
        verbose_name_plural = 'Club Members'
        ordering = ['username']

    def __str__(self):
        return f"{self.username} ({'VIP' if self.is_vip else 'Regular'})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def get_short_name(self):
        return self.first_name or self.username

    @property
    def strength_category(self):
        """Classify member strength level based on comfortable draw weight."""
        if self.strength_lbs < 25:
            return 'light'
        elif self.strength_lbs < 35:
            return 'medium'
        else:
            return 'heavy'

    @property
    def bow_count(self):
        """Return number of bows currently assigned to this member."""
        return self.member_bows.count()

    @property
    def can_add_bow(self):
        """
        Regular members: max 3 bows.
        VIP members: unlimited.
        """
        if self.is_vip:
            return True
        return self.bow_count < 3


# ─────────────────────────────────────────────
#  VIP MEMBER PROXY
# ─────────────────────────────────────────────

class VIPMemberManager(ClubMemberManager):
    """Manager that only returns VIP members."""
    def get_queryset(self):
        return super().get_queryset().filter(is_vip=True)


class VIPMember(ClubMember):
    """
    Proxy model for VIP ClubMembers.
    Adds VIP-specific logic (bow suggestion & generation)
    without creating a separate DB table.
    """

    objects = VIPMemberManager()

    class Meta:
        proxy = True
        verbose_name = 'VIP Member'
        verbose_name_plural = 'VIP Members'

    def suggest_bow(self, bows_queryset):
        """
        Suggest the most fitting bow from the database for this VIP member.

        Scoring logic:
          - Strength match:    |bow.draw_weight - member.strength_lbs| -> lower is better
          - Height match:      shorter member → shorter bow, taller → longer bow
          - Experience match:  beginners avoid compound/heavy bows
          - Gender/strength exception: short but strong → short but strong bow

        Returns the Bow instance with the highest score, or None.
        """
        if not bows_queryset.exists():
            return None

        def score_bow(bow):
            score = 0

            # 1. Strength match (most important — weight: 40 pts)
            strength_diff = abs(bow.draw_weight_lbs - self.strength_lbs)
            score += max(0, 40 - strength_diff)

            # 2. Bow length vs member height (weight: 30 pts)
            # Ideal bow length heuristic: height_cm / 3 → length in cm
            ideal_length = self.height_cm / 3
            length_diff = abs(bow.length_cm - ideal_length)
            score += max(0, 30 - length_diff / 2)

            # 3. Experience level compatibility (weight: 20 pts)
            experience_scores = {
                ExperienceLevel.BEGINNER: {
                    BowType.LONGBOW: 15,
                    BowType.SHORTBOW: 20,
                    BowType.RECURVE: 10,
                    BowType.COMPOUND: 0,
                    BowType.CROSSBOW: 5,
                },
                ExperienceLevel.ADEPT: {
                    BowType.LONGBOW: 18,
                    BowType.SHORTBOW: 18,
                    BowType.RECURVE: 20,
                    BowType.COMPOUND: 10,
                    BowType.CROSSBOW: 12,
                },
                ExperienceLevel.ADVANCED: {
                    BowType.LONGBOW: 15,
                    BowType.SHORTBOW: 15,
                    BowType.RECURVE: 20,
                    BowType.COMPOUND: 20,
                    BowType.CROSSBOW: 15,
                },
                ExperienceLevel.MASTER: {
                    BowType.LONGBOW: 20,
                    BowType.SHORTBOW: 15,
                    BowType.RECURVE: 20,
                    BowType.COMPOUND: 20,
                    BowType.CROSSBOW: 15,
                },
            }
            exp_map = experience_scores.get(self.experience, {})
            score += exp_map.get(bow.bow_type, 10)

            # 4. Special case: short but strong → short strong bow bonus
            if self.height_cm < 165 and self.strength_lbs >= 35:
                if bow.length_cm < 150 and bow.draw_weight_lbs >= 35:
                    score += 10

            return score

        best_bow = max(bows_queryset, key=score_bow)
        return best_bow

    def generate_perfect_bow(self):
        """
        Generate a 'perfect bow' specification for this VIP member.

        Returns a dict with ideal bow attributes (NOT saved to DB automatically).

        Logic:
          - draw_weight: member's stated strength ± small adjustment for accuracy
          - length: based on height (tall → long bow)
          - type: based on experience + height + strength
          - material: based on experience (beginners → wood, advanced → composite)
          - name: auto-generated descriptive name
        """
        # ── Draw Weight ───────────────────────
        # High accuracy → can handle slightly more weight
        accuracy_bonus = (self.accuracy_pct - 50) / 100 * 5  # -2.5 to +2.5
        ideal_weight = round(self.strength_lbs + accuracy_bonus)
        ideal_weight = max(15, min(80, ideal_weight))

        # ── Bow Length ────────────────────────
        # Formula: height * 0.95 for average arm, adjusted by arm_length
        arm_factor = (self.arm_length_cm - 60) * 0.5  # deviation from avg arm
        ideal_length = round(self.height_cm * 0.95 + arm_factor)
        ideal_length = max(100, min(220, ideal_length))

        # ── Bow Type ─────────────────────────
        if self.experience == ExperienceLevel.BEGINNER:
            if self.height_cm >= 175:
                bow_type = BowType.LONGBOW
            else:
                bow_type = BowType.SHORTBOW
        elif self.experience == ExperienceLevel.ADEPT:
            bow_type = BowType.RECURVE
        elif self.experience == ExperienceLevel.ADVANCED:
            if self.strength_lbs >= 40:
                bow_type = BowType.COMPOUND
            else:
                bow_type = BowType.RECURVE
        else:  # MASTER
            if self.accuracy_pct >= 70:
                bow_type = BowType.LONGBOW  # masters go traditional
            else:
                bow_type = BowType.COMPOUND

        # ── Material ─────────────────────────
        if self.experience in [ExperienceLevel.BEGINNER, ExperienceLevel.ADEPT]:
            material = BowMaterial.WOOD
        elif self.experience == ExperienceLevel.ADVANCED:
            material = BowMaterial.COMPOSITE
        else:  # MASTER
            if self.accuracy_pct >= 75:
                material = BowMaterial.CARBON
            else:
                material = BowMaterial.HYBRID

        # ── Auto Name ─────────────────────────
        strength_label = self.strength_category.capitalize()
        exp_label = self.experience.capitalize()
        name = f"Perfect {exp_label} {bow_type.replace('bow', ' Bow').title()} ({strength_label})"

        return {
            'name': name,
            'bow_type': bow_type,
            'draw_weight_lbs': ideal_weight,
            'length_cm': ideal_length,
            'material': material,
            'generated_for': self.username,
            'reasoning': (
                f"Based on: height={self.height_cm}cm, arm={self.arm_length_cm}cm, "
                f"strength={self.strength_lbs}lbs, experience={self.experience}, "
                f"accuracy={self.accuracy_pct}%"
            ),
        }


# ─────────────────────────────────────────────
#  BOW MODEL
# ─────────────────────────────────────────────

class Bow(models.Model):
    """
    Represents a bow stored in the club's database.

    Attributes:
        name            -- descriptive name of the bow
        bow_type        -- longbow / shortbow / recurve / compound / crossbow
        draw_weight_lbs -- tension / draw weight in pounds (lbs)
        length_cm       -- length of the bow in centimeters
        material        -- wood / composite / carbon / fiberglass / hybrid
        added_by        -- which member added this bow (ForeignKey)
        date_added      -- when it was added
        notes           -- optional extra notes
    """

    name = models.CharField(max_length=100)
    bow_type = models.CharField(
        max_length=20,
        choices=BowType.choices,
        default=BowType.RECURVE
    )
    draw_weight_lbs = models.PositiveIntegerField(
        validators=[MinValueValidator(5), MaxValueValidator(100)],
        help_text='Draw weight (tension) in pounds'
    )
    length_cm = models.PositiveIntegerField(
        validators=[MinValueValidator(50), MaxValueValidator(250)],
        help_text='Bow length in centimeters'
    )
    material = models.CharField(
        max_length=20,
        choices=BowMaterial.choices,
        default=BowMaterial.WOOD
    )
    added_by = models.ForeignKey(
        ClubMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='added_bows',
        help_text='Member who added this bow to the database'
    )
    date_added = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, help_text='Optional notes about this bow')

    class Meta:
        verbose_name = 'Bow'
        verbose_name_plural = 'Bows'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_bow_type_display()}, {self.draw_weight_lbs}lbs, {self.length_cm}cm)"

    @property
    def strength_category(self):
        """Classify bow draw weight."""
        if self.draw_weight_lbs < 25:
            return 'light'
        elif self.draw_weight_lbs < 35:
            return 'medium'
        else:
            return 'heavy'

    @property
    def size_category(self):
        """Classify bow size by length."""
        if self.length_cm < 130:
            return 'short'
        elif self.length_cm < 170:
            return 'medium'
        else:
            return 'long'


# ─────────────────────────────────────────────
#  MEMBER-BOW LINK (Many-to-Many with extra info)
# ─────────────────────────────────────────────

class MemberBow(models.Model):
    """
    Links a ClubMember to a Bow they own/use.

    A regular member can have at most 3 bows (enforced at view/serializer level).
    A VIP member has no limit.

    Attributes:
        member      -- the club member
        bow         -- the bow
        is_primary  -- is this the member's primary/favourite bow?
        date_added  -- when the member added this bow to their profile
    """

    member = models.ForeignKey(
        ClubMember,
        on_delete=models.CASCADE,
        related_name='member_bows'
    )
    bow = models.ForeignKey(
        Bow,
        on_delete=models.CASCADE,
        related_name='bow_members'
    )
    is_primary = models.BooleanField(
        default=False,
        help_text='Mark as primary/favourite bow'
    )
    date_added = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Member Bow'
        verbose_name_plural = 'Member Bows'
        unique_together = [('member', 'bow')]
        ordering = ['-is_primary', 'date_added']

    def __str__(self):
        primary = ' [PRIMARY]' if self.is_primary else ''
        return f"{self.member.username} → {self.bow.name}{primary}"

    def save(self, *args, **kwargs):
        """Enforce bow limit for regular members before saving."""
        if not self.pk:  # only on creation
            if not self.member.can_add_bow:
                raise ValueError(
                    f"Regular members can only have up to 3 bows. "
                    f"{self.member.username} already has {self.member.bow_count}."
                )
        super().save(*args, **kwargs)
