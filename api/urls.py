from . import views
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView 

urlpatterns  =[
    path('users/', views.UserListCreateView.as_view(), name='register_user'),
    path('users/profile/', views.ProfileListView.as_view(), name='profile'),
    path('token/', TokenObtainPairView.as_view(), name='login_token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('watch-ad/', views.watch_ad, name='watch-ad'), 
    path('withdraw/', views.WithdrawCreateView.as_view(), name='withdraw'),
    path("deposit/", views.DepositListCreateView.as_view(), name='deposit')
]