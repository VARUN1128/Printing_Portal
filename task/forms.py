from django import forms
from .models import Order
from . import shopkeepers

TRUE_FALSE_CHOICES = (
    (True, 'Black and White'),
    (False, 'Color')
)

shop_CHOICES = [(k, v) for k, v in shopkeepers.shops.items()]

class CustomClearableFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class PlaceOrderForm(forms.Form):
    docfile = forms.FileField(
        label='Select files',
        help_text='Allowed size per pdf: 10 MB',
        widget=CustomClearableFileInput(attrs={'multiple': True}),
    )
    no_of_copies = forms.IntegerField()
    black_and_white = forms.ChoiceField(
        choices=TRUE_FALSE_CHOICES,
        label="Print Type",
        initial='',
        widget=forms.Select(),
        required=True,
    )
    shopkeeper_email = forms.ChoiceField(
        choices=shop_CHOICES,
        label="Choose the location you want your files to be printed from",
        initial='',
        widget=forms.Select(),
    )

    class Meta:
        model = Order
        fields = ['docfile', 'no_of_copies', 'black_and_white', 'shopkeeper_email']

class otpForm(forms.Form):
    otp = forms.IntegerField()
