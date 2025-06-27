from django.db import models
from django.contrib.auth.models import User

class PostFood(models.Model):
    """食材テーブル"""
    UNIT_CHOICES = [
        ('kg', 'キログラム'),
        ('g', 'グラム'),
        ('L', 'リットル'),
        ('ml', 'ミリリットル'),
        ('個', '個'),
        ('袋', '袋'),
        ('箱', '箱'),
        ('本', '本'),
        ('枚', '枚'),
        ('束', '束'),
        ('パック', 'パック'),
        ('その他', 'その他'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name="食材名")
    description = models.TextField(blank=True, verbose_name="食材の説明")
    image = models.ImageField(upload_to='foods/', blank=True, null=True, verbose_name="画像")
    use_date = models.DateField(verbose_name="使用期限")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="数量")
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='個', verbose_name="単位")
    # タグとの多対多関係
    tags = models.ManyToManyField('PostTags', blank=True, verbose_name="タグ")
    # 店舗アカウント（作成者）
    store_account = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="店舗アカウント", related_name='store_foods')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    is_active = models.BooleanField(default=True, verbose_name="有効")

    class Meta:
        verbose_name = "食材"
        verbose_name_plural = "食材"
        ordering = ['-created_at']
        db_table = 'post_food'

    def __str__(self):
        return f"{self.name} ({self.quantity}{self.unit})"

    @property
    def quantity_with_unit(self):
        """数量と単位を組み合わせた表示"""
        return f"{self.quantity}{self.unit}"

class PostTags(models.Model):
    """タグテーブル"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True, verbose_name="タグ名")
    color = models.CharField(max_length=7, default='#6c757d', verbose_name="タグカラー", help_text="HEXカラーコード（例: #28a745）")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")

    class Meta:
        verbose_name = "タグ"
        verbose_name_plural = "タグ"
        ordering = ['name']
        db_table = 'post_tags'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # デフォルトカラーの設定（念のため）
        if not self.color:
            self.color = '#6c757d'
        super().save(*args, **kwargs)

class PostTagging(models.Model):
    """食材とタグの中間テーブル（カスタムフィールドが必要な場合）"""
    food = models.ForeignKey(PostFood, on_delete=models.CASCADE, verbose_name="食材")
    tag = models.ForeignKey(PostTags, on_delete=models.CASCADE, verbose_name="タグ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="関連付け日時")
    
    class Meta:
        unique_together = ('food', 'tag')
        verbose_name = "食材タグ関連"
        verbose_name_plural = "食材タグ関連"
        db_table = 'post_tagging'

    def __str__(self):
        return f"{self.food.name} - {self.tag.name}"