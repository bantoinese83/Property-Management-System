import stripe
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import RentPayment


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # Get the payment ID from metadata
        payment_id = session.get("metadata", {}).get("payment_id")
        if payment_id:
            try:
                payment = RentPayment.objects.get(id=payment_id)
                payment.status = "paid"
                payment.payment_method = "online"
                payment.transaction_id = session.get("payment_intent")
                payment.payment_processor = "stripe"
                payment.processed_at = timezone.now()
                payment.save()
            except RentPayment.DoesNotExist:
                # This should not happen if everything is set up correctly
                pass

    return HttpResponse(status=200)
