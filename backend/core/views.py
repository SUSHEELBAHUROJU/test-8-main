from django.shortcuts import get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import UserProfile, RetailerProfile, DueEntry, Transaction, Payment
from .serializers import (
    UserProfileSerializer, RetailerProfileSerializer, DueEntrySerializer,
    TransactionSerializer, PaymentSerializer
)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    try:
        user_type = request.data.get('user_type')
        if not user_type in ['retailer', 'supplier']:
            return Response({
                'error': 'Invalid user type'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create User
        user_data = request.data.get('user', {})
        user = User.objects.create_user(
            username=user_data.get('email'),
            email=user_data.get('email'),
            password=user_data.get('password'),
            first_name=user_data.get('firstName', '')
        )

        # Create UserProfile
        user_profile = UserProfile.objects.create(
            user=user,
            user_type=user_type,
            business_name=request.data.get('businessName'),
            phone=request.data.get('phone'),
            gst_number=request.data.get('gstNumber'),
            address=request.data.get('address')
        )

        login(request, user)
        
        return Response({
            'message': 'Registration successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'user_type': user_type,
                'business_name': user_profile.business_name
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        if 'user' in locals():
            user.delete()
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    try:
        user = User.objects.get(email=email)
        if user.check_password(password):
            user_profile = UserProfile.objects.get(user=user)
            login(request, user)
            return Response({
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'user_type': user_profile.user_type,
                    'business_name': user_profile.business_name
                }
            })
    except User.DoesNotExist:
        pass
    
    return Response({
        'error': 'Invalid credentials'
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'message': 'Logged out successfully'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_stats(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type == 'supplier':
        total_outstanding = DueEntry.objects.filter(
            supplier=user_profile,
            status='pending'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        active_retailers = DueEntry.objects.filter(
            supplier=user_profile
        ).values('retailer').distinct().count()
        
        monthly_sales = Transaction.objects.filter(
            supplier=user_profile,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        overdue_amount = DueEntry.objects.filter(
            supplier=user_profile,
            status='overdue'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return Response({
            'totalOutstanding': total_outstanding,
            'activeRetailers': active_retailers,
            'monthlySales': monthly_sales,
            'overdueAmount': overdue_amount
        })
    
    return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_analytics(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type == 'supplier':
        # Get last 6 months of data
        end_date = timezone.now()
        start_date = end_date - timedelta(days=180)
        
        # Transaction trends
        transactions = Transaction.objects.filter(
            supplier=user_profile,
            created_at__range=(start_date, end_date)
        ).values('created_at__date').annotate(
            amount=Sum('amount')
        ).order_by('created_at__date')
        
        # Payment trends
        payment_trends = DueEntry.objects.filter(
            supplier=user_profile,
            created_at__range=(start_date, end_date)
        ).values('created_at__month').annotate(
            on_time=Count('id', filter=Q(status='paid')),
            late=Count('id', filter=Q(status='overdue'))
        ).order_by('created_at__month')
        
        # Retailer growth
        retailer_growth = DueEntry.objects.filter(
            supplier=user_profile,
            created_at__range=(start_date, end_date)
        ).values('created_at__month').annotate(
            count=Count('retailer', distinct=True)
        ).order_by('created_at__month')
        
        return Response({
            'transactions': transactions,
            'paymentTrends': payment_trends,
            'retailerGrowth': retailer_growth
        })
    
    return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_retailers(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type == 'supplier':
        retailers = UserProfile.objects.filter(
            user_type='retailer',
            received_dues__supplier=user_profile
        ).distinct()
        serializer = UserProfileSerializer(retailers, many=True)
        return Response(serializer.data)
    
    return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_retailers(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    query = request.GET.get('q', '')
    
    if user_profile.user_type == 'supplier':
        retailers = UserProfile.objects.filter(
            user_type='retailer'
        ).filter(
            Q(business_name__icontains=query) |
            Q(phone__icontains=query)
        )[:10]
        serializer = UserProfileSerializer(retailers, many=True)
        return Response(serializer.data)
    
    return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recent_retailers(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type == 'supplier':
        retailers = UserProfile.objects.filter(
            user_type='retailer',
            received_dues__supplier=user_profile
        ).distinct().order_by('-received_dues__created_at')[:5]
        serializer = UserProfileSerializer(retailers, many=True)
        return Response(serializer.data)
    
    return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_retailer_details(request, retailer_id):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    retailer = get_object_or_404(UserProfile, id=retailer_id, user_type='retailer')
    
    if user_profile.user_type != 'supplier':
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get retailer's payment history
    total_dues = DueEntry.objects.filter(
        supplier=user_profile,
        retailer=retailer
    ).count()
    
    paid_on_time = 0
    payment_history = 'new'
    
    if total_dues > 0:
        paid_on_time = DueEntry.objects.filter(
            supplier=user_profile,
            retailer=retailer,
            status='paid'
        ).count()
        
        payment_ratio = paid_on_time / total_dues
        payment_history = 'excellent' if payment_ratio > 0.9 else \
                         'good' if payment_ratio > 0.7 else \
                         'fair'
    
    # Get total outstanding amount
    outstanding_amount = DueEntry.objects.filter(
        supplier=user_profile,
        retailer=retailer,
        status__in=['pending', 'overdue']
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Get recent transactions
    recent_transactions = Transaction.objects.filter(
        supplier=user_profile,
        retailer=retailer
    ).order_by('-created_at')[:5]
    
    response_data = {
        'id': retailer.id,
        'business_name': retailer.business_name,
        'phone': retailer.phone,
        'address': retailer.address,
        'payment_history': payment_history,
        'outstanding_amount': outstanding_amount,
        'total_dues': total_dues,
        'paid_on_time': paid_on_time,
        'recent_transactions': TransactionSerializer(recent_transactions, many=True).data
    }
    
    return Response(response_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dues(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type == 'supplier':
        dues = DueEntry.objects.filter(supplier=user_profile)
        serializer = DueEntrySerializer(dues, many=True)
        return Response(serializer.data)
    elif user_profile.user_type == 'retailer':
        dues = DueEntry.objects.filter(retailer=user_profile)
        serializer = DueEntrySerializer(dues, many=True)
        return Response(serializer.data)
    
    return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_due(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type != 'supplier':
        return Response({'error': 'Only suppliers can create dues'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = DueEntrySerializer(data={
        **request.data,
        'supplier': user_profile.id
    })
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_due_details(request, due_id):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    due = get_object_or_404(DueEntry, id=due_id)
    
    if due.supplier != user_profile and due.retailer != user_profile:
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = DueEntrySerializer(due)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_payment(request, due_id):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    due = get_object_or_404(DueEntry, id=due_id)
    
    if due.retailer != user_profile:
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = PaymentSerializer(data={
        **request.data,
        'due': due_id
    })
    
    if serializer.is_valid():
        payment = serializer.save()
        due.status = 'paid'
        due.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)