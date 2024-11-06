from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, RetailerProfile, BankDetails, Document, CreditAssessment,
    Transaction, Payment, DueEntry, ExistingLoan
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'

class RetailerProfileSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = RetailerProfile
        fields = '__all__'

class BankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankDetails
        fields = '__all__'

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'

class CreditAssessmentSerializer(serializers.ModelSerializer):
    retailer_name = serializers.CharField(source='retailer.user_profile.business_name', read_only=True)
    
    class Meta:
        model = CreditAssessment
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.business_name', read_only=True)
    retailer_name = serializers.CharField(source='retailer.business_name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class DueEntrySerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.business_name', read_only=True)
    retailer_name = serializers.CharField(source='retailer.business_name', read_only=True)
    retailer_phone = serializers.CharField(source='retailer.phone', read_only=True)
    
    class Meta:
        model = DueEntry
        fields = '__all__'

class ExistingLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExistingLoan
        fields = '__all__'