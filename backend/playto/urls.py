from django.contrib import admin
from django.urls import path
from payouts.views import PayoutViewSet
from ledger.views import BalanceView, LedgerView, AddFundsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/payouts', PayoutViewSet.as_view(), name='payouts'),
    path('api/v1/merchants/me/balance', BalanceView.as_view(), name='balance'),
    path('api/v1/merchants/me/ledger', LedgerView.as_view(), name='ledger'),
    path('api/v1/merchants/me/ledger/add-funds', AddFundsView.as_view(), name='add-funds'),
]