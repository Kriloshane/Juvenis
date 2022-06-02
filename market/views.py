from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.template.context_processors import request
from django.core.mail import send_mail
from django.core.paginator import Paginator
import io
from django.views import View
from django.db.models import Max, Min
from django.db.models import Q, F

from .apps import MarketConfig
from .forms import CustomerForm, PictureForm
from .models import *

from django.conf import settings


# TODO: проверить еще раз работу почты


class GalleryView(View):

    def get(self, request):
        max_price = Picture.objects.all().aggregate(Max('price'))['price__max']
        min_price = Picture.objects.all().aggregate(Min('price'))['price__min']

        if not max_price:
            max_price = 1000
        if not min_price:
            min_price = 0

        categories_filter = request.GET.getlist('category[]', Picture.PictureCategory)
        styles_filter = request.GET.getlist('style[]', Picture.PictureStyle)
        genres_filter = request.GET.getlist('genre[]', Picture.PictureGenre)
        input_price = request.GET.get('input_price', max_price)
        print(categories_filter)
        print(styles_filter)
        print(genres_filter)
        print(input_price)

        pics = Picture.objects.filter(
            Q(category__in=categories_filter) & Q(style__in=styles_filter) & Q(genre__in=genres_filter) &
            Q(price__lt=int(input_price) + 1))

        # Второй аргумент — кол-во фоток на странице
        paginator = Paginator(pics, 8)
        page = paginator.get_page(request.GET.get('page', 1))
        cnt = page.object_list.all().count()
        column1 = page.object_list.all()[0:cnt // 2 + cnt % 2]
        column2 = page.object_list.all()[cnt // 2 + cnt % 2:]
        is_paginated = page.has_other_pages()

        if page.has_previous():
            previous_url = '?page={}'.format(page.previous_page_number())
        else:
            previous_url = ''

        if page.has_next():
            next_url = '?page={}'.format(page.next_page_number())
        else:
            next_url = ''

        categories = Picture.PictureCategory
        styles = Picture.PictureStyle
        genres = Picture.PictureGenre

        return render(request, 'gallery.html',
                      {
                          'col1': column1,
                          'col2': column2,
                          'categories': categories,
                          'styles': styles,
                          'genres': genres,
                          'max_price': int(max_price),
                          'min_price': int(min_price),
                          'page': page,
                          'is_paginated': is_paginated,
                          'previous_url': previous_url,
                          'next_url': next_url,
                      })


class LotView(View):

    def get(self, request, slug):
        lot = Picture.objects.get(slug=slug)
        print(lot.reviews.all())
        return render(request, 'lot.html', {'lot': lot})


class ProfileView(View):

    def get(self, request, slug):
        profile = Customer.objects.get(slug=slug)
        is_mine = request.user == profile
        if profile.is_artist():
            return render(request, 'artist.html', {'is_mine': is_mine})
        elif profile.is_buyer():
            return render(request, 'buyer.html', {'is_mine': is_mine})


class MyAlbumsView(View):

    def get(self, request):
        return render(request, 'albums.html')


class FavouritesView(View):

    def get(self, request):
        return render(request, "liked.html")


class MyArtsView(View):

    def get(self, request):
        return render(request, 'artistgallery.html')


class CartView(View):

    def get(self):
        return render(request, 'cart.html')


class SignUp(View):

    def get(self, request):
        return (request, "registration.html")


class SignIn(View):

    def get(self, request):
        return (request, "login.html")
