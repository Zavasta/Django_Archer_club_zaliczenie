# Archery Club Management System

---
## Sample account:

Username	| Password	| Type | Experience |	Strength
|-----|-----|-----|-----|-----|
| 'admin'	| 'admin123' |	'Admin+VIP' |	'Master' |	40 lbs |
| 'artemis' |	vip123 |	VIP	Advanced |	38 lbs |
| 'titan' |	vip123 |	VIP	Master |	48 lbs |
| 'robin' |	pass123	| Regular |	Adept	| 28 lbs |
| 'alice' |	pass123 |	Regular |	Beginner	| 20 lbs |
| 'thorin' | pass123 |	Regular |	Advanced |	35 lbs |


---
## Project Structure

```
mojprojekt/
├── manage.py                    
├── mojprojekt/
│   ├── __init__.py
│   ├── settings.py              
│   ├── urls.py                  
│   └── wsgi.py                  
├── club_app/
│   ├── __init__.py
│   ├── models.py                
│   ├── views.py                 
│   ├── api_views.py             
│   ├── api_urls.py              
│   ├── serializers.py           
│   ├── forms.py                 
│   └── admin.py                 
├── templates/
│   ├── base.html                
│   └── club_app/
│       ├── welcome.html         
│       ├── login.html           
│       ├── register.html        
│       ├── dashboard.html       
│       ├── profile_edit.html    
│       ├── bow_list.html        
│       ├── bow_add.html         
│       ├── bow_edit.html        
│       ├── member_list.html     
│       ├── member_detail.html   
│       ├── vip_suggest_bow.html 
│       └── vip_generate_bow.html
├── tests/
│   ├── conftest.py              
│   └── test_api.py              
├── requirements.txt
├── pytest.ini
└── README.md
```

---

### Quick Start

```bash
python -m venv venv
venv\Scripts\activate     #Na windows   
```

```bash
pip install -r requirements.txt
```

```bash
python manage.py makemigrations club_app
python manage.py migrate
```

```bash
python manage.py createsuperuser
```

### sample data

```bash
python manage.py shell
# In the shell, run:
from club_app.models import ClubMember, Bow, MemberBow
# Create a VIP member
vip = ClubMember.objects.create_user('vip_user', 'vip@club.com', 'pass123', is_vip=True, height_cm=170, arm_length_cm=65, strength_lbs=35, age=28, experience='advanced', accuracy_pct=75.0)
# Create sample bows
Bow.objects.create(name='Forest Hunter', bow_type='longbow', draw_weight_lbs=28, length_cm=180, material='wood', added_by=vip)
```

### Run

```bash
python manage.py runserver
# → http://127.0.0.1:8000/
```

---

## URL Map

| URL | Description |
|-----|-------------|
| `/` | Welcome / landing page |
| `/login/` | Login form |
| `/register/` | New member registration |
| `/dashboard/` | Member dashboard |
| `/profile/edit/` | Edit member attributes |
| `/bows/` | Browse all bows |
| `/bows/add/` | Add a new bow |
| `/bows/<id>/edit/` | Edit a bow |
| `/members/` | Browse all members |
| `/members/<id>/` | Member detail |
| `/vip/suggest-bow/` | ⭐ VIP: suggest a bow |
| `/vip/generate-bow/` | ⭐ VIP: generate perfect bow |
| `/admin/` | Django admin panel |
| `/api/` | REST API root |

---

## REST API

### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register/` | Register new member |
| `POST` | `/api/auth/login/` | Login |
| `POST` | `/api/auth/logout/` | Logout |

### Members

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/members/` | List all members |
| `GET` | `/api/members/<id>/` | Member detail |
| `PUT` | `/api/members/<id>/` | Update member |
| `GET` | `/api/me/` | Current user's profile |
| `PUT` | `/api/me/` | Update own profile |

**Query filters:** `?experience=beginner`, `?gender=M`, `?is_vip=true`

### Bows

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/bows/` | List all bows |
| `POST` | `/api/bows/` | Create new bow |
| `GET` | `/api/bows/<id>/` | Bow detail |
| `PUT` | `/api/bows/<id>/` | Update bow |
| `DELETE` | `/api/bows/<id>/` | Delete bow |
| `GET` | `/api/my-bows/` | My linked bows |
| `POST` | `/api/my-bows/` | Link bow to profile |
| `DELETE` | `/api/my-bows/<bow_id>/` | Unlink bow from profile |

**Query filters:** `?type=longbow`, `?material=wood`, `?min_weight=25`, `?max_weight=40`

### VIP Features

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/vip/suggest-bow/` | Suggest best matching bow |
| `GET` | `/api/vip/generate-bow/` | Generate perfect bow spec |
| `POST` | `/api/vip/generate-bow/` | Generate + save bow to DB |

### Stats

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/stats/` | Club-wide statistics |

---

## Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test class
pytest tests/test_api.py::TestBowAPI -v
pytest tests/test_api.py::TestVIPAPI -v
pytest tests/test_api.py::TestBowLimits -v

# Run with coverage
pytest tests/ -v --cov=club_app --cov-report=term-missing

# Run a specific test by keyword
pytest tests/ -v -k "test_vip"
pytest tests/ -v -k "test_bow_limit"
```

---

## Member Attributes

| Attribute | Description | Range |
|-----------|-------------|-------|
| `gender` | M / F / Other | — |
| `height_cm` | Height in centimeters | 100–250 |
| `arm_length_cm` | Arm/draw length in cm | 40–120 |
| `strength_lbs` | Comfortable draw weight | 10–100 (20=light, 40+=heavy) |
| `age` | Age in years | 5–100 |
| `experience` | beginner / adept / advanced / master | — |
| `accuracy_pct` | % shots hitting centre | 0–100 |
| `is_vip` | VIP status | True/False |

## Bow Attributes

| Attribute | Description | Range |
|-----------|-------------|-------|
| `bow_type` | longbow / shortbow / recurve / compound / crossbow | — |
| `draw_weight_lbs` | Tension in pounds | 5–100 |
| `length_cm` | Bow length in centimeters | 50–250 |
| `material` | wood / composite / carbon / fiberglass / hybrid | — |

---

## VIP Features

### Suggest Me a Bow
Scores every bow in the database:
- **Draw weight match** (40 pts): lower difference = higher score
- **Length vs height** (30 pts): taller archer → longer bow
- **Experience compatibility** (20 pts): beginners avoid compound
- **Strength+size bonus** (10 pts): short but strong → short strong bow

### Generate Perfect Bow
Creates ideal bow specification from member's profile:
- **Draw weight**: stated strength ± accuracy adjustment
- **Length**: `height × 0.95 + arm_length_adjustment`
- **Type**: experience-based (beginner→longbow/shortbow, adept→recurve, advanced→compound, master→longbow or compound)
- **Material**: experience-based (beginner→wood, advanced→composite, master→carbon)

---

## 

- Regular members: **maximum 3 bows** per profile
- VIP members: **unlimited bows** + suggest bow + generate bow
- Only the bow creator (or admin) can **edit/delete** a bow
- Only the member themselves (or admin) can **edit** a profile

---

## cURL Examples

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"t@t.com","password":"pass123","password_confirm":"pass123","height_cm":175,"arm_length_cm":65,"strength_lbs":30,"age":25,"experience":"beginner","accuracy_pct":50.0}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"pass123"}' \
  -c cookies.txt

# List bows (with session cookie)
curl http://localhost:8000/api/bows/ -b cookies.txt

# Create bow
curl -X POST http://localhost:8000/api/bows/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"name":"My Bow","bow_type":"recurve","draw_weight_lbs":30,"length_cm":155,"material":"wood"}'

# VIP: suggest bow
curl http://localhost:8000/api/vip/suggest-bow/ -b cookies.txt

# VIP: generate & save bow
curl -X POST http://localhost:8000/api/vip/generate-bow/ \
  -H "Content-Type: application/json" \
  -b cookies.txt -d '{}'
```
