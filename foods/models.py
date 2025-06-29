from django.conf import settings
from django.db import models

class Refrigerator(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)

    def __str__(self):
            return self.name
        
class RefrigeratorIngredient(models.Model):
    refrigerator = models.ForeignKey(Refrigerator, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    expiry_date = models.DateField(blank=True, null=True)