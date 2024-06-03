from django.urls import path, re_path
from . import views
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('', views.place_order, name='place_order'),
    path('pay/', views.gateway, name='gateway'),
    path('pay/success/', views.success, name='success'),
    path('corders/', views.customer, name='customer-orders'),
    path('orders/', views.shopkeeper, name='shopkeeper-orders'),
    
    re_path(r'^download/(?P<path>.*)$', views.download, name='download'),
    re_path(r'^change/(?P<path>.*)$', views.status_change, name='change'),
    re_path(r'^valid/(?P<path>.*)$', views.validator, name='valid'),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
        re_path(r'^static/(?P<path>.*)$', serve, {
            'document_root': settings.STATIC_ROOT,
        }),
    ]
