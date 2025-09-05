from django.contrib import admin
from .models import UserProfile, Deposit, Withdraw

# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'referall_code', 'referral_link', 'referral_count', 'balance']


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'status', 'created_at']
    list_editable =['status',]

@admin.register(Withdraw)
class WithdrawAdmin(admin.ModelAdmin):
    list_display = ['profile', 'amount', 'status', 'account_no', 'method']
    list_editable = ['status']