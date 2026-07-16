from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 101)]

class CheckoutForm(forms.Form):
    first_name = forms.CharField(max_length=100, label='Имя')
    last_name = forms.CharField(max_length=100, label='Фамилия')
    email = forms.EmailField(label='Email')
    phone = forms.CharField(max_length=20, label='Телефон')
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label='Адрес')
    city = forms.CharField(max_length=100, label='Город')

class CartAddProductForm(forms.Form):
    """Форма добавления товара в корзину"""
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES, 
        coerce=int,
        label='Количество',
        widget=forms.NumberInput(attrs={
            'min': '1', 
            'max': '100',
            'class': 'quantity-input',
            'value': '1'
        })
    )
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)

class CartUpdateForm(forms.Form):
    """Форма обновления количества в корзине"""
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES, 
        coerce=int,
        widget=forms.NumberInput(attrs={'min': '1', 'max': '100'})
    )