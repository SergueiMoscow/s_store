from django import forms

from shop.models import Order


class SearchForm(forms.Form):
    q = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'Поиск'}
        )
    )


class OrderModelForm(forms.ModelForm):

    DELIVERY_CHOICES = (
        (0, 'Выберите, пожалуйста'),
        (1, 'Самовывоз'),
        (2, 'Доставка'),
    )
    delivery = forms.TypedChoiceField(
        label='Доставка',
        choices=DELIVERY_CHOICES,
        coerce=int
    )

    class Meta:
        model = Order
        # 1 вариант
        # fields = ['name', 'phone', 'email']
        # 2 вариант
        exclude = ['discount', 'status', 'need_delivery', 'date_order', 'date_send']
        labels = [
            {'address': 'Полный адрес (страна, город, индекс, улица, дом, квартира)'}
        ]
        widgets = {
            'address': forms.Textarea(
                attrs={'rows': 6, 'cols': 80, 'placeholder': 'При самовывозе можно оставить это поле пустым'}
            ),
            'notice': forms.Textarea(
                attrs={'rows': 6, 'cols': 80}
            )
        }

