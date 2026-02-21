from django.urls import path
from .views import assetlinks, apple_app_site_association, payment_page

urlpatterns = [
    path('.well-known/assetlinks.json', assetlinks),
    path('.well-known/apple-app-site-association', apple_app_site_association),
    path('pay-for-me/', payment_page, name='payment_page'),
]
