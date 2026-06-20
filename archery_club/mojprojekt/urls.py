
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from club_app import views as club_views

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Authentication
    path('', club_views.WelcomeView.as_view(), name='welcome'),
    path('login/', club_views.LoginView.as_view(), name='login'),
    path('logout/', club_views.LogoutView.as_view(), name='logout'),
    path('register/', club_views.RegisterView.as_view(), name='register'),

    # Dashboard
    path('dashboard/', club_views.DashboardView.as_view(), name='dashboard'),

    # Profile
    path('profile/edit/', club_views.ProfileEditView.as_view(), name='profile_edit'),

    # Bows
    path('bows/', club_views.BowListView.as_view(), name='bow_list'),
    path('bows/add/', club_views.BowAddView.as_view(), name='bow_add'),
    path('bows/<int:pk>/edit/', club_views.BowEditView.as_view(), name='bow_edit'),
    path('bows/<int:pk>/delete/', club_views.BowDeleteView.as_view(), name='bow_delete'),

    # Members
    path('members/', club_views.MemberListView.as_view(), name='member_list'),
    path('members/<int:pk>/', club_views.MemberDetailView.as_view(), name='member_detail'),

    # VIP Features
    path('vip/suggest-bow/', club_views.VIPSuggestBowView.as_view(), name='vip_suggest_bow'),
    path('vip/generate-bow/', club_views.VIPGenerateBowView.as_view(), name='vip_generate_bow'),

    # REST API
    path('api/', include('club_app.api_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
