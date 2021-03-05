from django.urls import path
from . import views


urlpatterns = [
    path('profile/<uuid:id>/', views.user_detail.as_view(), name="user-detail"),
    path('create/', views.create_user.as_view(), name="create-user"),
    path('', views.get_users.as_view(), name="get-users"),
]