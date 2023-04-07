import requests
import json
from django.http import JsonResponse
from django.test import TestCase
from django.urls import reverse
# from rest_framework.test import APIClient
# from django.conf import settings


def contribute(request):
    # Get the member ID and contribution amount from the request
    member_id = request.POST['member_id']
    amount = request.POST['amount']

    # Use the Mpesa API to initiate a payment request
    headers = {
        "Authorization": "Bearer {G9TEsFlcGzpvdrBuLjUimrv0U4Nv}",
        "Content-Type": "application/json"
    }
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    password = '{174379}{bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919}{timestamp}'.format(paybill_number='{PAYBILL_NUMBER}', passkey='{PASSKEY}', timestamp=timestamp)
    data = {
        "BusinessShortCode": "{174379}",
        "Password": 'MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMjMwNDA2MDUyMTMx',
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": "{254707261693}",
        "PartyB": "{174379}",
        "PhoneNumber": "{254707261693}",
        "CallBackURL": "https://948a-196-250-212-59.eu.ngrok.io",
        "AccountReference": member_id,
        "TransactionDesc": "Member contribution"
    }
    response = requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        print("Success")
        # Payment request was successful, redirect the user to the Mpesa checkout page
        checkout_request_id = response.json()['CheckoutRequestID']
        checkout_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush?businessShortCode={}&password={}&timestamp={}&transactionType=CustomerPayBillOnline&amount={}&partyA={}&partyB={}&phoneNumber={}&callBackURL={}&accountReference={}&transactionDesc=Member%20contribution&stkPushURL=https://sandbox.safaricom.co.ke/mpesa/stkpush'.format(data['BusinessShortCode'], password, timestamp, amount, data['PartyA'], data['PartyB'], data['PhoneNumber'], data['CallBackURL'], data['AccountReference'])
        return redirect(checkout_url)
    else:
        # Payment request failed, return an error message to the frontend
        print("Failed")
        return render(request, 'payment_failed.html')

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

# class ContributeViewTest(TestCase):
#     def setUp(self):
#         self.client = APIClient()

#     def test_contribute_view(self):
#         url = reverse('contribute')
#         data = {
#             'member_id': 123,
#             'amount': 500
#         }
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json().get('status'), 'success')