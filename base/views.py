from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
from django.db.models import Sum
from .models import SavingsGroup, Member, Transaction
from .forms import MemberRegistrationForm, DeactivateUserForm
from django.views.generic import TemplateView

@login_required
def member_dashboard(request):
    member = request.user.member
    transactions = member.transaction_set.order_by('-transaction_date')
    total_contributions = transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    context = {
        'member': member,
        'transactions': transactions,
        'total_contributions': total_contributions,
    }
    return render(request, 'member_dashboard.html', context)

@login_required
def superuser_dashboard(request):
    savings_group = request.user.member.savings_group
    members = savings_group.member_set.all()
    transactions = Transaction.objects.filter(member__savings_group=savings_group)
    total_contributions = transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    context = {
        'members': members,
        'transactions': transactions,
        'total_contributions': total_contributions,
    }
    return render(request, 'superuser_dashboard.html', context)

def member_registration(request):
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            member = Member.objects.create(
                user=user,
                savings_group=form.cleaned_data['savings_group'],
                mobile_number=form.cleaned_data['mobile_number'],
                id_number=form.cleaned_data['id_number'],
                email=form.cleaned_data['email'],
            )
            messages.success(request, 'Registration successful.')
            return redirect(reverse('login'))
    else:
        form = MemberRegistrationForm()
    context = {'form': form}
    return render(request, 'member_registration.html', context)

@login_required
def deactivate_user(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = UserDeactivationForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['confirm_deactivation']:
                user.is_active = False
                user.save()
                messages.success(request, 'User deactivated successfully.')
                return redirect(reverse('superuser_dashboard'))
    else:
        form = UserDeactivationForm()
    context = {'form': form, 'user': user}
    return render(request, 'deactivate_user.html', context)

class HomeView(TemplateView):
	template_name = 'base/home.html'

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

