
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import ClubMember, Bow, MemberBow, Gender, ExperienceLevel, BowType, BowMaterial


# ─────────────────────────────────────────────
#  AUTHENTICATION FORMS
# ─────────────────────────────────────────────

class LoginForm(forms.Form):
    """Simple login form."""

    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Enter your username',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        })
    )


class RegisterForm(forms.ModelForm):
    """Registration form for new club members."""

    password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'At least 6 characters',
        }),
        help_text='Minimum 6 characters.'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Repeat your password',
        }),
        label='Confirm Password'
    )

    class Meta:
        model = ClubMember
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'gender', 'height_cm', 'arm_length_cm', 'strength_lbs',
            'age', 'experience', 'accuracy_pct',
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Unique username'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'your@email.com'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'gender': forms.Select(attrs={'class': 'form-input'}),
            'height_cm': forms.NumberInput(attrs={'class': 'form-input', 'min': 100, 'max': 250}),
            'arm_length_cm': forms.NumberInput(attrs={'class': 'form-input', 'min': 40, 'max': 120}),
            'strength_lbs': forms.NumberInput(attrs={'class': 'form-input', 'min': 10, 'max': 100}),
            'age': forms.NumberInput(attrs={'class': 'form-input', 'min': 5, 'max': 100}),
            'experience': forms.Select(attrs={'class': 'form-input'}),
            'accuracy_pct': forms.NumberInput(attrs={'class': 'form-input', 'min': 0, 'max': 100, 'step': 0.1}),
        }
        help_texts = {
            'strength_lbs': '20 lbs = light/weak, 40+ lbs = heavy/strong',
            'accuracy_pct': '% of shots hitting the centre of the target (0-100)',
            'arm_length_cm': 'Your draw length / arm length in centimeters',
        }

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        password_confirm = cleaned.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match.")
        return cleaned


# ─────────────────────────────────────────────
#  PROFILE FORM
# ─────────────────────────────────────────────

class ProfileEditForm(forms.ModelForm):
    """Form to edit a member's archery attributes."""

    class Meta:
        model = ClubMember
        fields = [
            'first_name', 'last_name', 'email',
            'gender', 'height_cm', 'arm_length_cm', 'strength_lbs',
            'age', 'experience', 'accuracy_pct',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'gender': forms.Select(attrs={'class': 'form-input'}),
            'height_cm': forms.NumberInput(attrs={'class': 'form-input', 'min': 100, 'max': 250}),
            'arm_length_cm': forms.NumberInput(attrs={'class': 'form-input', 'min': 40, 'max': 120}),
            'strength_lbs': forms.NumberInput(attrs={'class': 'form-input', 'min': 10, 'max': 100}),
            'age': forms.NumberInput(attrs={'class': 'form-input', 'min': 5, 'max': 100}),
            'experience': forms.Select(attrs={'class': 'form-input'}),
            'accuracy_pct': forms.NumberInput(attrs={'class': 'form-input', 'min': 0, 'max': 100, 'step': 0.1}),
        }
        help_texts = {
            'strength_lbs': '20 lbs = light/weak, 40+ lbs = heavy/strong',
            'accuracy_pct': '% of shots hitting the centre of the target',
        }


# ─────────────────────────────────────────────
#  BOW FORMS
# ─────────────────────────────────────────────

class BowForm(forms.ModelForm):
    """Form to add or edit a bow."""

    class Meta:
        model = Bow
        fields = ['name', 'bow_type', 'draw_weight_lbs', 'length_cm', 'material', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. "Forest Hunter", "Black Shadow"',
            }),
            'bow_type': forms.Select(attrs={'class': 'form-input'}),
            'draw_weight_lbs': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 5,
                'max': 100,
                'placeholder': '20-80 lbs',
            }),
            'length_cm': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 50,
                'max': 250,
                'placeholder': '100-220 cm',
            }),
            'material': forms.Select(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Optional notes about this bow...',
            }),
        }
        help_texts = {
            'draw_weight_lbs': 'Draw weight (tension) in pounds (5-100 lbs)',
            'length_cm': 'Full bow length in centimeters',
        }


class MemberBowLinkForm(forms.ModelForm):
    """Form to link a bow to a member's profile."""

    class Meta:
        model = MemberBow
        fields = ['bow', 'is_primary']
        widgets = {
            'bow': forms.Select(attrs={'class': 'form-input'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
