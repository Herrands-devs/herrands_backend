from .models import Wallet, Payments
from rest_framework.response import Response

def update_agent_wallet(user, amount, errand_id , payment_mode):
    try:
        wallet, created = Wallet.objects.get_or_create(user=user)
        payment_instance = Payments.objects.get(errand__id = errand_id )
        if payment_mode == 'ONLINE' and payment_instance.status == 'c':
            deduction = amount * 0.15
            remaining_amount = amount - deduction
            wallet.balance += remaining_amount
            wallet.save()
        elif payment_mode == 'CASH':
            deduction = amount * 0.15
            remaining_amount = wallet.balance - deduction
            wallet.balance += remaining_amount
            wallet.save()
    except Exception as e:
        return Response({"success": False, "message": f"An error occurred: {str(e)}"}, status=500)