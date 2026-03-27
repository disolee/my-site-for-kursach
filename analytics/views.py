from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .reports import ReportGenerator
from .models import ProductAnalytics


@login_required
def dashboard_view(request):
    return render(request, 'analytics/dashboard.html', {
        'days_options': [7, 14, 30, 90],
    })


@login_required
@require_GET
def api_dashboard_stats(request):
    days = int(request.GET.get('days', 7))
    
    data = {
        'conversion': ReportGenerator.get_conversion_report(days),
        'top_products': ReportGenerator.get_top_products_report(days, 5),
        'sales': ReportGenerator.get_sales_report(days),
        'user_activity': ReportGenerator.get_user_activity_report(days),
    }
    return JsonResponse(data)


@login_required
@require_GET
def api_product_detail(request, product_id):
    try:
        analytics = ProductAnalytics.objects.select_related('product').get(product_id=product_id)
        data = {
            'product_id': product_id,
            'product_name': analytics.product.name,
            'views': analytics.views_count,
            'cart_adds': analytics.cart_adds_count,
            'purchases': analytics.purchases_count,
            'view_to_cart_rate': analytics.view_to_cart_rate,
            'cart_to_purchase_rate': analytics.cart_to_purchase_rate,
            'total_revenue': float(analytics.total_revenue),
        }
        return JsonResponse(data)
    except ProductAnalytics.DoesNotExist:
        return JsonResponse({'error': 'No data found'}, status=404)