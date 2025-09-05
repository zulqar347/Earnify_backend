from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    referall_code = models.CharField(max_length=100, null=True, blank=True)
    referred_by = models.CharField(max_length=100, null=True, blank=True)
    referral_count = models.PositiveIntegerField(default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    ads_watched_today = models.PositiveIntegerField(default=0)
    last_ad_refresh = models.DateTimeField(default=timezone.now)

    def refresh_ads(self):
        today = timezone.now().date()
        last_refresh_date = self.last_ad_refresh.date()
        if today > last_refresh_date:  # A new day has started
            self.ads_watched_today = 0
            self.last_ad_refresh = timezone.now()
            self.save()

    def save(self, *args, **kwargs):
        if not self.referall_code:
            self.referall_code = uuid.uuid4().hex[:8]
        super().save(*args, **kwargs)

    def referral_link(self):
        return f"http://localhost:5173/signup?ref={self.referall_code}"

    def __str__(self):
        return self.user.username
    
class Deposit(models.Model):
    STATUS_CHOICES =[
        ("pending", "Pending"),
        ("confirmed", 'Confirmed'),
        ('rejected', 'Rejected')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deposits')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=360)
    tracking_id = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100, default="EasyPaisa")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.status}"


class Withdraw(models.Model):
    WITHDRAW_CHOICES =[
        ("pending", "Pending"),
        ("confirmed", 'Confirmed'),
        ('rejected', 'Rejected')
    ]
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='withdraw')
    amount = models.PositiveIntegerField(default=360)
    status = models.CharField(choices=WITHDRAW_CHOICES, max_length=100, default="pending")
    account_name = models.CharField(max_length=100, default=None)
    account_no = models.CharField(max_length=100)
    method = models.CharField(max_length=100)
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile} requested {self.amount} via {self.method}"



@receiver(post_save, sender=Deposit)
def update_balance(sender, instance,created, **kwargs):
    if not created and instance.status == "confirmed":
        user = instance.user
        refree = Deposit.objects.filter(user=user).values_list('user__profile__referred_by', flat=True)[0]
        refreeProfile = UserProfile.objects.filter(referall_code=refree).first()
        
        print(refreeProfile)
        if refreeProfile:
            refreeProfile.balance += instance.amount *Decimal(0.1)
            refreeProfile.referral_count += 1
            refreeProfile.save()
    

@receiver(post_save, sender=Withdraw)
def cut_balance(sender, instance, created, **kwargs):
    if not created and instance.status == "confirmed":
        profile = instance.profile
        # profile = user.profile
        profile.balance -= instance.amount
        profile.save()
        
            
            