from django import forms
from django.core.exceptions import ValidationError

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
        (1, 'Доставка'),
        (2, 'Самовывоз'),
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

    def clean_delivery(self):
        value = self.cleaned_data['delivery']
        print('Clear_delivery')
        if value == 0:
            raise ValidationError('Необходимо выбрать способ доставки')
        return value

    def clean(self):
        address = self.cleaned_data['address']
        delivery = self.cleaned_data['delivery']
        if delivery == 1 and address == '':
            raise ValidationError('Укажите адрес доставки')
        return self.cleaned_data

