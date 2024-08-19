from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Course(models.Model):
    """Модель продукта - курса."""

    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='owns_courses',
        verbose_name='Автор курса',
    )
    title = models.CharField(
        max_length=250,
        verbose_name='Название курса',
    )
    start_date = models.DateTimeField(
        auto_now=False,
        auto_now_add=False,
        verbose_name='Дата и время начала курса'
    )
    price = models.PositiveIntegerField(
        verbose_name='Стоимость курса',
    )

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_course_title'
            )
        ]

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """Модель урока."""
    course = models.ForeignKey(
        to=Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Урок',
    )
    title = models.CharField(
        max_length=250,
        verbose_name='Название урока',
    )
    link = models.URLField(
        max_length=250,
        verbose_name='Ссылка',
    )

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'title'],
                name='unique_course_title_lesson'
            )
        ]

    def __str__(self):
        return self.title


class Group(models.Model):
    """Модель группы."""

    title = models.CharField(
        max_length=250,
        verbose_name='Название группы',
    )
    course = models.ForeignKey(
        to=Course,
        on_delete=models.CASCADE,
        related_name='groups',
        verbose_name='Курс',
    )
    students = models.ManyToManyField(
        to=User,
        related_name='in_groups',
        verbose_name='Студенты группы',
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'title'],
                name='unique_course_title'
            )
        ]
