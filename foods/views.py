from django.shortcuts import render
from datetime import datetime

def home(request):
    return render(request, 'home.html')

def food_list(request):
    query = request.GET.get('q')
    sort = request.GET.get('sort')

    all_foods = [
        {'name': 'トマト', 'price': 120, 'category': '野菜', 'area': '東京', 'distance': 2.1, 'created_at': datetime(2025, 6, 17)},
        {'name': 'りんご', 'price': 100, 'category': '果物', 'area': '名古屋', 'distance': 5.3, 'created_at': datetime(2025, 6, 16)},
        {'name': '豚肉', 'price': 250, 'category': '肉類', 'area': '東京', 'distance': 1.2, 'created_at': datetime(2025, 6, 15)},
    ]

    if query:
        query = query.lower()
        foods = [f for f in all_foods if
                 query in f['name'].lower() or
                 query in f['category'].lower() or
                 query in f['area'].lower()]
    else:
        foods = []  # ← 検索されてないときは何も出さない！

    # 並べ替えは検索があったときだけ実行（空なら意味ないから）
    if foods and sort:
        if sort == 'price_asc':
            foods = sorted(foods, key=lambda x: x['price'])
        elif sort == 'price_desc':
            foods = sorted(foods, key=lambda x: x['price'], reverse=True)
        elif sort == 'distance':
            foods = sorted(foods, key=lambda x: x['distance'])
        elif sort == 'new':
            foods = sorted(foods, key=lambda x: x['created_at'], reverse=True)

    return render(request, 'foods/food_list.html', {'foods': foods})
