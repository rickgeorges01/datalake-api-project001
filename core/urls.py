from django.urls import path
from .views import (grant_access, revoke_access, access_list,transaction_list,
recent_spend,total_per_user,top_products,audit_logs,list_resources,
transaction_version,lineage,search_transactions,repush_transaction,train_model,
average_spend,average_rating,sales_per_country,rating_distribution,daily_activity,busiest_day)

urlpatterns = [
    path('grant-access/', grant_access),
    path('revoke-access/', revoke_access),
    path('access-list/', access_list),
    path('transactions/',transaction_list),
    path('metrics/recent-spend/', recent_spend),
    path('metrics/total-per-user/', total_per_user),
    path('metrics/top-products/', top_products),
    path('metrics/avg-spend/', average_spend),
    path('metrics/avg-rating/', average_rating),
    path('metrics/sales-per-country/', sales_per_country),
    path('metrics/rating-distribution/', rating_distribution),
    path('metrics/daily-activity/', daily_activity),
    path('metrics/busiest-day/', busiest_day),
    path('audit/', audit_logs),
    path('resources/', list_resources),
    path('version/<int:id>/', transaction_version),
    path('lineage/<int:id>/', lineage),
    path('search/', search_transactions),
    path('repush/<int:id>/', repush_transaction),
    path('train-ml/', train_model),

]
