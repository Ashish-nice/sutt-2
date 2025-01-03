from django.urls import path
from . import views

urlpatterns = [
    # Class-based views
    path('', views.HomeView.as_view(), name='home'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('history/', views.HistoryView.as_view(), name='history'),
]
