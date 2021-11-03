from django.db import models
from django.contrib.auth.models import AbstractUser
from django.shortcuts import reverse
from django.utils.text import slugify
from django.db.models import F, ExpressionWrapper, FloatField, Sum
from time import time
from googletrans import Translator


class Customer(AbstractUser):  # username, password, f_n, l_n, email
    """Модель пользователя"""
    name = models.CharField(verbose_name="Имя", max_length=20, null=True, blank=True)
    surname = models.CharField(verbose_name="Фамилия", max_length=40, null=True, blank=True)
    email = models.EmailField(verbose_name="Электронная почта", max_length=100, unique=True)
    #   pictures = models.ManyToManyField("Picture", verbose_name="Картины", through="CustomerPicture")
    followers = models.ManyToManyField("Customer", verbose_name='Подписчики', null=True, blank=True,
                                       related_name="follower_set")
    subscriptions = models.ManyToManyField("Customer", verbose_name='Подписки', null=True, blank=True)
    last_activity = models.DateTimeField(blank=True, null=True, verbose_name="Последняя активность")
    art_currency = models.IntegerField(default=0, verbose_name="Валюта")

    def __str__(self):
        if self.name and self.surname:
            return f"{self.surname} {self.name} "
        return f"{self.username} - {self.email}"

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
    theme = models.TextField(verbose_name="Тема")
    technique = models.CharField(verbose_name="Техника", max_length=50)
    tags = models.ManyToManyField("Tag", verbose_name="Тэги", null=True, blank=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True, null=True, verbose_name='Ссылка')
    year_created = models.SmallIntegerField(verbose_name="Год создания", null=True, blank=True)

    def __str__(self):
        return f"{self.name}--{self.author}"

    class Meta:
        verbose_name = "Картина"
        verbose_name_plural = "Картины"

    def save(self, *args, **kwargs):
        if not self.id:
            translator = Translator()

            self.slug = slugify(f"{translator.translate(self.name).text.replace(' ', '-')}--{self.author.email.split('@')[0]}-{str(time())}", allow_unicode=True)
        super().save(*args, **kwargs)
        print(self.slug)

    def get_absolute_url_edit(self):
        return reverse('market:announcement_edit_url', kwargs={'slug': self.slug})

    def get_absolute_url(self):
        return reverse('market:announcement_url', kwargs={'slug': self.slug})

    def get_price(self):
        return '{0:,}'.format(self.price).replace(',', ' ')


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


class Reviews(models.Model):
    """Отзывы"""
    email = models.EmailField()
    name = models.CharField("Имя", max_length=100)
    text = models.TextField("Сообщение", max_length=5000)
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )
    movie = models.ForeignKey(Picture, verbose_name="Картина", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.movie}"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
