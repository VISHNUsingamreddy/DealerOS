from django.urls import path
from reconcile import views
urlpatterns=[path('',views.index,name='index'),path('api/disagreements/',views.disagreements_api,name='api')]
