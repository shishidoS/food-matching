from django.db import models
from django.contrib.auth.models import User
from stores.models import PostFood

class FoodReview(models.Model):
    """食材レビューテーブル"""
    id = models.AutoField(primary_key=True)
    food = models.ForeignKey(PostFood, on_delete=models.CASCADE, verbose_name="食材", related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="レビューワー", related_name='food_reviews')
    comment = models.TextField(verbose_name="コメント")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="投稿日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    
    class Meta:
        unique_together = ('food', 'reviewer')
        verbose_name = "食材レビュー"
        verbose_name_plural = "食材レビュー"
        ordering = ['-created_at']
        db_table = 'food_review'
        
    def __str__(self):
        return f"{self.food.name} - {self.reviewer.username}"

class FoodLike(models.Model):
    """食材いいねテーブル"""
    id = models.AutoField(primary_key=True)
    food = models.ForeignKey(PostFood, on_delete=models.CASCADE, verbose_name="食材", related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ユーザー", related_name='food_likes')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="いいね日時")
    
    class Meta:
        unique_together = ('food', 'user')
        verbose_name = "食材いいね"
        verbose_name_plural = "食材いいね"
        ordering = ['-created_at']
        db_table = 'food_like'
        
    def __str__(self):
        return f"{self.food.name} - {self.user.username}"
