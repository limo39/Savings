from django.db import models
from django.contrib.auth.models import User

class SavingsGroup(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    savings_group = models.ForeignKey(SavingsGroup, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=20)
    id_number = models.CharField(max_length=20)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

class Transaction(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=50, unique=True)
    transaction_date = models.DateTimeField(auto_now_add=True)

class Contribution(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True)
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.member.user.username} - {self.amount}'
