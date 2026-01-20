from django.contrib import admin

from .models import Invoice, PaymentMethod, Subscription, SubscriptionPlan


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ["name", "plan_type", "price", "interval", "is_active"]
    list_filter = ["plan_type", "interval", "is_active"]
    search_fields = ["name", "plan_type"]
    ordering = ["price"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "status", "current_period_end", "is_active"]
    list_filter = ["status", "plan", "cancel_at_period_end"]
    search_fields = ["user__username", "user__email", "stripe_subscription_id"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "stripe_subscription_id"]


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["user", "method_type", "last4", "brand", "is_default"]
    list_filter = ["method_type", "brand", "is_default"]
    search_fields = ["user__username", "stripe_payment_method_id"]
    ordering = ["-is_default", "-created_at"]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "amount", "status", "invoice_date", "paid_at"]
    list_filter = ["status", "currency", "invoice_date"]
    search_fields = ["user__username", "stripe_invoice_id"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "stripe_invoice_id", "stripe_invoice_url"]
