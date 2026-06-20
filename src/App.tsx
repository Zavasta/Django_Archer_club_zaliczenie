import { useState } from 'react'

// ─── Types ────────────────────────────────────────────────────────────────────

type Tab = 'overview' | 'structure' | 'models' | 'api' | 'vip' | 'tests'

interface NavItem {
  id: Tab
  label: string
  icon: string
}

// ─── Data ─────────────────────────────────────────────────────────────────────

const NAV_ITEMS: NavItem[] = [
  { id: 'overview',   label: 'Overview',      icon: '🏹' },
  { id: 'structure',  label: 'Project Structure', icon: '📁' },
  { id: 'models',     label: 'Models & OOP',  icon: '🗄️' },
  { id: 'api',        label: 'REST API',       icon: '📡' },
  { id: 'vip',        label: 'VIP Features',   icon: '⭐' },
  { id: 'tests',      label: 'pytest Tests',   icon: '🧪' },
]

const SCREENS = [
  { icon: '🌐', title: 'Welcome Page',    desc: '/ — Landing page with login & register CTAs' },
  { icon: '🔐', title: 'Login',           desc: '/login/ — Username + password form' },
  { icon: '📝', title: 'Register',        desc: '/register/ — Full member registration with archery attributes' },
  { icon: '🏠', title: 'Dashboard',       desc: '/dashboard/ — Profile overview + my bows + quick stats' },
  { icon: '⚙️', title: 'Edit Profile',    desc: '/profile/edit/ — Update physical & archery attributes' },
  { icon: '🏹', title: 'Browse Bows',     desc: '/bows/ — Database of all bows with filters' },
  { icon: '➕', title: 'Add Bow',         desc: '/bows/add/ — Create and link a bow to your profile' },
  { icon: '✏️', title: 'Edit Bow',        desc: '/bows/<id>/edit/ — Modify your bow\'s attributes' },
  { icon: '👥', title: 'Browse Members',  desc: '/members/ — All club members with stats & filters' },
  { icon: '👤', title: 'Member Detail',   desc: '/members/<id>/ — Individual member\'s stats and bows' },
  { icon: '🎯', title: 'Suggest Bow',     desc: '/vip/suggest-bow/ — ⭐ VIP: Smart bow matching algorithm' },
  { icon: '✨', title: 'Generate Bow',    desc: '/vip/generate-bow/ — ⭐ VIP: AI-generate perfect bow spec' },
]

const API_ENDPOINTS = [
  { method: 'POST', path: '/api/auth/register/', desc: 'Register new member', auth: false },
  { method: 'POST', path: '/api/auth/login/', desc: 'Login', auth: false },
  { method: 'POST', path: '/api/auth/logout/', desc: 'Logout', auth: true },
  { method: 'GET',  path: '/api/members/', desc: 'List all members (filters: ?experience=, ?gender=, ?is_vip=)', auth: true },
  { method: 'GET',  path: '/api/members/<id>/', desc: 'Member detail (includes nested bows)', auth: true },
  { method: 'PUT',  path: '/api/members/<id>/', desc: 'Update member profile', auth: true },
  { method: 'GET',  path: '/api/me/', desc: 'Current user\'s profile', auth: true },
  { method: 'PUT',  path: '/api/me/', desc: 'Update own profile', auth: true },
  { method: 'GET',  path: '/api/bows/', desc: 'List all bows (filters: ?type=, ?material=, ?min_weight=, ?max_weight=)', auth: true },
  { method: 'POST', path: '/api/bows/', desc: 'Create new bow (auto-linked to profile)', auth: true },
  { method: 'GET',  path: '/api/bows/<id>/', desc: 'Bow detail', auth: true },
  { method: 'PUT',  path: '/api/bows/<id>/', desc: 'Update bow (creator only)', auth: true },
  { method: 'DELETE', path: '/api/bows/<id>/', desc: 'Delete bow (creator only)', auth: true },
  { method: 'GET',  path: '/api/my-bows/', desc: 'Current user\'s linked bows', auth: true },
  { method: 'POST', path: '/api/my-bows/', desc: 'Add existing bow to profile', auth: true },
  { method: 'DELETE', path: '/api/my-bows/<bow_id>/', desc: 'Remove bow from profile', auth: true },
  { method: 'GET',  path: '/api/vip/suggest-bow/', desc: '⭐ VIP: Suggest best matching bow', auth: true },
  { method: 'GET',  path: '/api/vip/generate-bow/', desc: '⭐ VIP: Generate perfect bow spec', auth: true },
  { method: 'POST', path: '/api/vip/generate-bow/', desc: '⭐ VIP: Generate + save bow to DB', auth: true },
  { method: 'GET',  path: '/api/stats/', desc: 'Club-wide statistics', auth: true },
]

const METHOD_COLORS: Record<string, string> = {
  GET: 'bg-blue-100 text-blue-700',
  POST: 'bg-green-100 text-green-700',
  PUT: 'bg-amber-100 text-amber-700',
  DELETE: 'bg-red-100 text-red-700',
  PATCH: 'bg-purple-100 text-purple-700',
}

// ─── Components ───────────────────────────────────────────────────────────────

function Badge({ children, color }: { children: React.ReactNode; color: string }) {
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-bold ${color}`}>
      {children}
    </span>
  )
}

function CodeBlock({ code, lang = 'python' }: { code: string; lang?: string }) {
  return (
    <div className="relative">
      <div className="absolute top-2 right-2">
        <Badge color="bg-gray-700 text-gray-300">{lang}</Badge>
      </div>
      <pre className="bg-gray-900 text-gray-100 rounded-xl p-4 overflow-x-auto text-sm leading-relaxed">
        <code>{code}</code>
      </pre>
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-8">
      <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
        <span className="w-1 h-6 bg-amber-500 rounded inline-block" />
        {title}
      </h2>
      {children}
    </div>
  )
}

function Card({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-white border border-gray-200 rounded-xl p-5 shadow-sm ${className}`}>
      {children}
    </div>
  )
}

// ─── Tab Content Components ────────────────────────────────────────────────────

function OverviewTab() {
  return (
    <div className="space-y-8">
      {/* Hero */}
      <div className="bg-gradient-to-br from-gray-900 via-green-900 to-gray-900 rounded-2xl p-8 text-white">
        <div className="flex flex-col md:flex-row md:items-center gap-6">
          <span className="text-7xl">🏹</span>
          <div>
            <h1 className="text-3xl font-extrabold mb-2">Archery Club Management System</h1>
            <p className="text-green-300 text-lg">Django + DRF + pytest · Full-stack archery club application</p>
            <div className="flex flex-wrap gap-2 mt-4">
              {['Django 4.2+', 'DRF', 'SQLite', 'pytest', 'Tailwind CSS', 'OOP'].map(t => (
                <span key={t} className="px-3 py-1 bg-white/10 rounded-full text-sm font-medium">{t}</span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Quick Start */}
      <Section title="🚀 Quick Start">
        <CodeBlock lang="bash" code={`# 1. Create virtual environment
python -m venv venv && source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations + create sample data
python setup_db.py

# 4. Start development server
python manage.py runserver
# → http://127.0.0.1:8000/

# 5. Run tests
pytest tests/ -v`} />
      </Section>

      {/* Pages */}
      <Section title="📱 Application Pages">
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
          {SCREENS.map(s => (
            <Card key={s.title} className="flex items-start gap-3">
              <span className="text-2xl mt-0.5">{s.icon}</span>
              <div>
                <div className="font-bold text-gray-900 text-sm">{s.title}</div>
                <div className="text-xs text-gray-500 mt-0.5">{s.desc}</div>
              </div>
            </Card>
          ))}
        </div>
      </Section>

      {/* Accounts */}
      <Section title="👤 Sample Accounts (after setup_db.py)">
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-left py-2 font-semibold text-gray-600">Username</th>
                  <th className="text-left py-2 font-semibold text-gray-600">Password</th>
                  <th className="text-left py-2 font-semibold text-gray-600">Type</th>
                  <th className="text-left py-2 font-semibold text-gray-600">Experience</th>
                  <th className="text-right py-2 font-semibold text-gray-600">Strength</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {[
                  { u: 'admin',   p: 'admin123', type: 'Admin+VIP', exp: 'Master',   str: '40 lbs', color: 'bg-purple-100 text-purple-700' },
                  { u: 'artemis', p: 'vip123',   type: 'VIP',       exp: 'Advanced', str: '38 lbs', color: 'bg-amber-100 text-amber-700' },
                  { u: 'titan',   p: 'vip123',   type: 'VIP',       exp: 'Master',   str: '48 lbs', color: 'bg-amber-100 text-amber-700' },
                  { u: 'robin',   p: 'pass123',  type: 'Regular',   exp: 'Adept',    str: '28 lbs', color: 'bg-gray-100 text-gray-700' },
                  { u: 'alice',   p: 'pass123',  type: 'Regular',   exp: 'Beginner', str: '20 lbs', color: 'bg-gray-100 text-gray-700' },
                  { u: 'thorin',  p: 'pass123',  type: 'Regular',   exp: 'Advanced', str: '35 lbs', color: 'bg-gray-100 text-gray-700' },
                ].map(r => (
                  <tr key={r.u}>
                    <td className="py-2 font-mono font-bold text-gray-900">{r.u}</td>
                    <td className="py-2 font-mono text-gray-600">{r.p}</td>
                    <td className="py-2"><Badge color={r.color}>{r.type}</Badge></td>
                    <td className="py-2 text-gray-600">{r.exp}</td>
                    <td className="py-2 text-right text-gray-600">{r.str}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </Section>
    </div>
  )
}

function StructureTab() {
  return (
    <div className="space-y-8">
      <Section title="📁 Directory Structure">
        <CodeBlock lang="text" code={`archery_club/
├── manage.py                    ← CLI: python manage.py runserver
├── mojprojekt/
│   ├── __init__.py
│   ├── settings.py              ← INSTALLED_APPS, DB, DRF config
│   ├── urls.py                  ← Main URL routing (HTML + /api/)
│   └── wsgi.py                  ← Production WSGI entry point
├── club_app/
│   ├── __init__.py
│   ├── models.py                ← ClubMember, Bow, MemberBow, VIPMember
│   ├── views.py                 ← Class-based HTML views (12 views)
│   ├── api_views.py             ← DRF APIView classes (9 views + 1 fn)
│   ├── api_urls.py              ← /api/ URL conf (20 endpoints)
│   ├── serializers.py           ← DRF serializers (8 serializers)
│   ├── forms.py                 ← Django forms (5 forms)
│   └── admin.py                 ← Django admin customization
├── templates/
│   ├── base.html                ← Shared nav + messages + footer
│   └── club_app/
│       ├── welcome.html         ← Landing page
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html       ← Main hub
│       ├── profile_edit.html
│       ├── bow_list.html        ← With filters
│       ├── bow_add.html
│       ├── bow_edit.html
│       ├── member_list.html     ← With filters
│       ├── member_detail.html
│       ├── vip_suggest_bow.html ← VIP feature
│       └── vip_generate_bow.html← VIP feature
├── tests/
│   ├── conftest.py              ← @pytest.fixture definitions
│   └── test_api.py              ← 40+ test cases
├── setup_db.py                  ← Migrations + sample data script
├── requirements.txt
└── pytest.ini`} />
      </Section>

      <Section title="⚙️ manage.py Commands">
        <CodeBlock lang="bash" code={`# Start development server
python manage.py runserver

# Create new app module
python manage.py startapp new_feature_app

# Database migrations
python manage.py makemigrations club_app
python manage.py migrate

# Check configuration
python manage.py check

# Create superuser
python manage.py createsuperuser

# Open Django shell
python manage.py shell

# Collect static files (production)
python manage.py collectstatic`} />
      </Section>

      <Section title="⚙️ INSTALLED_APPS (settings.py)">
        <CodeBlock lang="python" code={`INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',          # Django REST Framework
    'rest_framework.authtoken', # Token auth
    'corsheaders',             # CORS for development
    'club_app',                # ← Our archery club app
]

# Custom user model
AUTH_USER_MODEL = 'club_app.ClubMember'`} />
      </Section>
    </div>
  )
}

function ModelsTab() {
  return (
    <div className="space-y-8">
      {/* Class Hierarchy */}
      <Section title="🗄️ Model Class Hierarchy">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <h3 className="font-bold text-gray-800 mb-3">User Models</h3>
            <div className="font-mono text-sm space-y-1">
              <div className="text-gray-500">AbstractBaseUser (Django)</div>
              <div className="pl-4 text-green-700">└── ClubMember</div>
              <div className="pl-8 text-amber-700">└── VIPMember (proxy)</div>
            </div>
            <div className="mt-3 text-xs text-gray-500">Custom manager: ClubMemberManager</div>
          </Card>
          <Card>
            <h3 className="font-bold text-gray-800 mb-3">Data Models</h3>
            <div className="font-mono text-sm space-y-1">
              <div className="text-blue-700">Bow</div>
              <div className="text-blue-700">MemberBow</div>
              <div className="pl-4 text-gray-500">ForeignKey → ClubMember</div>
              <div className="pl-4 text-gray-500">ForeignKey → Bow</div>
            </div>
            <div className="mt-3 text-xs text-gray-500">unique_together: (member, bow)</div>
          </Card>
        </div>
      </Section>

      {/* ClubMember */}
      <Section title="👤 ClubMember Model">
        <CodeBlock code={`class ClubMember(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model with archery-specific attributes.
    AUTH_USER_MODEL = 'club_app.ClubMember'
    """

    # ── Identity ──────────────────────────────
    username       = CharField(max_length=50, unique=True)
    email          = EmailField(unique=True)
    first_name     = CharField(max_length=50, blank=True)
    last_name      = CharField(max_length=50, blank=True)

    # ── Physical Attributes ───────────────────
    gender         = CharField(choices=Gender.choices)        # M/F/O
    height_cm      = PositiveIntegerField(100–250)            # in cm
    arm_length_cm  = PositiveIntegerField(40–120)             # draw length

    # ── Archery Attributes ────────────────────
    strength_lbs   = PositiveIntegerField(10–100)             # comfortable draw weight
    age            = PositiveIntegerField(5–100)
    experience     = CharField(choices=ExperienceLevel)       # beginner/adept/advanced/master
    accuracy_pct   = FloatField(0–100)                        # % shots at centre

    # ── Flags ─────────────────────────────────
    is_vip         = BooleanField(default=False)
    is_staff       = BooleanField(default=False)
    is_active      = BooleanField(default=True)
    date_joined    = DateTimeField(default=timezone.now)

    # ── Computed Properties ───────────────────
    @property
    def strength_category(self):  # 'light' / 'medium' / 'heavy'
        if self.strength_lbs < 25:  return 'light'
        elif self.strength_lbs < 35: return 'medium'
        else:                        return 'heavy'

    @property
    def bow_count(self):           # number of linked bows
        return self.member_bows.count()

    @property
    def can_add_bow(self):         # VIP = unlimited, Regular = max 3
        return True if self.is_vip else self.bow_count < 3

    USERNAME_FIELD = 'username'
    objects = ClubMemberManager()`} />
      </Section>

      {/* VIPMember */}
      <Section title="⭐ VIPMember (Proxy Model)">
        <CodeBlock code={`class VIPMember(ClubMember):
    """
    Proxy model — same DB table as ClubMember.
    Adds VIP-exclusive business logic methods.
    """

    objects = VIPMemberManager()  # returns only is_vip=True

    class Meta:
        proxy = True              # No extra DB table

    def suggest_bow(self, bows_queryset):
        """
        Score every bow and return the best match.

        Scoring (total 100 pts):
          40 pts – draw weight match
          30 pts – bow length vs member height
          20 pts – experience compatibility
          10 pts – short+strong special bonus
        """
        def score_bow(bow):
            score = 0
            score += max(0, 40 - abs(bow.draw_weight_lbs - self.strength_lbs))
            ideal_length = self.height_cm / 3
            score += max(0, 30 - abs(bow.length_cm - ideal_length) / 2)
            score += experience_scores[self.experience][bow.bow_type]
            if self.height_cm < 165 and self.strength_lbs >= 35:
                if bow.length_cm < 150 and bow.draw_weight_lbs >= 35:
                    score += 10
            return score

        return max(bows_queryset, key=score_bow)

    def generate_perfect_bow(self):
        """
        Generate ideal bow specification for this member.
        Returns a dict with bow attributes (not saved to DB).
        """
        accuracy_bonus = (self.accuracy_pct - 50) / 100 * 5
        ideal_weight = max(15, min(80, round(self.strength_lbs + accuracy_bonus)))
        ideal_length = max(100, min(220, round(self.height_cm * 0.95 + arm_factor)))
        bow_type = ...  # based on experience + height + strength
        material = ...  # beginner=wood, advanced=composite, master=carbon
        return { 'name': ..., 'bow_type': ..., 'draw_weight_lbs': ..., ... }`} />
      </Section>

      {/* Bow */}
      <Section title="🏹 Bow Model">
        <CodeBlock code={`class Bow(models.Model):
    name            = CharField(max_length=100)
    bow_type        = CharField(choices=BowType)  # longbow/shortbow/recurve/compound/crossbow
    draw_weight_lbs = PositiveIntegerField(5–100) # tension in pounds
    length_cm       = PositiveIntegerField(50–250)# bow length in cm
    material        = CharField(choices=BowMaterial) # wood/composite/carbon/fiberglass/hybrid
    added_by        = ForeignKey(ClubMember, on_delete=SET_NULL)
    date_added      = DateTimeField(auto)
    notes           = TextField(blank=True)

    @property
    def strength_category(self):  # 'light' / 'medium' / 'heavy'
    @property
    def size_category(self):      # 'short' / 'medium' / 'long'


class MemberBow(models.Model):
    """Many-to-many link: ClubMember ↔ Bow with extra info."""
    member     = ForeignKey(ClubMember, related_name='member_bows')
    bow        = ForeignKey(Bow, related_name='bow_members')
    is_primary = BooleanField(default=False)   # favourite bow marker
    date_added = DateTimeField(auto)

    class Meta:
        unique_together = [('member', 'bow')]  # one bow per member once

    def save(self, *args, **kwargs):
        if not self.pk and not self.member.can_add_bow:
            raise ValueError("Regular members: max 3 bows!")
        super().save(*args, **kwargs)`} />
      </Section>

      {/* Choices */}
      <Section title="📋 Enum Choices">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Card>
            <h3 className="font-bold text-gray-700 mb-3">ExperienceLevel</h3>
            <div className="space-y-2">
              {[
                { val: 'beginner', label: 'Beginner', color: 'bg-green-100 text-green-700' },
                { val: 'adept',    label: 'Adept',    color: 'bg-blue-100 text-blue-700' },
                { val: 'advanced', label: 'Advanced', color: 'bg-amber-100 text-amber-700' },
                { val: 'master',   label: 'Master',   color: 'bg-pink-100 text-pink-700' },
              ].map(e => (
                <div key={e.val} className="flex items-center gap-3">
                  <Badge color={e.color}>{e.label}</Badge>
                  <span className="font-mono text-xs text-gray-500">'{e.val}'</span>
                </div>
              ))}
            </div>
          </Card>
          <Card>
            <h3 className="font-bold text-gray-700 mb-3">BowType</h3>
            <div className="space-y-2 text-sm">
              {['longbow', 'shortbow', 'recurve', 'compound', 'crossbow'].map(t => (
                <div key={t} className="font-mono text-gray-700">{t}</div>
              ))}
            </div>
          </Card>
          <Card>
            <h3 className="font-bold text-gray-700 mb-3">BowMaterial</h3>
            <div className="space-y-2 text-sm">
              {['wood', 'composite', 'carbon', 'fiberglass', 'hybrid'].map(m => (
                <div key={m} className="font-mono text-gray-700">{m}</div>
              ))}
            </div>
          </Card>
          <Card>
            <h3 className="font-bold text-gray-700 mb-3">Strength Guide</h3>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-blue-400" />
                <span className="text-sm">Light: &lt;25 lbs</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-amber-400" />
                <span className="text-sm">Medium: 25–34 lbs</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-red-500" />
                <span className="text-sm">Heavy: 35+ lbs</span>
              </div>
            </div>
          </Card>
        </div>
      </Section>
    </div>
  )
}

function ApiTab() {
  return (
    <div className="space-y-8">
      <Section title="📡 REST API Endpoints">
        <div className="space-y-2">
          {API_ENDPOINTS.map((ep, i) => (
            <div key={i} className="flex items-start gap-3 p-3 bg-white border border-gray-200 rounded-lg hover:border-amber-200 transition-colors">
              <Badge color={METHOD_COLORS[ep.method] || 'bg-gray-100 text-gray-700'}>
                {ep.method}
              </Badge>
              <code className="text-sm font-mono text-gray-900 flex-shrink-0">{ep.path}</code>
              <span className="text-sm text-gray-500 flex-1">{ep.desc}</span>
              {!ep.auth && <Badge color="bg-orange-100 text-orange-700">Public</Badge>}
            </div>
          ))}
        </div>
      </Section>

      <Section title="🔧 DRF Setup">
        <CodeBlock code={`# requirements.txt
djangorestframework>=3.15.0
django-cors-headers>=4.3.0

# settings.py
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}`} />
      </Section>

      <Section title="📦 Serializers">
        <CodeBlock code={`# 8 serializers in serializers.py

ClubMemberSerializer        # Read-only, includes nested bows + computed fields
ClubMemberUpdateSerializer  # Update physical/archery attributes
RegisterSerializer          # Create member (validates password match)
LoginSerializer             # Authenticate with username+password
BowSerializer               # Full bow representation
BowCreateSerializer         # Create/update bow (validates bow limit)
MemberBowSerializer         # Member ↔ Bow link
VIPSuggestBowResponseSerializer   # VIP suggest response
VIPGenerateBowResponseSerializer  # VIP generate response

# Example – BowCreateSerializer validates bow limit:
def validate(self, attrs):
    user = self.context['request'].user
    if not self.instance and not user.can_add_bow:
        raise serializers.ValidationError(
            "Regular members can only add up to 3 bows!"
        )
    return attrs`} />
      </Section>

      <Section title="🌐 cURL Examples">
        <CodeBlock lang="bash" code={`# Register
curl -X POST http://localhost:8000/api/auth/register/ \\
  -H "Content-Type: application/json" \\
  -d '{"username":"archer","email":"a@club.com","password":"pass123",
       "password_confirm":"pass123","height_cm":175,"arm_length_cm":65,
       "strength_lbs":30,"age":25,"experience":"adept","accuracy_pct":60.0}'

# Login (save session cookie)
curl -X POST http://localhost:8000/api/auth/login/ \\
  -H "Content-Type: application/json" \\
  -c cookies.txt \\
  -d '{"username":"archer","password":"pass123"}'

# List bows
curl http://localhost:8000/api/bows/ -b cookies.txt

# Create bow
curl -X POST http://localhost:8000/api/bows/ \\
  -H "Content-Type: application/json" -b cookies.txt \\
  -d '{"name":"My Recurve","bow_type":"recurve","draw_weight_lbs":32,
       "length_cm":160,"material":"composite"}'

# Filter bows
curl "http://localhost:8000/api/bows/?type=longbow&min_weight=25" -b cookies.txt

# My bows
curl http://localhost:8000/api/my-bows/ -b cookies.txt

# Stats
curl http://localhost:8000/api/stats/ -b cookies.txt

# VIP: suggest a bow
curl http://localhost:8000/api/vip/suggest-bow/ -b cookies.txt

# VIP: generate + save bow
curl -X POST http://localhost:8000/api/vip/generate-bow/ \\
  -H "Content-Type: application/json" -b cookies.txt -d '{}'`} />
      </Section>
    </div>
  )
}

function VIPTab() {
  return (
    <div className="space-y-8">
      <div className="bg-gradient-to-r from-purple-900 to-indigo-900 rounded-2xl p-6 text-white">
        <div className="flex items-center gap-3">
          <span className="text-4xl">⭐</span>
          <div>
            <h2 className="text-2xl font-bold">VIP Features</h2>
            <p className="text-purple-300">Exclusive to is_vip=True members</p>
          </div>
        </div>
      </div>

      <Section title="⭐ VIP Privileges Overview">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { icon: '♾️', title: 'Unlimited Bows', desc: 'Regular = max 3. VIP = no limit on linked bows.' },
            { icon: '🎯', title: 'Suggest Me a Bow', desc: 'Algorithm picks the best bow from DB for your profile.' },
            { icon: '✨', title: 'Generate Perfect Bow', desc: 'AI generates and saves a custom bow spec to the database.' },
          ].map(f => (
            <Card key={f.title} className="text-center">
              <div className="text-4xl mb-3">{f.icon}</div>
              <div className="font-bold text-gray-900 mb-1">{f.title}</div>
              <div className="text-sm text-gray-500">{f.desc}</div>
            </Card>
          ))}
        </div>
      </Section>

      <Section title="🎯 Suggest Bow Algorithm">
        <CodeBlock code={`def suggest_bow(self, bows_queryset):
    """Score every bow in DB and return the best match."""

    def score_bow(bow):
        score = 0

        # 1. Strength match (40 points) — most important
        strength_diff = abs(bow.draw_weight_lbs - self.strength_lbs)
        score += max(0, 40 - strength_diff)

        # 2. Bow length vs height (30 points)
        # Ideal length heuristic: height / 3
        ideal_length = self.height_cm / 3
        length_diff = abs(bow.length_cm - ideal_length)
        score += max(0, 30 - length_diff / 2)

        # 3. Experience compatibility (20 points)
        experience_scores = {
            'beginner': {'longbow': 15, 'shortbow': 20, 'recurve': 10,
                         'compound': 0, 'crossbow': 5},
            'adept':    {'longbow': 18, 'shortbow': 18, 'recurve': 20,
                         'compound': 10, 'crossbow': 12},
            'advanced': {'longbow': 15, 'shortbow': 15, 'recurve': 20,
                         'compound': 20, 'crossbow': 15},
            'master':   {'longbow': 20, 'shortbow': 15, 'recurve': 20,
                         'compound': 20, 'crossbow': 15},
        }
        score += experience_scores[self.experience].get(bow.bow_type, 10)

        # 4. Special case: short but strong archer bonus (10 points)
        if self.height_cm < 165 and self.strength_lbs >= 35:
            if bow.length_cm < 150 and bow.draw_weight_lbs >= 35:
                score += 10   # short+strong bow for short+strong archer

        return score

    return max(bows_queryset, key=score_bow)`} />
      </Section>

      <Section title="✨ Generate Perfect Bow Algorithm">
        <CodeBlock code={`def generate_perfect_bow(self):
    """Generate ideal bow spec from member's profile attributes."""

    # ── Draw Weight ───────────────────────────────────────────────
    # High accuracy → can handle slightly more weight (±2.5 lbs)
    accuracy_bonus = (self.accuracy_pct - 50) / 100 * 5
    ideal_weight = round(self.strength_lbs + accuracy_bonus)
    ideal_weight = max(15, min(80, ideal_weight))

    # ── Bow Length ────────────────────────────────────────────────
    # height × 0.95 + arm length deviation from average (60cm)
    arm_factor = (self.arm_length_cm - 60) * 0.5
    ideal_length = round(self.height_cm * 0.95 + arm_factor)
    ideal_length = max(100, min(220, ideal_length))

    # ── Bow Type ─────────────────────────────────────────────────
    # beginner  → longbow (tall) or shortbow (short)
    # adept     → recurve
    # advanced  → compound (if strength_lbs >= 40) or recurve
    # master    → longbow (if accuracy >= 70) or compound
    bow_type = ...

    # ── Material ─────────────────────────────────────────────────
    # beginner/adept → wood
    # advanced       → composite
    # master+acc≥75  → carbon
    # master+acc<75  → hybrid
    material = ...

    return {
        'name':           f"Perfect {exp} {type} ({strength_label})",
        'bow_type':        bow_type,
        'draw_weight_lbs': ideal_weight,
        'length_cm':       ideal_length,
        'material':        material,
        'generated_for':   self.username,
        'reasoning':       f"height={height}cm, arm={arm}cm, strength={strength}lbs ...",
    }`} />
      </Section>

      <Section title="🔒 Access Control">
        <CodeBlock code={`# views.py — VIPRequiredMixin
class VIPRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_vip:
            messages.error(request, "🏹 VIP members only!")
            return redirect('dashboard')     # Redirect regular users
        return super().dispatch(request, *args, **kwargs)

# api_views.py — API VIP check
class APIVIPSuggestBowView(APIView):
    def get(self, request):
        if not request.user.is_vip:
            return Response(
                {'error': 'VIP members only.'},
                status=status.HTTP_403_FORBIDDEN
            )`} />
      </Section>
    </div>
  )
}

function TestsTab() {
  return (
    <div className="space-y-8">
      <Section title="🧪 Test Overview">
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          {[
            { count: '40+', label: 'Test Cases', color: 'text-blue-600' },
            { count: '8',   label: 'Test Classes', color: 'text-green-600' },
            { count: '7',   label: 'pytest Fixtures', color: 'text-purple-600' },
            { count: '100%', label: 'API Coverage', color: 'text-amber-600' },
            { count: 'ORM',  label: 'Isolated (DB)', color: 'text-red-600' },
            { count: 'DRF',  label: 'APIClient', color: 'text-indigo-600' },
          ].map(s => (
            <Card key={s.label} className="text-center">
              <div className={`text-2xl font-extrabold ${s.color}`}>{s.count}</div>
              <div className="text-sm text-gray-500 mt-1">{s.label}</div>
            </Card>
          ))}
        </div>
      </Section>

      <Section title="🔧 Running Tests">
        <CodeBlock lang="bash" code={`# Run all tests
pytest tests/ -v

# Run specific class
pytest tests/test_api.py::TestBowAPI -v
pytest tests/test_api.py::TestVIPAPI -v
pytest tests/test_api.py::TestBowLimits -v
pytest tests/test_api.py::TestModels -v

# Run by keyword
pytest tests/ -v -k "test_vip"
pytest tests/ -v -k "test_bow_limit"
pytest tests/ -v -k "test_auth"

# With coverage
pytest tests/ -v --cov=club_app --cov-report=term-missing

# Short output
pytest tests/ --tb=short -q`} />
      </Section>

      <Section title="🔧 conftest.py – @pytest.fixture">
        <CodeBlock code={`# tests/conftest.py

@pytest.fixture
def api_client():
    """Return an unauthenticated DRF APIClient."""
    return APIClient()

@pytest.fixture
def regular_member(db):
    """Create and return a regular (non-VIP) club member."""
    return ClubMember.objects.create_user(
        username='regular_archer', email='regular@archery.club',
        password='testpass123', gender='M', height_cm=175,
        arm_length_cm=65, strength_lbs=28, age=25,
        experience='adept', accuracy_pct=62.5, is_vip=False,
    )

@pytest.fixture
def vip_member(db):
    """Create and return a VIP club member."""
    ...

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
def sample_bows(db, regular_member):
    """Create 5 sample bows for testing."""
    return [Bow.objects.create(...) for _ in range(5)]`} />
      </Section>

      <Section title="📋 Test Classes">
        <div className="space-y-3">
          {[
            {
              name: 'TestAuthAPI',
              tests: ['register success → 201', 'password mismatch → 400', 'duplicate username → 400',
                      'login valid → 200', 'login wrong pw → 400', 'login nonexistent → 400'],
            },
            {
              name: 'TestMemberAPI',
              tests: ['list requires auth', 'list returns count+results', 'GET /me/ own profile',
                      'PUT /me/ updates attrs', 'update other → 403', 'filter by experience/gender/VIP',
                      'detail includes bows', 'strength_category in response'],
            },
            {
              name: 'TestBowAPI',
              tests: ['list authenticated', 'list unauthenticated → 403', 'create success → 201',
                      'create missing field → 400', 'get detail', 'update own bow', 'update other → 403',
                      'delete own bow → 204', 'delete other → 403', 'filter by type/weight',
                      'computed fields present', 'nonexistent → 404'],
            },
            {
              name: 'TestMyBowsAPI',
              tests: ['empty list', 'add bow to profile → 201', 'duplicate → 200', 'remove bow → 204', 'VIP has no limit'],
            },
            {
              name: 'TestBowLimits',
              tests: ['regular limited to 3 bows', 'VIP unlimited (5 bows)', 'bow_count property', 'can_add_bow True/False'],
            },
            {
              name: 'TestVIPAPI',
              tests: ['suggest bow VIP → 200', 'suggest denied regular → 403', 'suggest empty DB',
                      'generate bow → 200', 'generate denied → 403', 'POST generate saves to DB',
                      'beginner not compound', 'high strength → heavier suggestion'],
            },
            {
              name: 'TestStatsAPI',
              tests: ['stats structure 200', 'counts correct', 'unauthenticated → 403'],
            },
            {
              name: 'TestModels',
              tests: ['bow strength_category', 'bow size_category', 'member strength_category',
                      'VIPMember.suggest_bow()', 'VIPMember.generate_perfect_bow()', '__str__', 'get_full_name', 'MemberBow.__str__'],
            },
          ].map(tc => (
            <Card key={tc.name}>
              <h3 className="font-bold text-gray-800 mb-2 font-mono">{tc.name}</h3>
              <div className="flex flex-wrap gap-1.5">
                {tc.tests.map(t => (
                  <span key={t} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">{t}</span>
                ))}
              </div>
            </Card>
          ))}
        </div>
      </Section>

      <Section title="💡 Example Test">
        <CodeBlock code={`@pytest.mark.django_db
class TestBowLimits:
    """Tests for the 3-bow limit on regular members."""

    def test_regular_member_limited_to_3_bows(self, auth_client, regular_member):
        """Regular members cannot add more than 3 bows via API."""
        # Create 3 bows and link them
        for i in range(3):
            bow = Bow.objects.create(
                name=f'Bow {i}', bow_type='recurve',
                draw_weight_lbs=25, length_cm=150,
                material='wood', added_by=regular_member,
            )
            MemberBow.objects.create(member=regular_member, bow=bow)

        # 4th bow should be rejected
        data = {
            'name': 'One Too Many', 'bow_type': 'longbow',
            'draw_weight_lbs': 30, 'length_cm': 170, 'material': 'wood',
        }
        response = auth_client.post('/api/bows/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_vip_member_unlimited_bows(self, vip_client, vip_member):
        """VIP members can create more than 3 bows."""
        for i in range(5):
            data = {'name': f'VIP Bow {i}', 'bow_type': 'recurve',
                    'draw_weight_lbs': 35, 'length_cm': 160, 'material': 'composite'}
            response = vip_client.post('/api/bows/', data, format='json')
            assert response.status_code == status.HTTP_201_CREATED`} />
      </Section>
    </div>
  )
}

// ─── Main App ─────────────────────────────────────────────────────────────────

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>('overview')

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':  return <OverviewTab />
      case 'structure': return <StructureTab />
      case 'models':    return <ModelsTab />
      case 'api':       return <ApiTab />
      case 'vip':       return <VIPTab />
      case 'tests':     return <TestsTab />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Nav */}
      <nav className="bg-gray-900 text-white shadow-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center gap-4 h-14">
            <span className="text-xl font-bold whitespace-nowrap">🏹 Archery Club</span>
            <span className="text-gray-600 text-sm hidden sm:block">Django Application</span>
            <div className="flex-1 flex items-center gap-1 overflow-x-auto">
              {NAV_ITEMS.map(item => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
                    activeTab === item.id
                      ? 'bg-amber-500 text-white'
                      : 'text-gray-300 hover:text-white hover:bg-white/10'
                  }`}
                >
                  {item.icon} {item.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {renderContent()}
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-sm text-gray-500">
          <p className="font-semibold text-gray-700 mb-1">🏹 Archery Club Management System</p>
          <p>Django + DRF + pytest · All files in <code className="bg-gray-100 px-1 rounded">archery_club/</code></p>
          <p className="mt-1 text-xs">
            Run: <code className="bg-gray-100 px-1 rounded">cd archery_club && python setup_db.py && python manage.py runserver</code>
          </p>
        </div>
      </footer>
    </div>
  )
}
