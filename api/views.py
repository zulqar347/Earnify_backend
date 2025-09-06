from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserSerializer, UserProfileSerializer, WithdrawSerializer, DepositSerializer
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from .models import UserProfile, Deposit, Withdraw
from rest_framework.authentication import BaseAuthentication
from django.db.models import F
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

class UserListCreateView(APIView):
    def get(self, request):
        if request.user.is_superuser:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        else:
            return Response("You Are not Authorized To view This Page!", status=status.HTTP_401_UNAUTHORIZED)
        
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            profile = UserProfile.objects.create(user= user)
            profile.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class ProfileListView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    def get(self, request):
        profile = UserProfile.objects.all()#filter(user=request.user)
        serializer = UserProfileSerializer(profile, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def watch_ad(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    profile.refresh_ads() # Now this will work

    if profile.ads_watched_today >= 10:
        return JsonResponse({'status': 'limit_reached', 'message': 'You have watched all 10 ads for today!'})

    # Give reward
    if profile.referral_count <=4:
        profile.balance += F('balance') + 1 #profile.referral_count +1
        
    else:
        profile.balance += 5
        
    profile.ads_watched_today += 1
    profile.save()

    return JsonResponse({
        'status': 'success',
        'balance': profile.balance,
        'ads_remaining': 10 - profile.ads_watched_today
    })
        


class WithdrawCreateView(APIView):
    def get(self, request):
        withdraw = Withdraw.objects.get(profile=request.user.profile)
        serializer = WithdrawSerializer(withdraw, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = WithdrawSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
        

class DepositListCreateView(APIView):
    def get(self, request):
        deposit = Deposit.objects.get(user = request.user)
        serializer = DepositSerializer(deposit)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = DepositSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user = request.user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


