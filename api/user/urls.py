from django.urls import path
from . import views


urlpatterns = [
    path('profile/<uuid:id>/', views.user_detail.as_view(), name="user-detail"),
    path('create/', views.create_user.as_view(), name="create-user"),
    path('delete/', views.all_users.as_view(), name="delete-users"),
    path('populate/', views.populate_db.as_view(), name="populate-db"),
    path('', views.all_users.as_view(), name="get-users"),
]