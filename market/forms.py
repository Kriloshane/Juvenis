from django.contrib.auth import get_user_model
from django import forms
from django.forms.utils import ErrorList
from django.http import request

from .models import Customer, Picture, PictureImg


class CustomerForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput())

    def is_valid(self, *args, **kwargs):
        is_base_valid = super(CustomerForm, self).is_valid(*args, **kwargs)

        if self.cleaned_data['password'] != self.cleaned_data['password1']:
            self.errors['password'] = ErrorList(['введенные пароли не одинаковы'])
            return False
        return is_base_valid

    class Meta:
        model = Customer
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'password1']
        widgets = {
            "password": forms.PasswordInput()
        }


class PictureForm(forms.ModelForm):
    name = forms.CharField(label='Название', widget=forms.TextInput())
    price = forms.IntegerField(label='Стоимость', min_value=0, widget=forms.NumberInput())
    description = forms.CharField(label='Описание', widget=forms.Textarea(), required=False)
    images = forms.ImageField(
        label='Выберите изображение для загрузки',
        widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    class Meta:
        model = Picture
        fields = ['name', 'price', 'length', 'width', 'description', 'genre', 'style', 'category',
                  'theme', 'technique', 'tags']

    # def clean_dimensions(self):
    #    s = self.cleaned_data.get('dimensions')
    #    l = s.split('x')
    #    if len(l) == 2:
    #        if l[0].isdigit() and l[1].isdigit():
    #            return s
    #    return ValueError('Формат размеров введен некорректно...')


class PictureImgForm(forms.ModelForm):
    class Meta:
        model = PictureImg
        fields = ['image', 'announcement']

    # def save(self, commit=True, *args, **kwargs):
    #     super(Picture, self).save(*args, **kwargs)
    #     self.announcement = request.user
