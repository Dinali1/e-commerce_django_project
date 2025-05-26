from django.contrib.auth.views import PasswordChangeView, LogoutView
from django.urls import path

from apps.views import *

urlpatterns = [
    path('', HomeListView.as_view(), name='home'),
    path('category', CategoriesView.as_view(), name='category'),
    path('category/<str:slug>', CategoriesView.as_view(), name='category'),
    path('product-detail/<str:slug>', ProductDetail.as_view(), name='product_detail'),
    path('signin', AccountView.as_view(), name='signin'),
    path('order', OrderView.as_view(), name='order'),
    path('send-email', SendMailFormView.as_view(), name='send_email'),
    path('check-email', RegisterCreateView.as_view(), name='check_email'),
    path('login', LoginFormView.as_view(), name='login'),
    path('about', WebsiteInfoView.as_view(), name='about'),
    path('profile/<int:pk>', ProfileListView.as_view(), name='profile'),
    path('district-list', district_list, name='district_list'),
    path('sell-product', MarketView.as_view(), name='sell-product'),
    path('phone-num/<int:pk>', PhoneNumberChangeVIew.as_view(), name='phone-num'),
    path('pass-change/<int:pk>', PasswordChangeView.as_view(), name='password_change'),
    path('log-exit', ExitProfileView.as_view(), name='log-exit'),
    path('stream', StreamView.as_view(), name='stream'),
    path('save-stream', SaveStreamCreteView.as_view(), name='save-stream'),
    path('oqim/<int:pk>', StreamDetailView.as_view(), name='copy-stream'),
    path('delete-stream/<int:pk>', DeleteStreamView.as_view(), name='delete-stream'),
    path('statistics', Statistics.as_view(), name='statistics'),
    path('chart/', chart_view, name='chart'),
    path('payment', PaymentCreateView.as_view(), name='payment'),
    path('operator/', OperatorListView.as_view(), name='operator'),
    path("order/list", OrderListView.as_view(), name="order-list"),
    path('request/list', RequestTemplateView.as_view(), name="request-list"),


]

