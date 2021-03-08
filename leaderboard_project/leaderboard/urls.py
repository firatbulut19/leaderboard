from django.urls import path
from . import views


urlpatterns = [
    path('', views.global_leaderboard.as_view(), name="global_leaderboard"),
    path('<str:country>/', views.country_leaderboard.as_view(), name="country_leaderboard"),
]