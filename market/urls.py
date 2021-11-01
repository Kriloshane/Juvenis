from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import *
from .apps import MarketConfig

app_name = MarketConfig.name

urlpatterns = [
    path('accounts/register/', Register.as_view(), name='register_url'),
    path('announcement/create/', AnnouncementCreate.as_view(), name='announcement_create_url'),
    # path('announcement/<str:slug>/', AnnouncementView.as_view(), name="announcement_url"),
    path('announcement/<str:slug>/', AnnouncementView.as_view(), name="announcement_url"),
    path('announcement/edit/<str:slug>/', AnnouncementEdit.as_view(), name="announcement_edit_url")
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
