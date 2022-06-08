from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import *
from .apps import MarketConfig

app_name = MarketConfig.name

urlpatterns = [
    path('', GalleryView.as_view(), name="gallery-view"),
    path('lots/<str:slug>/', LotView.as_view(), name="lot-view"),

    path('profiles/<str:slug>/', ProfileView.as_view(), name="profile-view"),

    path('profiles/<str:user_slug>/albums/', MyAlbumsView.as_view(), name="my-albums-view"),
    path('profiles/<str:user_slug>/albums/<str:slug>', AlbumView.as_view(), name="album-view"),

    path('arts/<str:slug>', ArtsView.as_view(), name="my-arts-view"),
    path('favourites/', FavouritesView.as_view(), name="favourites-view"),
    path('cart/<str:slug>', CartView.as_view(), name="cart-view"),
    path('lots/create_lot', CreateLotView.as_view(), name="create-lot-view"),

    path('signup/', SignUp.as_view(), name="my_signup"),
    path('login/', SignIn.as_view(), name="my_login"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# accounts/login/ [name='login']
# accounts/logout/ [name='logout']
# accounts/password_change/ [name='password_change']
# accounts/password_change/done/ [name='password_change_done']
# accounts/password_reset/ [name='password_reset']
# accounts/password_reset/done/ [name='password_reset_done']
# accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
# accounts/reset/done/ [name='password_reset_complete']
