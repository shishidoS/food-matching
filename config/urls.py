from django.contrib import admin
from django.urls import path
from stores.views import add_test_table_data,home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('add_test_table_data/', add_test_table_data, name='add_test_table_data'),
    path('', home, name='home'),
]
