from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from courses.models import Course, Group, Lesson
from users.models import Subscription

User = get_user_model()


class LessonSerializer(serializers.ModelSerializer):
    """Список уроков."""

    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Lesson
        fields = (
            'title',
            'link',
            'course'
        )


class CreateLessonSerializer(serializers.ModelSerializer):
    """Создание уроков."""

    class Meta:
        model = Lesson
        fields = (
            'title',
            'link',
            'course'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Lesson.objects.all(),
                fields=('title', 'course',),
                message='В данном курсе есть урок с таким же названием.'
            ),
        ]


class StudentSerializer(serializers.ModelSerializer):
    """Студенты курса."""

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
        )


class GroupSerializer(serializers.ModelSerializer):
    """Список групп."""
    
    class Meta:
        model = Group
        fields = (
            'id',     
            'title',     
            'course',     
            'students',     
        )


class CreateGroupSerializer(serializers.ModelSerializer):
    """Создание групп."""

    class Meta:
        model = Group
        fields = (
            'title',
            'course',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Group.objects.all(),
                fields=('title', 'course',),
                message='В данном курсе есть группа с таким же названием.'
            ),
        ]

    def validate(self, data):
        course = data.get('course')
        if course.groups.count() == 10:
            raise ValidationError(
                {
                    'errors': (
                        'Количество групп на курс достигло '
                        'максимального значения - 10.'
                    ),
                }
            )
        return data


class MiniLessonSerializer(serializers.ModelSerializer):
    """Список названий уроков для списка курсов."""

    class Meta:
        model = Lesson
        fields = (
            'title',
        )


class MiniGroupSerializer(serializers.ModelSerializer):
    """Список id групп в которых числится студент."""

    class Meta:
        model = Group
        fields = (
            'id',
            'course',
        )


class CourseSerializer(serializers.ModelSerializer):
    """Список курсов."""

    lessons = MiniLessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField(read_only=True)
    students_count = serializers.SerializerMethodField(read_only=True)
    groups_filled_percent = serializers.SerializerMethodField(read_only=True)
    demand_course_percent = serializers.SerializerMethodField(read_only=True)
    """
    Необходимо отобразить список всех продуктов на платформе, к каждому продукту приложить информацию:

    1 - Количество учеников занимающихся на продукте.
    2 - На сколько % заполнены группы? (среднее значение по количеству участников в группах 
        от максимального значения участников в группе, где максимальное = 30).
    3 - Процент приобретения продукта (рассчитывается исходя из количества полученных доступов к продукту 
        деленное на общее количество пользователей на платформе).
    """
    def get_lessons_count(self, obj):
        """Количество уроков в курсе."""
        return obj.lessons_count

    def get_students_count(self, obj):
        """Общее количество студентов на курсе."""
        return obj.students_count

    def get_groups_filled_percent(self, obj):
        """Процент заполнения групп, если в группе максимум 30 чел.."""
        # TODO Доп. задание

    def get_demand_course_percent(self, obj):
        """Процент приобретения курса."""
        # TODO Доп. задание

    class Meta:
        model = Course
        fields = (
            'id',
            'author',
            'title',
            'start_date',
            'price',
            'lessons_count',
            'lessons',
            'demand_course_percent',
            'students_count',
            'groups_filled_percent',
        )


class CreateCourseSerializer(serializers.ModelSerializer):
    """Создание курсов."""

    class Meta:
        model = Course
        fields = (
            'author',
            'title',
            'start_date',
            'price',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Course.objects.all(),
                fields=('title', 'author',),
                message='Данный курс уже существует.'
            ),
        ]
