from django.urls import path
from . import views

app_name = 'stores'

urlpatterns = [
    # メインエントリーポイント
    path('', views.store_redirect, name='store_redirect'),
    
    # ダッシュボード
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # 食材関連
    path('items/', views.item_list, name='item_list'),
    path('items/post/', views.item_post, name='item_post'),
    path('items/<int:item_id>/', views.item_detail, name='item_detail'),
    path('items/<int:item_id>/edit/', views.item_post, name='item_edit'),
    path('items/<int:item_id>/delete/', views.item_delete, name='item_delete'),
    
    # タグ関連
    path('tags/create-ajax/', views.tag_create_ajax, name='tag_create_ajax'),
]