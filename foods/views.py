from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Q, Count
from stores.models import PostFood, PostTags
from .models import FoodReview, FoodLike
from datetime import date, timedelta
import json

def food_list(request):
    """食材一覧ページ（ユーザー側）"""
    # storesアプリの食材データを取得（いいね数と一緒に）
    foods = PostFood.objects.filter(is_active=True).annotate(
        like_count=Count('likes'),
        review_count=Count('reviews')
    )
    
    # 検索機能
    query = request.GET.get('query')
    tag_id = request.GET.get('tag')
    
    if query:
        foods = foods.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    if tag_id:
        foods = foods.filter(tags=tag_id)
    
    foods = foods.distinct().order_by('-created_at')
    
    # 期限チェック
    today = date.today()
    warning_date = today + timedelta(days=3)
    
    # タグ一覧
    all_tags = PostTags.objects.all().order_by('name')
    
    context = {
        'foods': foods,
        'all_tags': all_tags,
        'query': query,
        'selected_tag': tag_id,
        'today': today,
        'warning_date': warning_date,
    }
    return render(request, 'foods/food_list.html', context)

def food_detail(request, food_id):
    """食材詳細ページ（レビュー機能付き）"""
    food = get_object_or_404(PostFood, id=food_id, is_active=True)
    
    # 期限チェック
    today = date.today()
    is_expired = food.use_date < today
    is_warning = food.use_date <= today + timedelta(days=3) and not is_expired
    
    context = {
        'food': food,
        'is_expired': is_expired,
        'is_warning': is_warning,
    }
    return render(request, 'foods/food_detail.html', context)

def review_post(request, food_id):
    """レビュー投稿API"""
    if request.method == 'POST':
        try:
            food = get_object_or_404(PostFood, id=food_id, is_active=True)
            
            # デフォルトユーザーを取得（認証機能無効化中）
            default_user = User.objects.first()
            if not default_user:
                default_user = User.objects.create_user('demo_user', 'demo@example.com', 'demo123')
            
            # 既存のレビューがあるかチェック
            existing_review = FoodReview.objects.filter(food=food, reviewer=default_user).first()
            if existing_review:
                return JsonResponse({
                    'success': False,
                    'error': 'すでにレビューを投稿済みです。'
                })
            
            # リクエストデータを取得
            data = json.loads(request.body)
            comment = data.get('comment', '').strip()
            
            # 空のコメントの場合はエラー
            if not comment:
                return JsonResponse({
                    'success': False,
                    'error': 'コメントを入力してください。'
                })
            
            # レビューを作成
            review = FoodReview.objects.create(
                food=food,
                reviewer=default_user,
                comment=comment
            )
            
            return JsonResponse({
                'success': True,
                'review_id': review.id,
                'message': 'レビューを投稿しました。'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def reviews_list(request, food_id):
    """レビュー一覧取得API"""
    try:
        food = get_object_or_404(PostFood, id=food_id, is_active=True)
        reviews = FoodReview.objects.filter(food=food).select_related('reviewer')
        
        reviews_data = []
        for review in reviews:
            reviews_data.append({
                'id': review.id,
                'reviewer_name': review.reviewer.username,
                'comment': review.comment,
                'created_at': review.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        # 統計情報
        total_reviews = reviews.count()
        total_likes = FoodLike.objects.filter(food=food).count()
        
        return JsonResponse({
            'success': True,
            'reviews': reviews_data,
            'stats': {
                'total_reviews': total_reviews,
                'total_likes': total_likes
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def reviews_stats(request, food_id):
    """レビュー統計取得API"""
    try:
        food = get_object_or_404(PostFood, id=food_id, is_active=True)
        reviews = FoodReview.objects.filter(food=food)
        
        total_reviews = reviews.count()
        total_likes = FoodLike.objects.filter(food=food).count()
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total_reviews': total_reviews,
                'total_likes': total_likes
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def toggle_like(request, food_id):
    """いいねトグルAPI"""
    if request.method == 'POST':
        try:
            food = get_object_or_404(PostFood, id=food_id, is_active=True)
            
            # デフォルトユーザーを取得（認証機能無効化中）
            default_user = User.objects.first()
            if not default_user:
                default_user = User.objects.create_user('demo_user', 'demo@example.com', 'demo123')
            
            # 既存のいいねをチェック
            existing_like = FoodLike.objects.filter(food=food, user=default_user).first()
            
            if existing_like:
                # いいねを削除
                existing_like.delete()
                is_liked = False
                message = 'いいねを取り消しました。'
            else:
                # いいねを追加
                FoodLike.objects.create(food=food, user=default_user)
                is_liked = True
                message = 'いいねしました！'
            
            # 現在のいいね数を取得
            total_likes = FoodLike.objects.filter(food=food).count()
            
            return JsonResponse({
                'success': True,
                'is_liked': is_liked,
                'total_likes': total_likes,
                'message': message
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def get_like_status(request, food_id):
    """いいね状態取得API"""
    try:
        food = get_object_or_404(PostFood, id=food_id, is_active=True)
        
        # デフォルトユーザーを取得（認証機能無効化中）
        default_user = User.objects.first()
        if not default_user:
            default_user = User.objects.create_user('demo_user', 'demo@example.com', 'demo123')
        
        # ユーザーがいいねしているかチェック
        is_liked = FoodLike.objects.filter(food=food, user=default_user).exists()
        total_likes = FoodLike.objects.filter(food=food).count()
        
        return JsonResponse({
            'success': True,
            'is_liked': is_liked,
            'total_likes': total_likes
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
