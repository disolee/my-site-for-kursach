from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 101)]

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