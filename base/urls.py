from django.urls import path
from django.contrib.auth import views as auth_views
from .views import remove_member, create_member, DownloadTransactionsPDF, dashboard, member_dashboard, superuser_dashboard, member_registration, deactivate_user, home, signup, CustomLoginView

urlpatterns = [
    path('', home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('signup/', auth_views.LogoutView.as_view(), name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('member_dashboard/', member_dashboard, name='member_dashboard'),
    path('superuser_dashboard/', superuser_dashboard, name='superuser_dashboard'),
    path('member_registration/', member_registration, name='member_registration'),
    path('deactivate_user/<int:user_id>/', deactivate_user, name='deactivate_user'),
    path('dashboard/', dashboard, name='dashboard'),
    path('download_transactions/', DownloadTransactionsPDF, name='DownloadTransactionsPDF'),
    path('create_member/', create_member, name='create_member'),
    path('remove_member/', remove_member, name='remove_member'),   
]