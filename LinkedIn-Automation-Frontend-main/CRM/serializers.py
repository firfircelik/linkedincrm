from rest_framework import serializers
from .models import Campaign, Note, Account, SavedSearch, LeadsList

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'  # Adjust this based on what data you want to expose

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'content', 'created_at', 'profile']

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__' 

class SavedSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedSearch
        fields = '__all__'

class LeadsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadsList
        fields = '__all__'