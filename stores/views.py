from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Recipe
from django.shortcuts import render


def home(request):
    return render(request, 'index.html')
@csrf_exempt
def add_test_table_data(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        instructions = request.POST.get('instructions')
        image_url = request.POST.get('image_url', None)

        recipe = Recipe.objects.create(
            title=title,
            description=description,
            instructions=instructions,
            image_url=image_url
        )
        return JsonResponse({'message': 'データが追加されました', 'id': recipe.id})
    return JsonResponse({'error': '無効なリクエスト'}, status=400)