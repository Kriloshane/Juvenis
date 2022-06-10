from django.db import models
from django.contrib.auth.models import AbstractUser
from django.shortcuts import reverse
from django.utils.text import slugify
from django.db.models import F, ExpressionWrapper, FloatField, Sum
from time import time
from django.utils import timezone


# TODO:  разобраться с последней активностью пользователя


class Customer(AbstractUser):  # username, password, f_n, l_n, email
    class CustomerStatus(models.TextChoices):
        artist = "A", "Художник"
        buyer = "B", "Покупатель"

    """Модель пользователя"""
    first_name = models.CharField(verbose_name="Имя", max_length=20)
    last_name = models.CharField(verbose_name="Фамилия", max_length=30)
    email = models.EmailField(verbose_name="Электронная почта", max_length=100, unique=True)
    city = models.CharField(verbose_name="Город", max_length=50, default="Москва", blank=True, null=True)
    phone_number = models.CharField(verbose_name="Телефон", max_length=12, default="+79999999999",
                                    blank=True, null=True)
    status = models.CharField(max_length=3, choices=CustomerStatus.choices, default=CustomerStatus.buyer, db_index=True,
                              verbose_name="Статус пользователя")
    biography = models.TextField(blank=True, null=True)
    followers = models.ManyToManyField("Customer", verbose_name='Подписчики', blank=True,
                                       related_name="follower_set")
    photo = models.ImageField(verbose_name="Фотография", upload_to="users_photo", null=True, blank=True,
                              default="/media/default_user_photo.jpg' %}")
    subscriptions = models.ManyToManyField("Customer", verbose_name='Подписки', blank=True)
    last_activity = models.DateTimeField(blank=True, null=True, verbose_name="Последняя активность")
    art_currency = models.IntegerField(default=0, verbose_name="Валюта")
    slug = models.SlugField(max_length=150, unique=True, blank=True, null=True, verbose_name='Ссылка')

    def __str__(self):
        if self.first_name and self.last_name and self.id:
            return f"{self.first_name} {self.last_name}"
        return f"{self.username}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(
                f"{self.username}-"
                f"{self.status}-"
                f"{timezone.now()}")
            print(self.slug)
        super(Customer, self).save(*args, **kwargs)

    def is_artist(self):
        return self.status == Customer.CustomerStatus.artist

    def is_buyer(self):
        return self.status == Customer.CustomerStatus.buyer

    def get_absolute_url(self):
        return reverse('market:profile-view', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Picture(models.Model):
    """Модель картины"""

    class PictureGenre(models.TextChoices):
        """Подмодель жанров картин"""

        is_absent = "NUL", "Отсутствует"
        abstraction = "ABS", "Абстракция"
        portrait = "PRT", "Портрет"
        landscape = "LSC", "Пейзаж"
        still_life = "STL", "Натюрморт"
        animalistics = "ANM", "Анималистика"
        battle_genre = "BTG", "Батальный жарн"
        caricature = "CRC", "Карикатура"
        grotecsue = "GRT", "Шарж"

    class PictureCategory(models.TextChoices):
        """Подмодель категорий картин"""
        is_absent = "NUL", "Отсутствует"
        painting = "PTG", "Живопись"
        graphics = "GRF", "Графика"
        poster = "PST", "Постер"
        collage = "CLG", "Коллаж"
        embroidered_painting = "EMB", "Вышитая картина"
        photography = "PHT", "Фотография"
        sculpture = "SCL", "Скульптура"
        sketch = "SKT", "Эскиз"
        ceramics = "CRM", "Керамика"

    class PictureStyle(models.TextChoices):
        """Подмодель стилей картин"""
        is_absent = "NUL", "Отсутствует"
        abstractionism = "ABS", "Абстракционизм"
        impressionism = "IMP", "Импресиионизм"
        modernism = "MDR", "Модернизм"
        cubism = "CBS", "кубизм"
        avant_gardism = "AVN", "Авангардизм"
        expressionism = "EXP", "Экспрессионизм"
        fauvism = "FVS", "Фовизм"
        pop_art = "PPA", "Поп-арт"
        realism = "RLS", "Реализм"
        surrealism = "SUR", "Сюрреализм"
        symbolism = "SMB", "Символизм"
        hyperrealism = "HYP", "Гиппереализм"

    name = models.CharField(max_length=100, verbose_name="Название", db_index=True)
    author = models.ForeignKey("Customer", on_delete=models.CASCADE, verbose_name="Автор", db_index=True,
                               related_name="pictures")
    price = models.FloatField(verbose_name="Цена", help_text="Цену указывать в рублях", db_index=True)
    # dimensions = models.CharField(verbose_name="Размеры", help_text="например, 1x1 (в метрах)", max_length=30)
    description = models.TextField(verbose_name="Описание", null=True, blank=True)
    length = models.CharField(verbose_name="Длина", max_length=40, null=True, blank=True)
    width = models.CharField(verbose_name="Ширина", max_length=40, null=True, blank=True)
    genre = models.CharField(verbose_name="Жанр", choices=PictureGenre.choices, max_length=3,
                             default=PictureGenre.is_absent, db_index=True)
    style = models.CharField(verbose_name="Стиль", choices=PictureStyle.choices, max_length=3,
                             default=PictureStyle.is_absent, db_index=True)
    category = models.CharField(verbose_name="Категория", choices=PictureCategory.choices, max_length=3,
                                default=PictureCategory.is_absent, db_index=True)
    for_sale = models.BooleanField(default=True, verbose_name='На продажу')
    theme = models.TextField(verbose_name="Тема")
    technique = models.CharField(verbose_name="Техника", max_length=50)
    tags = models.ManyToManyField("Tag", verbose_name="Тэги", blank=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True, null=True, verbose_name='Ссылка',
                            allow_unicode=True)
    year_created = models.SmallIntegerField(verbose_name="Год создания", null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.author}"

    class Meta:
        verbose_name = "Картина"
        verbose_name_plural = "Картины"

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(
                f"{self.name}-{self.author.email.split('@')[0]}-{str(time())}",
                allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url_edit(self):
        return reverse('market:lot-edit-view', kwargs={'slug': self.slug})

    def get_absolute_url(self):
        return reverse('market:lot-view', kwargs={'slug': self.slug})

    def muzzle(self):
        if self.images:
            return self.images.all()[0]

    def get_price(self):
        n = str(int(self.price))[::-1]
        return ' '.join(n[i:i + 3] for i in range(0, len(n), 3))[::-1]


class CustomerPicture(models.Model):
    """Связующая картины и пользователей модель"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    picture = models.ForeignKey(Picture, on_delete=models.CASCADE)
    time_created = models.DateField(auto_now_add=True, verbose_name="Время создания объявления")


def gen_image_filename(instance, filename):
    return '{0}/{1}'.format(instance.announcement.slug, filename)


class PictureImg(models.Model):
    image = models.ImageField(verbose_name="Изображение", upload_to=gen_image_filename, blank=True, null=True)
    announcement = models.ForeignKey(Picture, on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return self.image.name

    def delete(self, *args, **kwargs):
        storage, path = self.image.storage, self.image.path
        super(PictureImg, self).delete(*args, **kwargs)
        storage.delete(path)

    class Meta:
        verbose_name = "Фотография к картине"
        verbose_name_plural = "Фотографии к картине"


class Tag(models.Model):
    """Модель тэга картины"""
    name = models.CharField(max_length=150, verbose_name='Название')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "тэг"
        verbose_name_plural = "тэги"
        ordering = ['name']


class Review(models.Model):
    """Отзывы"""
    author = models.ForeignKey(Customer, verbose_name='Автор', on_delete=models.CASCADE, related_name="reviews")
    text = models.TextField("Сообщение", max_length=5000)
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )
    movie = models.ForeignKey(Picture, verbose_name="Картина", on_delete=models.CASCADE, related_name="reviews")
    likes = models.IntegerField(default=0, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.movie}"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"


class BuyerAlbum(models.Model):
    name = models.CharField(max_length=25, verbose_name='Название альбома', default="Пустой альбом")
    buyer = models.ForeignKey(Customer, verbose_name="Покупатель", on_delete=models.CASCADE, related_name="albums")
    pictures = models.ManyToManyField(Picture, verbose_name="Лоты", blank=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True, null=True, verbose_name='Ссылка')

    def __str__(self):
        return f'{self.slug}'

    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)
            self.slug = slugify(f"{self.buyer}-{self.id}")
        super().save(*args, **kwargs)

    def cover(self):
        count = self.pictures.all().count()
        if count != 0:
            return self.pictures.all()[count - 1].muzzle().image.url
        return "/static/img/blank_album.jpg"

    def get_absolute_url(self):
        return reverse('market:album-view', kwargs={'user_slug': self.buyer.slug, 'slug': self.slug})

    class Meta:
        verbose_name = "Альбом"
        verbose_name_plural = "Альбомы"


class BuyerCart(models.Model):
    buyer = models.OneToOneField(Customer, verbose_name="Покупатель", on_delete=models.CASCADE, related_name="cart")
    pictures = models.ManyToManyField(Picture, verbose_name="Лоты", blank=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True, null=True, verbose_name='Ссылка')

    def __str__(self):
        return f'{self.slug}'

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(f"cart-{self.buyer}-{self.buyer.id}")
        super(BuyerCart, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('market:cart-view', kwargs={'slug': self.slug})

    def get_sum(self):
        cart_sum = 0
        for picture in self.pictures.all():
            cart_sum += picture.price
        return cart_sum

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
