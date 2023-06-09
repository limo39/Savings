from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse, FileResponse
from django.db.models import Sum
from .models import SavingsGroup, Member, Transaction, Contribution
from .forms import MemberRegistrationForm, MemberCreationForm, DeactivateUserForm, MyUserCreationForm, LoginForm, SavingsGroupForm
from django.views.generic import TemplateView
from django.template.loader import get_template

from base.forms import SavingsGroupForm
from base.models import SavingsGroup

import io
from django.utils import timezone
from xhtml2pdf import pisa
from PyPDF2 import PdfFileMerger
from django.views.decorators.csrf import csrf_exempt

def home(request):
    return render(request, 'base/home.html')


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
    return render(request, 'base/member_dashboard.html', context)

@login_required
def member_dashboard(request):
    try:
        member = request.user.member
    except Member.DoesNotExist:
        # Redirect to the signup page if the user doesn't have a member object
        return redirect('base/signup.html')

    # Render the member dashboard page
    return render(request, 'base/member_dashboard.html', {'member': member})

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

@user_passes_test(lambda u: u.is_superuser)
@login_required
def create_member(request):
    form = MemberCreationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            member = form.save()
            password = form.cleaned_data['password1']
            member.groups.add(Group.objects.get(name='members'))
            member.save()
            send_mail(
                'Your account has been created',
                f'Your account has been created. Your temporary password is {password}. Please log in and change your password.',
                'from@example.com',
                [member.email],
                fail_silently=False,
            )
            return redirect('dashboard')
    return render(request, 'create_member.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def superuser_dashboard(request):
    if request.method == 'POST':
        form = SavingsGroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Savings group created successfully!')
            return redirect('base/superuser_dashboard.html')
    else:
        form = SavingsGroupForm()

    savings_group = request.user.member.savings_group
    members = savings_group.member_set.all()
    transactions = Transaction.objects.filter(member__savings_group=savings_group)
    total_contributions = transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    context = {
        'members': members,
        'transactions': transactions,
        'total_contributions': total_contributions,
        'form': form,
    }
    return render(request, 'base/superuser_dashboard.html', context)

@user_passes_test(lambda u: u.is_superuser)
def remove_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    member.delete()
    return redirect('superuser_dashboard')

def member_registration(request):
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            user.set_password(password)
            user.save()
            mobile_number = form.cleaned_data.get('mobile_number')
            id_number = form.cleaned_data.get('id_number')
            email = form.cleaned_data.get('email')
            user = authenticate(username=user.username, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = MemberRegistrationForm()

    return render(request, 'base/member_registration.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
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

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'base/signup.html', {'form': form})


def CustomLoginView(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home.html')  
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form}) 

@login_required
def dashboard(request):
    member = request.user.member
    year_contribution = Contribution.objects.filter(member=member, transaction_date__year=timezone.now().year).aggregate(total=Sum('amount'))['total'] or 0
    mtd_contribution = Contribution.objects.filter(member=member, transaction_date__month=timezone.now().month).aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'user': request.user,
        'year_contribution': year_contribution,
        'mtd_contribution': mtd_contribution,
    }

    return render(request, 'dashboard.html', context)

@login_required
def DownloadTransactionsPDF(request):
    member = request.user.member

    # Generate HTML for the PDF
    template = get_template('dashboard.html')
    html = template.render({'member': member})

    # Generate PDF using xhtml2pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transaction_history.pdf"'
    pisa_status = pisa.CreatePDF(
        html, dest=response, encoding='utf-8'
    )
    if pisa_status.err:
        return HttpResponse('PDF generation failed')
    return response

@csrf_exempt
def mpesa_callback(request):
    if request.method == 'POST':
        # Parse the callback data from Mpesa
        callback_data = json.loads(request.body)

        # Get the relevant data from the callback
        transaction_reference = callback_data['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value']
        amount = callback_data['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value']
        phone_number = callback_data['Body']['stkCallback']['CallbackMetadata']['Item'][4]['Value']
        payment_date = callback_data['Body']['stkCallback']['CallbackMetadata']['Item'][3]['Value']

        # Update your database with the payment details
        contribution = Contribution.objects.get(transaction_reference=transaction_reference)
        contribution.amount = amount
        contribution.phone_number = phone_number
        contribution.payment_date = payment_date
        contribution.status = 'Paid'
        contribution.save()

        # Send a confirmation message to the member
        message = f"Dear member, your contribution of KES {amount} has been received. Thank you for your support!"
        send_sms(phone_number, message)

        # Return a success response to Mpesa
        response_data = {'ResultCode': 0, 'ResultDesc': 'Success'}
        return JsonResponse(response_data)
    else:
        # Return an error response if the request method is not POST
        response_data = {'ResultCode': 1, 'ResultDesc': 'Failed'}
        return JsonResponse(response_data)