from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import *
from .apps import MarketConfig

app_name = MarketConfig.name

urlpatterns = [
    path('', GalleryView.as_view(), name="gallery-view"),
    path('lots/<str:slug>', LotView.as_view(), name="lot-view"),

    path('profiles/<str:slug>', ProfileView.as_view(), name="profile-view"),
    path('my_albums', MyAlbumsView.as_view(), name="my-albums-view"),
    path('my_arts', MyArtsView.as_view(), name="my-arts-view"),
    path('favourites', FavouritesView.as_view(), name="favourites-view"),
    path('cart', CartView.as_view(), name="cart-view"),

    path('signup', SignUp.as_view(), "signup-view"),
    path('login', SignIn.as_view(), "login-view"),
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
