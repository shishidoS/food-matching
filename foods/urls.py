from django.urls import path
from . import views

app_name = 'foods'

urlpatterns = [
    # 食材一覧ページ（ユーザー側）
    path('', views.food_list, name='food_list'),
    
    # 食材詳細ページ（レビュー機能付き）
    path('<int:food_id>/', views.food_detail, name='food_detail'),
    
    # レビュー関連API
    path('reviews/<int:food_id>/post/', views.review_post, name='review_post'),
    path('reviews/<int:food_id>/list/', views.reviews_list, name='reviews_list'),
    path('reviews/<int:food_id>/stats/', views.reviews_stats, name='reviews_stats'),
    
    # いいね関連API
    path('like/<int:food_id>/toggle/', views.toggle_like, name='toggle_like'),
    path('like/<int:food_id>/status/', views.get_like_status, name='like_status'),
]