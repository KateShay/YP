from django import forms
from .models import Partner, SalesHistory, PartnerType


class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = [
            'name', 'partner_type', 'rating', 'address',
            'director_name', 'phone', 'email', 'inn', 'logo'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'partner_type': forms.Select(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'director_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+79999999999'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'inn': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_rating(self):
        rating = self.cleaned_data['rating']
        if rating < 0:
            raise forms.ValidationError("Рейтинг должен быть неотрицательным числом")
        return rating


class SalesHistoryFilterForm(forms.Form):
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='С даты'
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='По дату'
    )