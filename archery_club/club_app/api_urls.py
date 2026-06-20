"""
REST API URL configuration for the Archery Club.

All routes are prefixed with /api/ (see mojprojekt/urls.py).

Route map:
  POST   /api/auth/register/           ← register new member
  POST   /api/auth/login/              ← login
  POST   /api/auth/logout/             ← logout

  GET    /api/members/                 ← list all members
  GET    /api/members/<id>/            ← member detail
  PUT    /api/members/<id>/            ← update member (own or admin)
  GET    /api/me/                      ← current user's profile
  PUT    /api/me/                      ← update current user's profile

  GET    /api/bows/                    ← list all bows
  POST   /api/bows/                    ← create new bow
  GET    /api/bows/<id>/               ← bow detail
  PUT    /api/bows/<id>/               ← update bow
  DELETE /api/bows/<id>/               ← delete bow

  GET    /api/my-bows/                 ← current user's bows
  POST   /api/my-bows/                 ← add bow to profile
  DELETE /api/my-bows/<bow_id>/        ← remove bow from profile

  GET    /api/vip/suggest-bow/         ← VIP: suggest a bow
  GET    /api/vip/generate-bow/        ← VIP: generate bow spec
  POST   /api/vip/generate-bow/        ← VIP: generate + save bow

  GET    /api/stats/                   ← club statistics
"""

from django.urls import path
from . import api_views

urlpatterns = [
    # ── Auth ──────────────────────────────────
    path('auth/register/', api_views.APIRegisterView.as_view(), name='api_register'),
    path('auth/login/', api_views.APILoginView.as_view(), name='api_login'),
    path('auth/logout/', api_views.APILogoutView.as_view(), name='api_logout'),

    # ── Members ───────────────────────────────
    path('members/', api_views.APIMemberListView.as_view(), name='api_member_list'),
    path('members/<int:pk>/', api_views.APIMemberDetailView.as_view(), name='api_member_detail'),
    path('me/', api_views.APIMeView.as_view(), name='api_me'),

    # ── Bows ──────────────────────────────────
    path('bows/', api_views.APIBowListView.as_view(), name='api_bow_list'),
    path('bows/<int:pk>/', api_views.APIBowDetailView.as_view(), name='api_bow_detail'),

    # ── My Bows ───────────────────────────────
    path('my-bows/', api_views.APIMyBowsView.as_view(), name='api_my_bows'),
    path('my-bows/<int:bow_id>/', api_views.APIRemoveBowFromProfileView.as_view(), name='api_remove_bow'),

    # ── VIP Features ──────────────────────────
    path('vip/suggest-bow/', api_views.APIVIPSuggestBowView.as_view(), name='api_vip_suggest'),
    path('vip/generate-bow/', api_views.APIVIPGenerateBowView.as_view(), name='api_vip_generate'),

    # ── Stats ─────────────────────────────────
    path('stats/', api_views.api_stats, name='api_stats'),
]
