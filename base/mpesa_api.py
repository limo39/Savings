import requests
import json
from django.http import JsonResponse

def contribute(request):
    # Get the member ID and contribution amount from the request
    member_id = request.POST['member_id']
    amount = request.POST['amount']

    # Use the Mpesa API to initiate a payment request
    headers = {
        "Authorization": "Bearer {MwB2lpyKSBqGflIjRTWyFG4rhTTa}",
        "Content-Type": "application/json"
    }
    data = {
        "BusinessShortCode": "{paybill_number}",
        "Password": "{password}",
        "Timestamp": "{timestamp}",
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": "{phone_number}",
        "PartyB": "{paybill_number}",
        "PhoneNumber": "{phone_number}",
        "CallBackURL": "https://savings/mpesa/callback",
        "AccountReference": "{member_id}",
        "TransactionDesc": "Member contribution"
    }
    response = requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        # Payment request was successful, return the response to the frontend
        return JsonResponse({'status': 'success', 'data': response.json()})
    else:
        # Payment request failed, return an error message to the frontend
        return JsonResponse({'status': 'error', 'message': 'Payment request failed'})

def mpesa_callback(request):
    # Get the callback data from the request
    callback_data = json.loads(request.body)

    # Update the contribution record in the database to reflect the payment status
    contribution = Contribution.objects.get(member_id=callback_data['BillRefNumber'])
    contribution.paid = True
    contribution.payment_date = timezone.now()
    contribution.save()

    # Send a confirmation message to the member
    message = "Dear member, your contribution of KES {amount} has been received. Thank you for your support!"
    send_sms(contribution.member.phone_number, message)

    # Return a success response to Mpesa
    return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})
