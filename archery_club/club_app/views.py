"""
Views for the Archery Club application.

View hierarchy:
  View (Django)
    ├── WelcomeView          ← landing page
    ├── LoginView            ← login form
    ├── LogoutView           ← logout action
    ├── RegisterView         ← new member registration
    ├── DashboardView        ← member dashboard (own bows + attributes)
    ├── ProfileEditView      ← edit member attributes
    ├── BowListView          ← browse all bows
    ├── BowAddView           ← add a new bow
    ├── BowEditView          ← edit an existing bow
    ├── BowDeleteView        ← delete a bow
    ├── MemberListView       ← browse all members
    ├── MemberDetailView     ← view one member's stats
    ├── VIPSuggestBowView    ← VIP: suggest a fitting bow
    └── VIPGenerateBowView   ← VIP: generate a perfect bow spec
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseForbidden

from .models import ClubMember, Bow, MemberBow, VIPMember
from .forms import (
    LoginForm, RegisterForm, ProfileEditForm,
    BowForm, MemberBowLinkForm
)


# ─────────────────────────────────────────────
#  MIXINS
# ─────────────────────────────────────────────

class VIPRequiredMixin(LoginRequiredMixin):
    """Mixin that restricts access to VIP members only."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_vip:
            messages.error(request, "🏹 This feature is available for VIP members only!")
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


# ─────────────────────────────────────────────
#  AUTHENTICATION VIEWS
# ─────────────────────────────────────────────

class WelcomeView(View):
    """Landing page — redirect to dashboard if logged in, else show welcome."""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'club_app/welcome.html')


class LoginView(View):
    """Login form view."""

    template_name = 'club_app/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f"Welcome back, {user.get_short_name()}! 🏹")
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
        return render(request, self.template_name, {'form': form})


class LogoutView(LoginRequiredMixin, View):
    """Logout action."""

    def post(self, request):
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect('login')

    def get(self, request):
        logout(request)
        return redirect('login')


class RegisterView(View):
    """New member registration form."""

    template_name = 'club_app/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = RegisterForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            messages.success(request, f"Welcome to the Archery Club, {user.get_short_name()}! 🎯")
            return redirect('dashboard')
        return render(request, self.template_name, {'form': form})


# ─────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────

class DashboardView(LoginRequiredMixin, View):
    """
    Member dashboard.
    Shows: member's attributes, their bows, VIP status, quick stats.
    """

    template_name = 'club_app/dashboard.html'

    def get(self, request):
        member = request.user
        member_bows = MemberBow.objects.filter(member=member).select_related('bow')
        all_members_count = ClubMember.objects.filter(is_active=True).count()
        all_bows_count = Bow.objects.count()

        context = {
            'member': member,
            'member_bows': member_bows,
            'all_members_count': all_members_count,
            'all_bows_count': all_bows_count,
            'can_add_bow': member.can_add_bow,
            'bow_limit': None if member.is_vip else 3,
        }
        return render(request, self.template_name, context)


# ─────────────────────────────────────────────
#  PROFILE
# ─────────────────────────────────────────────

class ProfileEditView(LoginRequiredMixin, View):
    """Edit member's archery attributes."""

    template_name = 'club_app/profile_edit.html'

    def get(self, request):
        form = ProfileEditForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ProfileEditForm(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully! 🎯")
            return redirect('dashboard')
        return render(request, self.template_name, {'form': form})


# ─────────────────────────────────────────────
#  BOW VIEWS
# ─────────────────────────────────────────────

class BowListView(LoginRequiredMixin, View):
    """Browse all bows in the database."""

    template_name = 'club_app/bow_list.html'

    def get(self, request):
        bows = Bow.objects.select_related('added_by').all()

        # Filtering
        bow_type = request.GET.get('type', '')
        material = request.GET.get('material', '')
        strength = request.GET.get('strength', '')

        if bow_type:
            bows = bows.filter(bow_type=bow_type)
        if material:
            bows = bows.filter(material=material)
        if strength == 'light':
            bows = bows.filter(draw_weight_lbs__lt=25)
        elif strength == 'medium':
            bows = bows.filter(draw_weight_lbs__gte=25, draw_weight_lbs__lt=35)
        elif strength == 'heavy':
            bows = bows.filter(draw_weight_lbs__gte=35)

        # Get member's bow ids for UI highlighting
        member_bow_ids = set(
            MemberBow.objects.filter(member=request.user).values_list('bow_id', flat=True)
        )

        from .models import BowType as BT, BowMaterial as BM
        context = {
            'bows': bows,
            'member_bow_ids': member_bow_ids,
            'bow_types': BT.choices,
            'bow_materials': BM.choices,
            'selected_type': bow_type,
            'selected_material': material,
            'selected_strength': strength,
            'can_add_bow': request.user.can_add_bow,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """Add an existing bow to the member's profile."""
        bow_id = request.POST.get('bow_id')
        bow = get_object_or_404(Bow, pk=bow_id)
        member = request.user

        if not member.can_add_bow:
            messages.error(request, "You've reached the maximum of 3 bows. Upgrade to VIP for unlimited bows!")
            return redirect('bow_list')

        _, created = MemberBow.objects.get_or_create(member=member, bow=bow)
        if created:
            messages.success(request, f"🏹 '{bow.name}' added to your profile!")
        else:
            messages.info(request, f"You already have '{bow.name}' in your profile.")
        return redirect('bow_list')


class BowAddView(LoginRequiredMixin, View):
    """Add a new bow to the database (and optionally to own profile)."""

    template_name = 'club_app/bow_add.html'

    def get(self, request):
        if not request.user.can_add_bow:
            messages.error(request, "You've reached the maximum of 3 bows. Upgrade to VIP for unlimited bows!")
            return redirect('bow_list')
        form = BowForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if not request.user.can_add_bow:
            messages.error(request, "You've reached the maximum of 3 bows.")
            return redirect('bow_list')

        form = BowForm(data=request.POST)
        if form.is_valid():
            bow = form.save(commit=False)
            bow.added_by = request.user
            bow.save()
            # Link to member's profile
            MemberBow.objects.create(member=request.user, bow=bow)
            messages.success(request, f"🏹 '{bow.name}' added successfully!")
            return redirect('dashboard')
        return render(request, self.template_name, {'form': form})


class BowEditView(LoginRequiredMixin, View):
    """Edit an existing bow (only the member who added it, or admin)."""

    template_name = 'club_app/bow_edit.html'

    def get(self, request, pk):
        bow = get_object_or_404(Bow, pk=pk)
        if bow.added_by != request.user and not request.user.is_staff:
            messages.error(request, "You can only edit bows you added.")
            return redirect('bow_list')
        form = BowForm(instance=bow)
        return render(request, self.template_name, {'form': form, 'bow': bow})

    def post(self, request, pk):
        bow = get_object_or_404(Bow, pk=pk)
        if bow.added_by != request.user and not request.user.is_staff:
            messages.error(request, "You can only edit bows you added.")
            return redirect('bow_list')

        form = BowForm(data=request.POST, instance=bow)
        if form.is_valid():
            form.save()
            messages.success(request, f"🏹 '{bow.name}' updated successfully!")
            return redirect('bow_list')
        return render(request, self.template_name, {'form': form, 'bow': bow})


class BowDeleteView(LoginRequiredMixin, View):
    """Remove a bow from the member's profile (not from global DB)."""

    def post(self, request, pk):
        bow = get_object_or_404(Bow, pk=pk)
        member_bow = MemberBow.objects.filter(member=request.user, bow=bow).first()
        if member_bow:
            member_bow.delete()
            messages.success(request, f"'{bow.name}' removed from your profile.")
        else:
            messages.error(request, "This bow is not in your profile.")
        return redirect('dashboard')


# ─────────────────────────────────────────────
#  MEMBER VIEWS
# ─────────────────────────────────────────────

class MemberListView(LoginRequiredMixin, View):
    """Browse all club members and their stats."""

    template_name = 'club_app/member_list.html'

    def get(self, request):
        members = ClubMember.objects.filter(is_active=True).prefetch_related('member_bows')

        # Filtering
        experience = request.GET.get('experience', '')
        gender = request.GET.get('gender', '')
        vip_only = request.GET.get('vip', '')

        if experience:
            members = members.filter(experience=experience)
        if gender:
            members = members.filter(gender=gender)
        if vip_only:
            members = members.filter(is_vip=True)

        from .models import ExperienceLevel as EL, Gender as G
        context = {
            'members': members,
            'experience_choices': EL.choices,
            'gender_choices': G.choices,
            'selected_experience': experience,
            'selected_gender': gender,
            'vip_only': vip_only,
        }
        return render(request, self.template_name, context)


class MemberDetailView(LoginRequiredMixin, View):
    """View a specific member's statistics and bows."""

    template_name = 'club_app/member_detail.html'

    def get(self, request, pk):
        member = get_object_or_404(ClubMember, pk=pk, is_active=True)
        member_bows = MemberBow.objects.filter(member=member).select_related('bow')
        context = {
            'profile_member': member,
            'member_bows': member_bows,
        }
        return render(request, self.template_name, context)


# ─────────────────────────────────────────────
#  VIP VIEWS
# ─────────────────────────────────────────────

class VIPSuggestBowView(VIPRequiredMixin, View):
    """
    VIP Feature: Suggest the most fitting bow from the database.
    Uses VIPMember.suggest_bow() scoring algorithm.
    """

    template_name = 'club_app/vip_suggest_bow.html'

    def get(self, request):
        member = request.user
        all_bows = Bow.objects.all()

        # Use VIPMember proxy to access the suggest_bow method
        vip_member = VIPMember.objects.get(pk=member.pk)
        suggested_bow = vip_member.suggest_bow(all_bows)

        context = {
            'member': member,
            'suggested_bow': suggested_bow,
            'member_summary': {
                'height': member.height_cm,
                'arm_length': member.arm_length_cm,
                'strength': member.strength_lbs,
                'experience': member.get_experience_display(),
                'accuracy': member.accuracy_pct,
                'strength_category': member.strength_category,
            }
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """Add the suggested bow to member's profile."""
        bow_id = request.POST.get('bow_id')
        if bow_id:
            bow = get_object_or_404(Bow, pk=bow_id)
            _, created = MemberBow.objects.get_or_create(member=request.user, bow=bow)
            if created:
                messages.success(request, f"🏹 Suggested bow '{bow.name}' added to your profile!")
            else:
                messages.info(request, "You already have this bow in your profile.")
        return redirect('dashboard')


class VIPGenerateBowView(VIPRequiredMixin, View):
    """
    VIP Feature: Generate a 'perfect bow' specification for this member.
    Uses VIPMember.generate_perfect_bow() algorithm.
    """

    template_name = 'club_app/vip_generate_bow.html'

    def get(self, request):
        member = request.user
        vip_member = VIPMember.objects.get(pk=member.pk)
        generated = vip_member.generate_perfect_bow()

        context = {
            'member': member,
            'generated_bow': generated,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """Save the generated bow to the database and add to member's profile."""
        member = request.user
        vip_member = VIPMember.objects.get(pk=member.pk)
        generated = vip_member.generate_perfect_bow()

        # Save generated bow to DB
        bow = Bow.objects.create(
            name=generated['name'],
            bow_type=generated['bow_type'],
            draw_weight_lbs=generated['draw_weight_lbs'],
            length_cm=generated['length_cm'],
            material=generated['material'],
            added_by=member,
            notes=f"[AUTO-GENERATED] {generated['reasoning']}",
        )
        MemberBow.objects.get_or_create(member=member, bow=bow)
        messages.success(request, f"🎯 Perfect bow '{bow.name}' generated and added to your profile!")
        return redirect('dashboard')
