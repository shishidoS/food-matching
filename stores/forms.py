from django import forms
from .models import PostFood, PostTags

class ItemPostForm(forms.ModelForm):
    # タグの選択フィールド（複数選択可能）
    tags = forms.ModelMultipleChoiceField(
        queryset=PostTags.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        required=False,
        label='タグ'
    )
    
    # 新しいタグを追加するためのフィールド
    new_tags = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '新しいタグをカンマ区切りで入力（例: 野菜,有機,国産）'
        }),
        label='新しいタグ',
        help_text='複数のタグはカンマ(,)で区切って入力してください'
    )
    
    # 新しいタグの色情報を保存するhiddenフィールド
    new_tags_colors = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.HiddenInput(),
        help_text='タグと色の対応情報をJSON形式で保存'
    )

    class Meta:
        model = PostFood
        fields = ['name', 'description', 'use_date', 'quantity', 'unit', 'image', 'tags']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '食材名を入力してください'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '食材の説明を入力してください（任意）'
            }),
            'use_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '数量を入力してください'
            }),
            'unit': forms.Select(attrs={
                'class': 'form-select'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'name': '食材名',
            'description': '食材の説明',
            'use_date': '使用期限',
            'quantity': '数量',
            'unit': '単位',
            'image': '食材画像'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 必須フィールドの設定
        self.fields['name'].required = True
        self.fields['use_date'].required = True
        self.fields['quantity'].required = True
        self.fields['unit'].required = True
        
        # タグの選択肢を名前順でソート
        self.fields['tags'].queryset = PostTags.objects.all().order_by('name')

    def clean_quantity(self):
        """数量のバリデーション"""
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError('数量は0より大きい値を入力してください。')
        return quantity

    def save(self, commit=True):
        import json
        
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            
            # まず選択されたタグを保存
            self.save_m2m()
            
            # 新しいタグの処理
            new_tags_str = self.cleaned_data.get('new_tags', '')
            new_tags_colors_str = self.cleaned_data.get('new_tags_colors', '')
            
            if new_tags_str:
                new_tag_names = [tag.strip() for tag in new_tags_str.split(',') if tag.strip()]
                
                # 色情報をJSONから取得
                tag_colors = {}
                if new_tags_colors_str:
                    try:
                        tag_colors = json.loads(new_tags_colors_str)
                    except json.JSONDecodeError:
                        tag_colors = {}
                
                for tag_name in new_tag_names:
                    # 個別の色を取得（デフォルトは#28a745）
                    tag_color = tag_colors.get(tag_name, '#28a745')
                    
                    # タグの重複チェックと作成（色も指定）
                    tag, created = PostTags.objects.get_or_create(
                        name=tag_name,
                        defaults={'color': tag_color}
                    )
                    if created:
                        print(f"新しいタグを作成しました: {tag_name} (色: {tag_color})")  # デバッグ用
                    # 食材にタグを追加
                    instance.tags.add(tag)
        
        return instance

class TagCreateForm(forms.ModelForm):
    """タグ作成用フォーム"""
    class Meta:
        model = PostTags
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'タグ名を入力してください'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'value': '#6c757d'
            })
        }
        labels = {
            'name': 'タグ名',
            'color': 'タグカラー'
        }

class ItemSearchForm(forms.Form):
    """食材検索用フォーム"""
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '食材名で検索...'
        }),
        label='検索キーワード'
    )
    
    tag = forms.ModelChoiceField(
        queryset=PostTags.objects.all(),
        required=False,
        empty_label='すべてのタグ',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='タグで絞り込み'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tag'].queryset = PostTags.objects.all().order_by('name')