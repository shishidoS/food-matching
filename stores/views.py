from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.db.models import Q
from django.urls import reverse
from datetime import date, timedelta
from .models import PostFood, PostTags
from .forms import ItemPostForm, TagCreateForm, ItemSearchForm

def store_redirect(request):
    """
    /stores/ へのアクセス処理
    アカウント機能無効化中：直接 item_list へリダイレクト
    """
    # アカウント機能を一時的に無効化
    return redirect('stores:item_list')
    
    # 以下はアカウント機能有効時に使用
    # if request.user.is_authenticated:
    #     return redirect('stores:item_list')
    # else:
    #     return redirect('accounts:login')

# @login_required  # アカウント機能無効化中はコメントアウト
def item_list(request):
    """食材一覧ページ（店舗アカウント専用）"""
    # 検索フォームの処理
    search_form = ItemSearchForm(request.GET)
    
    # アカウント機能無効化中：全ての食材を表示
    items = PostFood.objects.filter(is_active=True)
    
    # アカウント機能有効時：現在のユーザーの食材のみを表示
    # items = PostFood.objects.filter(
    #     store_account=request.user,
    #     is_active=True
    # )
    
    # 検索・フィルタリング
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        tag_filter = search_form.cleaned_data.get('tag')
        
        if query:
            items = items.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )
        
        if tag_filter:
            items = items.filter(tags=tag_filter)
    
    items = items.distinct().order_by('-created_at')
    
    # 期限切れ・期限間近のアラート
    today = date.today()
    warning_date = today + timedelta(days=3)
    
    expired_items = items.filter(use_date__lt=today)
    warning_items = items.filter(use_date__gte=today, use_date__lte=warning_date)
    
    # タグ一覧（フィルタ用）
    all_tags = PostTags.objects.all().order_by('name')
    
    context = {
        'items': items,
        'search_form': search_form,
        'all_tags': all_tags,
        'expired_items': expired_items,
        'warning_items': warning_items,
        'store_name': 'デモ店舗',  # アカウント機能無効化中は固定値
        # 'store_name': request.user.username,  # アカウント機能有効時
    }
    return render(request, 'stores/item_list.html', context)

# @login_required  # アカウント機能無効化中はコメントアウト
def item_post(request, item_id=None):
    """食材投稿・編集ページ"""
    # 編集の場合、食材の存在確認（アカウント機能無効化中は所有者チェックなし）
    item = None
    if item_id:
        item = get_object_or_404(PostFood, id=item_id)
        # アカウント機能有効時の所有者チェック
        # item = get_object_or_404(PostFood, id=item_id, store_account=request.user)
    
    if request.method == 'POST':
        form = ItemPostForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            if not item:  # 新規作成の場合
                # アカウント機能無効化中：デフォルトユーザーを設定
                try:
                    from django.contrib.auth.models import User
                    default_user = User.objects.first()
                    if not default_user:
                        # ユーザーが存在しない場合は作成
                        default_user = User.objects.create_user('demo_store', 'demo@example.com', 'demo123')
                    
                    # フォームインスタンスのstore_accountを設定
                    food_item = form.save(commit=False)
                    food_item.store_account = default_user
                    food_item.save()
                    
                    # 新しいタグの処理を手動で実行
                    form.save_m2m()  # 選択されたタグを保存
                    
                    # 新しいタグの処理
                    new_tags_str = form.cleaned_data.get('new_tags', '')
                    new_tags_color = form.cleaned_data.get('new_tags_color', '#28a745')
                    
                    if new_tags_str:
                        new_tag_names = [tag.strip() for tag in new_tags_str.split(',') if tag.strip()]
                        for tag_name in new_tag_names:
                            tag, created = PostTags.objects.get_or_create(
                                name=tag_name,
                                defaults={'color': new_tags_color}
                            )
                            if created:
                                messages.info(request, f"新しいタグ「{tag_name}」を作成しました（色: {new_tags_color}）。")
                            food_item.tags.add(tag)
                    
                    food_item = food_item  # 作成されたインスタンスを使用
                except Exception as e:
                    messages.error(request, f"ユーザー設定エラー: {e}")
                    food_item = form.save()  # フォールバック
                # アカウント機能有効時
                # food_item.store_account = request.user
                # food_item = form.save()
            else:
                # 編集の場合は通常通り保存
                food_item = form.save()
            
            action = "更新" if item else "登録"
            messages.success(request, f"食材「{food_item.name}」を{action}しました。")
            return redirect('stores:item_detail', item_id=food_item.id)
    else:
        form = ItemPostForm(instance=item)
    
    # 既存のタグ一覧も取得
    existing_tags = PostTags.objects.all().order_by('name')
    
    context = {
        'form': form,
        'item': item,
        'existing_tags': existing_tags,
        'is_edit': item is not None,
        'store_name': 'デモ店舗',  # アカウント機能無効化中は固定値
        # 'store_name': request.user.username,  # アカウント機能有効時
    }
    return render(request, 'stores/item_post.html', context)

# @login_required  # アカウント機能無効化中はコメントアウト
def item_detail(request, item_id):
    """食材詳細ページ"""
    # アカウント機能無効化中：全ての食材にアクセス可能
    item = get_object_or_404(PostFood, id=item_id, is_active=True)
    # アカウント機能有効時：自分の食材のみ
    # item = get_object_or_404(PostFood, id=item_id, store_account=request.user, is_active=True)
    
    # 期限チェック
    today = date.today()
    is_expired = item.use_date < today
    is_warning = item.use_date <= today + timedelta(days=3) and not is_expired
    
    context = {
        'item': item,
        'is_expired': is_expired,
        'is_warning': is_warning,
        'store_name': 'デモ店舗',  # アカウント機能無効化中は固定値
        # 'store_name': request.user.username,  # アカウント機能有効時
    }
    return render(request, 'stores/item_detail.html', context)

# @login_required  # アカウント機能無効化中はコメントアウト
def item_delete(request, item_id):
    """食材削除（論理削除）"""
    # アカウント機能無効化中：全ての食材を削除可能
    item = get_object_or_404(PostFood, id=item_id)
    # アカウント機能有効時：自分の食材のみ
    # item = get_object_or_404(PostFood, id=item_id, store_account=request.user)
    
    if request.method == 'POST':
        item.is_active = False
        item.save()
        messages.success(request, f"食材「{item.name}」を削除しました。")
        return redirect('stores:item_list')
    
    context = {
        'item': item,
        'store_name': 'デモ店舗',  # アカウント機能無効化中は固定値
        # 'store_name': request.user.username,  # アカウント機能有効時
    }
    return render(request, 'item_delete.html', context)

# @login_required  # アカウント機能無効化中はコメントアウト
def tag_create_ajax(request):
    """AJAX でタグを作成"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = TagCreateForm(request.POST)
        if form.is_valid():
            tag = form.save()
            return JsonResponse({
                'success': True,
                'tag_id': tag.id,
                'tag_name': tag.name,
                'tag_color': tag.color
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

# @login_required  # アカウント機能無効化中はコメントアウト
def dashboard(request):
    """ダッシュボード（概要ページ）"""
    # 統計情報の取得（アカウント機能無効化中：全ての食材対象）
    total_items = PostFood.objects.filter(is_active=True).count()
    # アカウント機能有効時
    # total_items = PostFood.objects.filter(store_account=request.user, is_active=True).count()
    
    today = date.today()
    expired_items = PostFood.objects.filter(
        # store_account=request.user,  # アカウント機能有効時
        is_active=True,
        use_date__lt=today
    ).count()
    
    warning_items = PostFood.objects.filter(
        # store_account=request.user,  # アカウント機能有効時
        is_active=True,
        use_date__gte=today,
        use_date__lte=today + timedelta(days=3)
    ).count()
    
    recent_items = PostFood.objects.filter(
        # store_account=request.user,  # アカウント機能有効時
        is_active=True
    ).order_by('-created_at')[:5]
    
    context = {
        'total_items': total_items,
        'expired_items': expired_items,
        'warning_items': warning_items,
        'recent_items': recent_items,
        'store_name': 'デモ店舗',  # アカウント機能無効化中は固定値
        # 'store_name': request.user.username,  # アカウント機能有効時
    }
    return render(request, 'stores/dashboard.html', context)