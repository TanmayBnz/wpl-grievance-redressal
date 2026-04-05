from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Public
    path('', views.index, name='index'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('login/', views.login_page, name='login'),

    # Auth
    path('register/', views.register, name='register'),
    path('signin/', auth_views.LoginView.as_view(template_name='GRsystem/signin.html'), name='signin'),
    path('logout/', auth_views.LogoutView.as_view(template_name='GRsystem/logout.html'), name='logout'),
    path('login_redirect/', views.login_redirect, name='login_redirect'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    # Password reset flow
    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='GRsystem/password_reset.html'),
         name='password_reset'),
    path('password-reset-done/',
         auth_views.PasswordResetDoneView.as_view(template_name='GRsystem/password_reset_done.html'),
         name='password_reset_done'),
    re_path(r'^password-reset-confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,40})/$',
            auth_views.PasswordResetConfirmView.as_view(template_name='GRsystem/password_reset_confirm.html'),
            name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='GRsystem/password_reset_complete.html'),
         name='password_reset_complete'),

    # Student
    path('dashboard/', views.dashboard, name='dashboard'),
    path('password/', views.change_password, name='change_password'),
    path('complaints/', views.complaints, name='complaints'),
    path('list/', views.complaint_list, name='list'),
    path('slist/', views.solved_list, name='slist'),
    path('pdf/', views.pdf_view, name='pdf_view'),

    # Grievance officer
    path('counter/', views.counter, name='counter'),
    path('allcomplaints/', views.allcomplaints, name='allcomplaints'),
    path('solved/', views.solved_complaints, name='solved'),
    path('passwords/', views.change_password_g, name='change_password_g'),
    path('pdf_g/', views.pdf_viewer, name='pdf_viewer'),
]
