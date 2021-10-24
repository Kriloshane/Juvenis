from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import F, ExpressionWrapper, FloatField, Sum


class Customer(AbstractUser):  # username, password, f_n, l_n, email
    """Модель пользователя"""
    name = models.CharField(verbose_name="Имя", max_length=20, null=True, blank=True)
    surname = models.CharField(verbose_name="Фамилия", max_length=40, null=True, blank=True)
    email = models.EmailField(verbose_name="Электронная почта", max_length=100, unique=True)
    pictures = models.ManyToManyField("Picture", verbose_name="Картины", through="CustomerPicture")

    def __str__(self):
        if self.name and self.surname:
            return f"{self.username}: {self.name} {self.surname} - {self.email}"
        return f"{self.username} - {self.email}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Picture(models.Model):
    """Модель картины"""
    class PictureGenre(models.TextChoices):
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
    author_list = models.ForeignKey("Customer", on_delete=models.CASCADE, verbose_name="Автор", db_index=True)
    price = models.FloatField(verbose_name="Цена", help_text="Цену указывать в рублях", db_index=True)
    dimensions = models.CharField(verbose_name="Размеры", help_text="например, 1x1 (в метрах)", max_length=30)
    description = models.TextField(verbose_name="Описание", null=True, blank=True)
    genre = models.CharField(verbose_name="Жанр", choices=PictureGenre.choices, max_length=3,
                             default=PictureGenre.is_absent, db_index=True)
    style = models.CharField(verbose_name="Стиль", choices=PictureStyle.choices, max_length=3,
                             default=PictureStyle.is_absent, db_index=True)
    category = models.CharField(verbose_name="Категория", choices=PictureCategory.choices, max_length=3,
                                default=PictureCategory.is_absent, db_index=True)
    theme = models.TextField(verbose_name="Тема")
    technique = models.CharField(verbose_name="Техника", max_length=50)
    tags = models.ManyToManyField("Tag", verbose_name="Тэги")

    def __str__(self):
        return f"{self.name}--{self.author}--{self.time_created}"

    class Meta:
        verbose_name = "Картина"
        verbose_name_plural = "Картины"


class CustomerPicture(models.Model):
    time_created = models.DateField(auto_now_add=True, verbose_name="Время создания объявления")


class Tag(models.Model):
    """Модель тэга картины"""
    name = models.CharField(max_length=150, verbose_name='Название')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "тэг"
        verbose_name_plural = "тэги"
        ordering = ['name']
