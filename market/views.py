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


class IndexView(View):

    def get(self, request):
        """Examples"""
        photography = Picture.objects.filter(category=Picture.PictureCategory.photography)
        abstraction = Picture.objects.filter(genre=Picture.PictureGenre.abstraction)
        portrait = Picture.objects.filter(genre=Picture.PictureGenre.portrait)
        sketch = Picture.objects.filter(category=Picture.PictureCategory.sketch)

        """Albums"""
        albums = BuyerAlbum.objects.all().reverse()[0:10]

        return render(request, 'new/index.html', {
            'albums': albums,
            'p': photography,
            'a': abstraction,
            'por': portrait,
            's': sketch,
        })


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
        input_price_min = int(request.GET.get('min_price', min_price))
        input_price_max = int(request.GET.get('max_price', max_price))

        pics = Picture.objects.filter(
            Q(category__in=categories_filter) & Q(style__in=styles_filter) & Q(genre__in=genres_filter) &
            Q(price__lte=input_price_max) & Q(price__gte=input_price_min))
        print(pics)

        if request.user.is_authenticated:
            try:
                request.user.cart.pictures.all()
            except:
                BuyerCart.objects.create(buyer=request.user)

        # Второй аргумент — кол-во фоток на странице
        paginator = Paginator(pics, 9)
        page = paginator.get_page(request.GET.get('page', 1))
        data = [list() for i in range(3)]
        i = 0
        for lot in page.object_list.all():
            data[i % 3].append(lot)
            i += 1
        print(data)
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

        return render(request, 'new/shop.html',
                      {
                          'data': data,
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


class ContactView(View):

    def get(self, request):
        return render(request, 'new/contact.html')


class LotView(View):

    def get(self, request, slug):
        lot = Picture.objects.get(slug=slug)
        albums = request.user.albums.all()
        is_liked = False
        for album in albums:
            if lot in album.pictures.all():
                is_liked = True
        in_cart = lot in request.user.cart.pictures.all()
        author_lots = Picture.objects.filter(author=lot.author).reverse()[0:5]
        return render(request, 'new/lot.html', {
            'lot': lot,
            'albums': albums,
            'is_liked': is_liked,
            'in_cart': in_cart,
            'author_lots': author_lots
        })

    def post(self, request, slug):
        lot = Picture.objects.get(slug=slug)
        print(request.POST)
        action = request.POST['action']
        if action == "add_favour":
            album = BuyerAlbum.objects.get(id=request.POST['album_id'])
            album.pictures.add(lot)
            album.save()
        elif action == "delete_favour":
            albums = request.user.albums.all()
            for album in albums:
                if lot in album.pictures.all():
                    album.pictures.remove(lot)
        elif action == "add_cart":
            request.user.cart.pictures.add(lot)
        elif action == "delete_cart":
            request.user.cart.pictures.remove(lot)
        return redirect(lot.get_absolute_url())


def add_favour(request, slug):
    lot = Picture.objects.get(slug=slug)
    request.user.favorites.add(lot)
    return redirect(request.META.get('HTTP_REFERER'))


def delete_favour(request, slug):
    lot = Picture.objects.get(slug=slug)
    request.user.favorites.remove(lot)
    return redirect(request.META.get('HTTP_REFERER'))


class ProfileView(View):

    def get(self, request, slug):
        profile = Customer.objects.get(slug=slug)
        is_mine = request.user == profile
        if profile.is_artist():
            lots = Picture.objects.filter(author=profile).reverse()[0:4]
            sale_count = Picture.objects.filter(author=profile, for_sale=True).count()
            return render(request, 'new/artist.html',
                          {'profile': profile, 'is_mine': is_mine, 'lots': lots, 'fs_cnt': sale_count})
        elif profile.is_buyer():
            albums = BuyerAlbum.objects.filter(buyer=profile).reverse()[0:3]
            return render(request, 'new/buyer.html', {'profile': profile, 'is_mine': is_mine, 'albums': albums})

    def post(self, request, slug):
        profile = Customer.objects.get(slug=slug)
        request.user.subscriptions.add(profile)
        profile.followers.add(request.user)
        return redirect(profile.get_absolute_url())


class MyAlbumsView(View):

    def get(self, request, user_slug):
        profile = Customer.objects.get(slug=user_slug)
        albums = BuyerAlbum.objects.filter(buyer=profile)
        return render(request, 'new/albums.html', {
            'albums': albums,
            'is_mine': request.user == Customer.objects.get(slug=user_slug),
            'profile': profile
        })


def create_album(request, user_slug):
    if request.method == 'POST':
        name = request.POST.get('name')
        BuyerAlbum.objects.create(name=name, buyer=request.user)
        return redirect(request.META.get('HTTP_REFERER'))


class AlbumView(View):

    def get(self, request, user_slug, slug):
        album = BuyerAlbum.objects.get(slug=slug)
        return render(request, "new/album.html", {
            'album': album,
            'is_mine': request.user == Customer.objects.get(slug=user_slug)
        })


def add_to_album(request):
    if request.method == "POST":
        lot = Picture.objects.get(slug=request.POST.get('lot_slug', None))
        for slug in request.POST.getlist('slugs[]', ''):
            album = BuyerAlbum.objects.get(slug=slug)
            album.pictures.add(lot)
            album.save()
        return redirect(request.META.get('HTTP_REFERER'))


def delete_from_album(request):
    if request.method == "POST":
        lot = Picture.objects.get(slug=request.POST.get('lot_slug', None))
        for slug in request.POST.getlist('slugs[]', ''):
            album = BuyerAlbum.objects.get(slug=slug)
            album.pictures.remove(lot)
            album.save()
        return redirect(request.META.get('HTTP_REFERER'))


def add_comment(request):
    if request.method == "POST":
        lot = Picture.objects.get(slug=request.POST.get('lot_slug', None))
        text = request.POST.get('text')
        Review.objects.create(author=request.user, movie=lot, text=text)
        return redirect(request.META.get('HTTP_REFERER'))


def delete_comment(request, slug, id):
    Review.objects.get(id=id).delete()
    return redirect(request.META.get('HTTP_REFERER'))


def like_comment(request, slug, id):
    review = Review.objects.get(id=id)
    review.likes.add(request.user)
    review.save()
    return redirect(request.META.get('HTTP_REFERER'))


def dislike_comment(request, slug, id):
    review = Review.objects.get(id=id)
    review.likes.remove(request.user)
    review.save()
    return redirect(request.META.get('HTTP_REFERER'))


def album_delete(request, user_slug, slug):
    BuyerAlbum.objects.get(slug=slug).delete()
    return redirect(f'profiles/{request.user.slug}/albums/')


class FavouritesView(View):

    def get(self, request):
        data = [list() for i in range(4)]
        i = 0
        for album in request.user.albums.all():
            for lot in album.pictures.all():
                data[i % 4].append(lot) if [lot] not in data else 0
                i += 1
        print(data)
        return render(request, "new/favourites.html", {
            'data': data
        })


class ArtsView(View):

    def get(self, request, slug, for_sale=True):
        lots = Picture.objects.filter(author=Customer.objects.get(slug=slug)).reverse()
        return render(request, 'new/artistsgallery.html', {
            'lots': lots,
            'is_mine': request.user == Customer.objects.get(slug=slug)
        })


class CartView(View):

    def get(self, request, slug):
        return render(request, 'cart.html')


class CreateLotView(View):

    def get(self, request):
        categories = Picture.PictureCategory
        styles = Picture.PictureStyle
        genres = Picture.PictureGenre
        return render(request, 'new/lot_creating.html', {
            'categories': categories,
            'styles': styles,
            'genres': genres,
        })

    def post(self, request):
        print(request.POST)
        print(request.FILES)

        name = request.POST.get('name', 'Название')
        price = request.POST.get('price', 0)
        description = request.POST.get('description', '')
        length = request.POST.get('length', 100)
        width = request.POST.get('width', 100)
        technique = request.POST.get('technique', '')
        year_created = request.POST.get('year_created', 2000)
        category = request.POST.get('category', Picture.PictureCategory.is_absent)
        genre = request.POST.get('category', Picture.PictureGenre.is_absent)
        style = request.POST.get('style', Picture.PictureStyle.is_absent)

        lot = Picture.objects.create(name=name, author=request.user, price=price, description=description,
                                     length=length, width=width, category=category, genre=genre, style=style,
                                     technique=technique, year_created=year_created)
        for image in request.FILES.getlist('pictures[]'):
            PictureImg.objects.create(image=image, announcement=lot)

        return redirect(lot.get_absolute_url())


class SignUp(View):

    def get(self, request):
        return render(request, "new/signup.html")


class SignIn(View):

    def get(self, request):
        return render(request, "new/signin.html")
