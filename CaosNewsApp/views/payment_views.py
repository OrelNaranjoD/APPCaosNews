from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from transbank.error.transbank_error import TransbankError
from transbank.error.transaction_commit_error import TransactionCommitError
from transbank.webpay.webpay_plus.transaction import Transaction
import random


@csrf_exempt
@require_http_methods(["POST"])
def webpay_plus_create(request):
    """Vista para crear transacción de pago con Webpay Plus"""
    buy_order = str(random.randrange(1000000, 99999999))
    session_id = str(random.randrange(1000000, 99999999))
    amount = request.POST.get("amount")
    subscription_type = request.POST.get("subscription_type")
    return_url = request.build_absolute_uri(reverse("webpay-plus-commit"))
    create_request = {
        "buy_order": buy_order,
        "session_id": session_id,
        "amount": amount,
        "return_url": return_url,
    }
    response = (Transaction()).create(buy_order, session_id, amount, return_url)
    return render(
        request,
        "webpay/plus/create.html",
        {
            "request": create_request,
            "response": response,
            "amount": amount,
            "subscription_type": subscription_type,
        },
    )


@csrf_exempt
@require_http_methods(["GET"])
def webpay_plus_commit(request):
    """Vista para confirmar transacción de pago con Webpay Plus"""
    token = request.GET.get("token_ws") or request.GET.get("TBK_TOKEN")
    try:
        response = (Transaction()).commit(token=token)
    except TransactionCommitError as e:
        return render(request, "webpay/plus/error.html", {"message": str(e)})
    return render(
        request, "webpay/plus/commit.html", {"token": token, "response": response}
    )
