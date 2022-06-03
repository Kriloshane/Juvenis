from django.contrib import admin
from django.utils.safestring import mark_safe

from .forms import PictureImgForm
from .models import *


class InlinePictureImg(admin.TabularInline):
    model = PictureImg
    extra = 1


class PictureAdmin(admin.ModelAdmin):
    inlines = (InlinePictureImg, )

    # def get_image(self, obj):
    #     return mark_safe(f'<img src={obj.photos.first().url} width="100" height="110"')


admin.site.register(Picture, PictureAdmin)
admin.site.register(Customer)
admin.site.register(BuyerAlbum)
admin.site.register(PictureImg)
admin.site.register(Tag)
admin.site.register(Review)
