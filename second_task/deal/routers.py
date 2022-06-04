from audioop import add
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import add_deal

urlpatterns = [
    path('add-deal', add_deal),
]