
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import ClubMember, Bow, MemberBow, VIPMember


# ─────────────────────────────────────────────
#  MEMBER ADMIN
# ─────────────────────────────────────────────

@admin.register(ClubMember)
class ClubMemberAdmin(UserAdmin):
    """Admin interface for ClubMember."""

    list_display = [
        'username', 'email', 'get_full_name', 'gender',
        'experience', 'accuracy_badge', 'strength_lbs',
        'bow_count', 'is_vip', 'is_active', 'date_joined',
    ]
    list_filter = ['is_vip', 'is_active', 'gender', 'experience', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']

    fieldsets = (
        ('Account', {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'gender', 'age')}),
        ('Physical Attributes', {'fields': ('height_cm', 'arm_length_cm')}),
        ('Archery Attributes', {'fields': ('strength_lbs', 'experience', 'accuracy_pct')}),
        ('Permissions', {'fields': ('is_vip', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('date_joined',)}),
    )

    add_fieldsets = (
        ('Account', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'gender', 'age'),
        }),
        ('Physical Attributes', {
            'fields': ('height_cm', 'arm_length_cm'),
        }),
        ('Archery Attributes', {
            'fields': ('strength_lbs', 'experience', 'accuracy_pct'),
        }),
        ('Permissions', {
            'fields': ('is_vip', 'is_active', 'is_staff'),
        }),
    )

    def accuracy_badge(self, obj):
        color = 'green' if obj.accuracy_pct >= 70 else 'orange' if obj.accuracy_pct >= 40 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, obj.accuracy_pct
        )
    accuracy_badge.short_description = 'Accuracy'

    def bow_count(self, obj):
        return obj.bow_count
    bow_count.short_description = '# Bows'


@admin.register(VIPMember)
class VIPMemberAdmin(ClubMemberAdmin):
    """Admin for VIP Members (proxy model)."""

    list_display = ClubMemberAdmin.list_display
    list_filter = ['is_active', 'gender', 'experience']

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_vip=True)


# ─────────────────────────────────────────────
#  BOW ADMIN
# ─────────────────────────────────────────────

@admin.register(Bow)
class BowAdmin(admin.ModelAdmin):
    """Admin interface for Bows."""

    list_display = [
        'name', 'bow_type', 'draw_weight_lbs', 'strength_category_display',
        'length_cm', 'size_category_display', 'material', 'added_by', 'date_added',
    ]
    list_filter = ['bow_type', 'material']
    search_fields = ['name', 'added_by__username', 'notes']
    ordering = ['name']
    readonly_fields = ['date_added', 'added_by']

    def strength_category_display(self, obj):
        colors = {'light': 'blue', 'medium': 'orange', 'heavy': 'red'}
        color = colors.get(obj.strength_category, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.strength_category.capitalize()
        )
    strength_category_display.short_description = 'Strength'

    def size_category_display(self, obj):
        return obj.size_category.capitalize()
    size_category_display.short_description = 'Size'


# ─────────────────────────────────────────────
#  MEMBER-BOW ADMIN
# ─────────────────────────────────────────────

@admin.register(MemberBow)
class MemberBowAdmin(admin.ModelAdmin):
    """Admin interface for MemberBow (who has which bow)."""

    list_display = ['member', 'bow', 'is_primary', 'date_added']
    list_filter = ['is_primary']
    search_fields = ['member__username', 'bow__name']
    ordering = ['member__username']


# ── Admin Site Customization ─────────────────
admin.site.site_header = "🏹 Archery Club Administration"
admin.site.site_title = "Archery Club Admin"
admin.site.index_title = "Club Management Panel"
