from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.template.context_processors import request
from PIL import Image
import io

from django.views import View

from .apps import MarketConfig
from .forms import CustomerForm, PictureForm
from .models import *


class Register(View):
    def get(self, request):
        form = CustomerForm()
        return render(request, 'registration/register.html', {'form': form})

    def post(self, request):
        form = CustomerForm(request.POST)

        if form.is_valid():
            customer = form.save(commit=False)
            customer.set_password(form.cleaned_data['password'])
            customer.save()
            user = authenticate(username=customer.username, password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
            return redirect('/')


class AnnouncementCreate(View):
    def get(self, request):
        form = PictureForm()
        return render(request, 'announcement_create.html', {'form': form})

    def post(self, request):
        form = PictureForm(request.POST, request.FILES)

        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.author = request.user
            announcement.save()
            # for image in request.FILES.getlist('images'):
            # print(request.FILES.getlist('images'))

            # for image in form.cleaned_data["images"]:
            l = []
            for image in request.FILES.getlist('images'):
                l.append(PictureImg(image=image, announcement=announcement))

            PictureImg.objects.bulk_create(l)
            return redirect(reverse(f"{MarketConfig.name}:announcement_url", kwargs={"slug": announcement.slug}))
        return redirect("/")


class AnnouncementEdit(View):
    def get(self, request, slug):
        picture = get_object_or_404(Picture, slug=slug)
        form = PictureForm(instance=picture)
        return render(request, 'announcement_edit.html', {'form': form})

    def post(self, request, slug):
        picture = get_object_or_404(Picture, slug=slug)
        form = PictureForm(request.POST, instance=picture)

        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.author = request.user
            announcement.save()
            print(request.FILES.getlist('images'))
            for image in request.FILES.getlist('images'):
                announcement_image = PictureImg(image=image, announcement=announcement)
                announcement_image.save()
            return redirect(reverse(f"{MarketConfig.name}:announcement_url", kwargs={"slug": announcement.slug}))
        return redirect("/")


class AnnouncementView(View):
    def get(self, request, slug):
        picture = get_object_or_404(Picture, slug__iexact=slug)
        images = PictureImg.objects.filter(announcement=picture)
        print(images)
        return render(request, template_name="announcement.html",
                      context={"picture": picture, "picture_images": images})

