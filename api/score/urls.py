from django.urls import path
from . import views


urlpatterns = [
    path('submit/', views.submit_score.as_view(), name="submit-score"),
]