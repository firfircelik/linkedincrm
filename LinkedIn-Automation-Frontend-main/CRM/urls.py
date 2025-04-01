from django.contrib import admin
from django.urls import path
from django.urls import include, path
from . import views
from .views import UserLoginView, CampaignListAPIView, ColdLeadsAPIView, UserLoginAPIView, UpdateLeadStatusAPIView, AccountsPerformanceAPIView
from .rest_views import NewCampaignAPIView, ProfileUpdateAPIView, ConnectLinkedinAccountAPIView, LeadsFileListAPIView, AddAccountAPIView, NoteListCreateAPIView, AccountListView, SavedSearchListView, LeadsListView, LeadsListDownloadAPIView, LeadsFileListAPIViewV1, CampaignProfilesDownloadAPIView, ConnectLinkedinAccountAPIViewV1
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', UserLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.index, name="Home"),
    path("campaign/", views.campaign, name="Campaign"),
    path("pipeline", views.pipeline, name="Pipeline"),
    path("setting/", views.setting, name="Setting"),
    path("accounts/", views.accounts, name="Accounts"),
    path("new_campaign/", views.new_campaign, name="new_campaign"),
    path("pending_campaigns", views.pending_campaigns, name="pending_campaigns"),
    path("prompt_management/", views.prompt_management, name="prompt_management"),
    path("analysis", views.analysis, name="analysis"),
    path("account_details/<int:account_id>/", views.account_details, name="account_details"),
    path("user_metrics_distribution/", views.user_metrics_distribution, name="user_metrics_distribution"),
    path('cold_leads/<int:user_id>/', views.cold_leads, name="cold_leads"),
    path('cold_leads/', views.cold_leads, name="cold_leads"),
    path('account_reporting/', views.account_reporting, name="account_reporting"),
    path('api/campaigns/', CampaignListAPIView.as_view(), name='api_campaigns'),
    path('api/cold_leads/', ColdLeadsAPIView.as_view(), name='api_cold_leads'),
    path('api/cold_leads/<int:user_id>/', ColdLeadsAPIView.as_view(), name='api_cold_leads_with_id'),
    path('api/login/', csrf_exempt(UserLoginAPIView.as_view()), name='api_login'),
    path('api/profiles/update-lead-status/<int:profile_id>/', UpdateLeadStatusAPIView.as_view(), name='update-lead-status'),
    path('api/accounts_performance/', AccountsPerformanceAPIView.as_view(), name='api_accounts_performance'),
    path('api/new_campaign/', NewCampaignAPIView.as_view(), name='new_campaign'),
    path('api/profile/<int:pk>/', ProfileUpdateAPIView.as_view(), name='profile-update'),
    path('api/settings/connect_linkedin_account/', ConnectLinkedinAccountAPIViewV1.as_view(), name='connect-linkedin-account'),
    path('api/settings/leads-list/', LeadsFileListAPIViewV1.as_view(), name='leads-list'),
    path('api/settings/download_leads/<int:campaign_id>/', CampaignProfilesDownloadAPIView.as_view(), name='download-leads'),
    path('api/settings/upload_leads/', LeadsFileListAPIView.as_view(), name='upload-leads'),
    path('api/settings/add_account/', AddAccountAPIView.as_view(), name='add-account'),
    path('api/notes/<int:profile_id>/', NoteListCreateAPIView.as_view(), name='note-list-create'),
    path('api/accounts/', AccountListView.as_view(), name='account-list'),
    path('api/savedsearches/<int:user_id>/', SavedSearchListView.as_view(), name='saved-search-list'),
    path('api/leadslist/<int:user_id>/', LeadsListView.as_view(), name='leads-list'),
]

