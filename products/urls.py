from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.product_list_create, name='product-list-create'),
    re_path(r'^(?P<pk>.+)/?$', views.product_detail, name='product-detail'),
]