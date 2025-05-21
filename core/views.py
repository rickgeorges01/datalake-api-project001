from django.contrib.auth.models import User
from .models import AccessRight
from .serializers import AccessRightSerializer, AuditLogSerializer, TransactionSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Transaction, AuditLog
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Q, Avg, Count


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def grant_access(request):
    username = request.data.get('username')
    resource = request.data.get('resource')

    try:
        user = User.objects.get(username=username)
        access, created = AccessRight.objects.get_or_create(user=user, resource=resource)
        access.can_access = True
        access.save()
        return Response({'message': f'Accès donné à {username} pour {resource}'})
    except User.DoesNotExist:
        return Response({'error': 'Utilisateur non trouvé'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def revoke_access(request):
    username = request.data.get('username')
    resource = request.data.get('resource')

    try:
        user = User.objects.get(username=username)
        access = AccessRight.objects.get(user=user, resource=resource)
        access.can_access = False
        access.save()
        return Response({'message': f'Accès retiré à {username} pour {resource}'})
    except AccessRight.DoesNotExist:
        return Response({'error': 'Accès non existant'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def access_list(request):
    accesses = AccessRight.objects.filter(user=request.user)
    serializer = AccessRightSerializer(accesses, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_list(request):
    queryset = Transaction.objects.all()

    # Filtres dynamiques
    filters = {
        'payment_method': request.GET.get('payment_method'),
        'country': request.GET.get('country'),
        'product_category': request.GET.get('product_category'),
        'status': request.GET.get('status'),
    }

    for key, value in filters.items():
        if value:
            filter_key = key  # correspond au champ du modèle
            queryset = queryset.filter(**{filter_key: value})

    # Projection dynamique
    fields_param = request.GET.get('fields')
    if fields_param:
        fields = [f.strip() for f in fields_param.split(',')]
    else:
        fields = None

    if request.GET.get("all") == "true":
        serializer = TransactionSerializer(queryset, many=True, fields=fields)
        return Response(serializer.data)

    # Pagination
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(queryset, request)

    serializer = TransactionSerializer(result_page, many=True, fields=fields)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_spend(request):
    now = timezone.now()
    five_minutes_ago = now - timedelta(minutes=5)

    recent_transactions = Transaction.objects.filter(order_date__gte=five_minutes_ago)
    total_spent = recent_transactions.aggregate(total=Sum('amount'))['total'] or 0

    return Response({
        "timestamp": now,
        "transactions_checked": recent_transactions.count(),
        "total_spent_last_5_minutes": round(total_spent, 2)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def total_per_user(request):
    results = Transaction.objects.values(
        'customer_name', 'payment_method'
    ).annotate(total_spent=Sum('amount')).order_by('-total_spent')

    return Response(results)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_products(request):
    try:
        top_n = int(request.GET.get('x', 5))
    except ValueError:
        return Response({"error": "x doit être un entier"}, status=400)

    results = Transaction.objects.values(
        'product_category'
    ).annotate(total_quantity=Sum('amount')).order_by('-total_quantity')[:top_n]

    return Response({
        "top": top_n,
        "result": results
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def average_spend(request):
    avg = Transaction.objects.aggregate(avg=Avg('amount'))['avg'] or 0
    return Response({"average_transaction_amount": round(avg, 2)})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def average_rating(request):
    avg = Transaction.objects.aggregate(avg=Avg('customer_rating'))['avg'] or 0
    return Response({"average_customer_rating": round(avg, 2)})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sales_per_country(request):
    data = Transaction.objects.values('country').annotate(
        total=Sum('amount')
    ).order_by('-total')
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rating_distribution(request):
    from django.db.models import Count
    bins = Transaction.objects.values('customer_rating').annotate(count=Count('id')).order_by('customer_rating')
    return Response(bins)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def daily_activity(request):
    from django.db.models.functions import TruncDate
    data = Transaction.objects.annotate(
        date=TruncDate('order_date')
    ).values('date').annotate(count=Count('id')).order_by('date')
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def busiest_day(request):
    from django.db.models.functions import TruncDate
    data = Transaction.objects.annotate(
        date=TruncDate('order_date')
    ).values('date').annotate(count=Count('id')).order_by('-count').first()
    return Response(data or {"error": "Aucune transaction"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_logs(request):
    logs = AuditLog.objects.all().order_by('-timestamp')[:100]
    serializer = AuditLogSerializer(logs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_resources(request):
    resources = {
        "transactions": {
            "count": Transaction.objects.count(),
            "fields": [f.name for f in Transaction._meta.fields]
        },
        "audit_logs": {
            "count": AuditLog.objects.count(),
            "fields": [f.name for f in AuditLog._meta.fields]
        }
    }
    return Response(resources)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lineage(request, id):
    path = f"/api/version/{id}/"
    logs = AuditLog.objects.filter(path=path).order_by('-timestamp')
    serializer = AuditLogSerializer(logs, many=True)
    return Response({
        "transaction_id": id,
        "access_count": logs.count(),
        "access_log": serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_version(request, id):
    return Response({
        "error": "Le versioning n’est pas activé dans le système. Cet appel est réservé à un futur cas d’usage."
    }, status=501)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_transactions(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return Response({"error": "Paramètre 'q' manquant"}, status=400)

    queryset = Transaction.objects.filter(
        Q(customer_name__icontains=query) |
        Q(country__icontains=query) |
        Q(product_category__icontains=query) |
        Q(status__icontains=query)
    )

    serializer = TransactionSerializer(queryset[:50], many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def repush_transaction(request, id):
    try:
        transaction = Transaction.objects.get(pk=id)
        # Ici tu simules l’envoi dans Kafka :
        print(f"RE-PUSH: {transaction.customer_name} → {transaction.amount}€")
        return Response({
            "message": f"Transaction {id} repushée dans le pipeline avec succès.",
            "data": TransactionSerializer(transaction).data
        })
    except Transaction.DoesNotExist:
        return Response({"error": "Transaction non trouvée"}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def train_model(request):
    # Ici on simule le lancement d’un entraînement
    print("[ML] Début de l'entraînement du modèle sur les données de transactions...")
    return Response({
        "status": "success",
        "message": "Entraînement du modèle ML déclenché (simulation)"
    })
