from django.urls import path
from .views import * ##hello_world, schema_view   , add_person ,Query_Qty

from django.urls import path
from .views import hello_world
# from . import schema_view

urlpatterns = [
    path('hello/', hello_world, name='hello_world'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('add_person/', add_person, name='add_person'),
    path('Query_Qty/', Query_Qty, name='Query_Qty'),
    path('image_wall/', image_wall, name='image_wall'),
]
