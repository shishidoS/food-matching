from django.db import models
from foods.models import Ingredient  # 他アプリのモデルをインポート

class Recipe(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructions = models.TextField()
    image_url = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.title

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity_text = models.CharField(max_length=100)  # 「大さじ1」のようなテキストを保存

    def __str__(self):
        return f"{self.ingredient.name} ({self.quantity_text})"