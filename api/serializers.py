from django.contrib.auth.models import User
from .models import UserProfile, Deposit, Withdraw
from rest_framework import serializers



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username','email', 'password']
        extra_kwargs = {'password': {'write_only': True}}



class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")
    email = serializers.EmailField(source="user.email")
    password = serializers.CharField(source="user.password", write_only=True)
    class Meta:
        model = UserProfile
        fields =['id','username','email', 'password', 'referall_code', 'referral_link', 'referred_by', 'referral_count', 'balance', 'ads_watched_today']
        read_only_fields = ['referall_code', 'referral_link','referral_count','balance']

    def create(self, validated_data):
        user_data = validated_data.pop("user")   # DRF puts username/email/password inside "user"
        password = user_data.pop("password")
        user = User.objects.create(**user_data)
        user.set_password(password)
        user.save()

        # deposit = Deposit.objects.create(user=user)

        profile = UserProfile.objects.create(user=user, **validated_data)
        return profile
    


class WithdrawSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(source ="profile.balance", read_only = True, max_digits=10, decimal_places=2)
    username = serializers.SerializerMethodField(read_only=True)   # For reading
    # username_input = serializers.CharField(write_only=True)
    class Meta:
        model = Withdraw
        fields = '__all__'
        read_only_fields = ['id', 'username', 'created_at', 'profile']

    def get_username(self, obj):
        return obj.profile.user.username  
    
    def create(self, validated_data):
        user = self.context['request'].user
        if not hasattr(user, 'profile'):
            raise serializers.ValidationError("This user has no profile.")
        return Withdraw.objects.create(profile=user.profile, **validated_data)
    
class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = ['user', 'bank_name', 'tracking_id', 'amount', 'status']
        read_only_fields = ['user']