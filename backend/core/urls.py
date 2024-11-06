from django.urls import path
from . import views

urlpatterns = [
    # Auth endpoints
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    
    # Dashboard endpoints
    path('dashboard/stats/', views.get_dashboard_stats, name='dashboard-stats'),
    path('dashboard/analytics/', views.get_dashboard_analytics, name='dashboard-analytics'),
    
    # Retailers endpoints
    path('retailers/', views.get_retailers, name='retailers-list'),
    path('retailers/search/', views.search_retailers, name='retailers-search'),
    path('retailers/recent/', views.get_recent_retailers, name='recent-retailers'),
    path('retailers/<str:retailer_id>/', views.get_retailer_details, name='retailer-details'),
    
    # Dues endpoints
    path('dues/', views.get_dues, name='dues-list'),
    path('dues/create/', views.create_due, name='create-due'),
    path('dues/<str:due_id>/', views.get_due_details, name='due-details'),
    path('dues/<str:due_id>/pay/', views.make_payment, name='make-payment'),
]